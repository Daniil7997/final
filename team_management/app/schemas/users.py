from pydantic import BaseModel

from app.schemas.types import EmailType, UserNameType


# ======================================================
# REQUEST / RESPONSE (API CONTRACT)
# ======================================================
class GetProfileResponse(BaseModel):
    name: UserNameType
    email: EmailType
