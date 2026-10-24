from pydantic import BaseModel

from app.schemas.types import TeamsRoleType


# ======================================================
# REQUEST / RESPONSE (API CONTRACT)
# ======================================================
class CreateInviteResponse(BaseModel):
    invite_code: str
    invite_code_ttl: int


class JoinTeamRequest(BaseModel):
    invite_code: str


class GetMembershipResponse(BaseModel):
    name: str
    email: str
    team_role: TeamsRoleType
