from pydantic import BaseModel, Field

from app.schemas.types import (
    IdType,
    TeamDescriptionType,
    TeamNameType,
    TeamsRoleType,
)


# ======================================================
# REQUEST / RESPONSE (API CONTRACT)
# ======================================================
class CreateTeamRequest(BaseModel):
    name: TeamNameType
    description: TeamDescriptionType
    manager_id: IdType = Field(
        description='Assign the user with ID <manager_id> as the team manager'
        )


class CreateTeamResponse(BaseModel):
    id: IdType
    name: TeamNameType
    description: TeamDescriptionType


class ChangeTeamMemberRole(BaseModel):
    new_role: TeamsRoleType
