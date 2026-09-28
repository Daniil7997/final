from pydantic import BaseModel

from app.schemas.types import (UserNameType,
                               EmailType,
                               UserRoleType)


# ======================================================
# REQUEST / RESPONSE (API CONTRACT)
# ======================================================
class GetProfileResponse(BaseModel):
    name: UserNameType
    email: EmailType
    user_role: UserRoleType
