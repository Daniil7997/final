from sqlalchemy.exc import IntegrityError

from app.services.base import BaseService
from app.schemas.teams import (CreateInviteResponse,
                               JoinTeamRequest,
                               GetMembershipResponse)
from app.schemas.types import IdType
from app.schemas.structural import TeamsSchema
from app.core.infrastructure.storage.invite import invite_storage
from app.core.utils import generate_invite_code
from app.core.config import settings
from app.domain.teams.exceptions import (TeamNotFoundError,
                                         InviteNotFoundError,
                                         TeamMembershipRequiredError,
                                         TeamMemberNotFoundError)


class TeamsService(BaseService):

    async def create_invite(self,
                            user_id: IdType,
                            team_id: IdType) -> CreateInviteResponse:
        async with self.unit_of_work as uow:
            repo = uow.teams
            user_in_team = await repo.check_user_in_team(user_id=user_id,
                                                         team_id=team_id)
            if user_in_team is None:
                raise TeamNotFoundError()
        invite_code = generate_invite_code()
        await invite_storage.set(key=str(invite_code),
                                 value=str(team_id))
        return CreateInviteResponse(
            invite_code=invite_code,
            invite_code_ttl=settings.app.invite_code_ttl
            )

    async def join_team(self,
                        data: JoinTeamRequest,
                        user_id: IdType) -> IdType:
        team_id = await invite_storage.get(key=str(data.invite_code))
        if team_id is None:
            raise InviteNotFoundError()
        async with self.unit_of_work as uow:
            repo = uow.teams
            await repo.join_team(user_id=user_id, team_id=team_id)
        return IdType(team_id)

    async def get_team_membership(
            self,
            team_id: IdType,
            actor_id: IdType
            ) -> list[GetMembershipResponse]:
        async with self.unit_of_work as uow:
            repo = uow.teams
            check = await repo.check_user_in_team(user_id=actor_id,
                                                  team_id=team_id)
            if not check:
                raise TeamMembershipRequiredError()
            list_users = await repo.get_team_membership_by_team_id(
                team_id=team_id,
                actor_id=actor_id
                )
            users = [
                GetMembershipResponse.model_validate(user.model_dump())
                for user in list_users
                ]
            return users

    async def remove_team_member(self,
                                 team_id: IdType,
                                 member_id: IdType,
                                 actor_id: IdType) -> IdType:
        async with self.unit_of_work as uow:
            repo = uow.teams
            removed_member_id = await repo.remove_team_member(
                member_id=member_id,
                actor_id=actor_id,
                team_id=team_id
                )
            if removed_member_id is None:
                raise TeamMemberNotFoundError()
            return removed_member_id
