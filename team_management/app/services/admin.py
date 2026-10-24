from sqlalchemy.exc import IntegrityError

from app.services.base import BaseService
from app.schemas.admin import CreateTeamRequest, CreateTeamResponse
from app.schemas.types import IdType, TeamsRoleType
from app.schemas.structural import TeamsSchema
from app.core.infrastructure.storage.invite import invite_storage
from app.core.infrastructure.db.codes import DBIntegrityState
from app.core.utils import generate_invite_code
from app.core.config import settings
from app.domain.teams.exceptions import (TeamMemberNotFoundError,
                                         TeamNameAlreadyExistError)
from app.domain.users.exceptions import UserNotFoundError


class AdminService(BaseService):

    async def create_team(self, data: CreateTeamRequest) -> CreateTeamResponse:
        async with self.unit_of_work as uow:
            repo = uow.teams
            try:
                team: TeamsSchema = await repo.create_team(
                    name=data.name,
                    description=data.description,
                    manager_id=data.manager_id
                    )
                return CreateTeamResponse.model_validate(team.model_dump())
            except IntegrityError as e:
                sqlstate = getattr(e.orig, "sqlstate", None)
                
                if sqlstate == DBIntegrityState.FOREIGN_KEY_VIOLATION:
                    raise UserNotFoundError()
                    
                elif sqlstate == DBIntegrityState.UNIQUE_VIOLATION:
                    raise TeamNameAlreadyExistError()

                else: raise e

    async def change_team_member_role(self,
                                      team_id: IdType,
                                      member_id: IdType,
                                      new_role: TeamsRoleType) -> None:
        async with self.unit_of_work as uow:
            repo = uow.teams
            updated_id = await repo.change_team_member_role(
                team_id=team_id,
                member_id=member_id,
                new_role=new_role
                )
            if updated_id is None:
                raise TeamMemberNotFoundError()
