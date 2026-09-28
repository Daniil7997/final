from pydantic import BaseModel

from app.schemas.types import (IdType,
                               UserRoleType,
                               TeamNameType,
                               TeamDescriptionType)


# ======================================================
# REQUEST / RESPONSE (API CONTRACT)
# ======================================================
class CreateTeamRequest(BaseModel):
    name: TeamNameType
    description: TeamDescriptionType


class CreateTeamResponse(BaseModel):
    id: IdType
    name: TeamNameType
    description: TeamDescriptionType


class CreateInviteResponse(BaseModel):
    invite_code: str
    invite_code_ttl: int


class JoinTeamRequest(BaseModel):
    invite_code: str


class GetMembershipResponse(BaseModel):
    name: str
    email: str
    user_role: UserRoleType
    team_role: str


class ChangeTeamMemberRole(BaseModel):
    new_role: str
