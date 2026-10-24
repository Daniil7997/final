from typing import Annotated
from fastapi import Depends, Path
from fastapi.security import (HTTPBearer,
                              HTTPAuthorizationCredentials)

from app.core.security import decode_token
from app.schemas.auth import (AccessTokensPayload)
from app.schemas.types import IdType, TeamsRoleType
from app.core.infrastructure.unit_of_work import UnitOfWork
from app.services.auth import AuthService
from app.core.infrastructure.db.models.teams import TeamsRoles
from app.dependencies.db import get_unit_of_work
from app.core.exceptions.auth import (ForbiddenError,
                                      InvalidTokenTypeError)
from app.domain.teams.exceptions import TeamMembershipRequiredError


auth_scheme = HTTPBearer()


def auth_service(
        unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)]
        ) -> AuthService:
    return AuthService(unit_of_work=unit_of_work)


def verify_access_token(
        token: Annotated[HTTPAuthorizationCredentials, Depends(auth_scheme)]
        ) -> AccessTokensPayload:
    payload = decode_token(token=token.credentials)
    if payload.token_type != 'access':
        raise InvalidTokenTypeError()
    return payload


def id_from_access_token(
        payload: Annotated[AccessTokensPayload, Depends(verify_access_token)]
        ) -> IdType:
    return payload.sub


async def team_role_from_db(
        team_id: Annotated[IdType, Path()],
        user_id: Annotated[IdType, Depends(id_from_access_token)],
        unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)]
) -> TeamsRoleType:
    async with unit_of_work as uow:
        role = await uow.teams.get_team_role(user_id=user_id, team_id=team_id)
        if role is None:
            raise TeamMembershipRequiredError()
        return role


def required_manager_or_higher(
        team_role: Annotated[TeamsRoleType, Depends(team_role_from_db)]
        ) -> TeamsRoleType:
    access_granted = team_role >= TeamsRoles.manager
    if not access_granted:
        raise ForbiddenError()
    return team_role


def required_member_or_higher(
        team_role: Annotated[TeamsRoleType, Depends(team_role_from_db)]
        ) -> TeamsRoleType:
    access_granted = team_role >= TeamsRoles.member
    if not access_granted:
        raise ForbiddenError()
    return team_role


async def required_admin(
        user_id: Annotated[IdType, Depends(id_from_access_token)],
        unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)]
) -> bool:
    async with unit_of_work as uow:
        is_admin: bool = await uow.users.check_is_admin(user_id=user_id)
        if not is_admin:
            raise ForbiddenError()
    return is_admin
