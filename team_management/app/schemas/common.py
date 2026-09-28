from pydantic import BaseModel


# ======================================================
# REQUEST / RESPONSE (API CONTRACT)
# ======================================================
class SuccessMessageResponse(BaseModel):
    msg: str
