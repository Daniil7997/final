from app.services.base import BaseService
from app.schemas.teams import (CreateInviteResponse,
                               JoinTeamRequest,
                               GetMembershipResponse)
from app.schemas.types import IdType, TeamsRoleType
from app.core.infrastructure.storage.invite import invite_storage
from app.core.utils import generate_invite_code
from app.core.config import settings
from app.domain.teams.exceptions import (InviteNotFoundError,
                                         TeamMemberNotFoundError,
                                         LowActorRolePrivilegeError)


class TeamsService(BaseService):

    async def create_invite(self, team_id: IdType) -> CreateInviteResponse:
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
            await uow.teams.join_team(user_id=user_id, team_id=team_id)
        return IdType(team_id)

    async def get_team_membership(
            self,
            team_id: IdType,
            ) -> list[GetMembershipResponse]:
        async with self.unit_of_work as uow:
            list_users = await uow.teams.get_team_membership_by_team_id(
                team_id=team_id,
                )
            users = [
                GetMembershipResponse.model_validate(user.model_dump())
                for user in list_users
                ]
            return users

    async def remove_team_member(
            self,
            team_id: IdType,
            member_id: IdType,
            actor_role: TeamsRoleType
            ) -> IdType:
        async with self.unit_of_work as uow:
            user_role = await uow.teams.get_team_role(
                user_id=member_id,
                team_id=team_id
            )
            if actor_role <= user_role:
                raise LowActorRolePrivilegeError()
            deleted_id = await uow.teams.remove_team_member(
                member_id=member_id,
                team_id=team_id
                )
            if deleted_id is None:
                raise TeamMemberNotFoundError()
            return deleted_id
