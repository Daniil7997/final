import datetime as dt

from pydantic import BaseModel

from app.schemas.types import (IdType,
                               MeetingsDescriptionType)


# ======================================================
# REQUEST / RESPONSE (API CONTRACT)
# ======================================================
class CreateMeetingRequest(BaseModel):
    description: MeetingsDescriptionType
    start_meeting: dt.datetime
    end_meeting: dt.datetime
    user_id: list[IdType] | IdType | None = None


class CreateMeetingsResponse(BaseModel):
    meeting_id: IdType


class AddUserToMeetingRequest(BaseModel):
    user_id: list[IdType] | IdType


class GetTeamMeetingsResponse(BaseModel):
    id: IdType
    description: str
    start_meeting: dt.datetime
    end_meeting: dt.datetime
