from typing import Annotated
from fastapi import Depends
from fastapi.security import (HTTPBearer,
                              HTTPAuthorizationCredentials)

from app.core.security import decode_token
from app.schemas.auth import (AccessTokensPayload)
from app.schemas.types import IdType, UserRoleType
from app.core.infrastructure.unit_of_work import UnitOfWork
from app.services.auth import AuthService
from app.models.users import UsersRoles
from app.dependencies.db import get_unit_of_work
from app.core.exceptions.auth import (ForbiddenError,
                                      InvalidTokenTypeError)


auth_scheme = HTTPBearer()


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


def get_user_role_from_access_token(
        payload: Annotated[AccessTokensPayload, Depends(verify_access_token)]
) -> UserRoleType:
    return UserRoleType(payload.user_role)


def required_manager_or_higher(
        user_role: Annotated[UserRoleType,
                             Depends(get_user_role_from_access_token)]
        ) -> UserRoleType:
    access_granted = user_role >= UsersRoles.manager
    if not access_granted:
        raise ForbiddenError()
    return user_role


def auth_service(
        unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)]
        ) -> AuthService:
    return AuthService(unit_of_work=unit_of_work)
