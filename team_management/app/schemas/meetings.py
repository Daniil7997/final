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


class CreateMeetingsResponse(BaseModel):
    meeting_id: IdType


class AddUserToMeetingRequest(BaseModel):
    user_id: IdType


class GetTeamMeetingsResponse(BaseModel):
    id: IdType
    description: str
    start_meeting: dt.datetime
    end_meeting: dt.datetime
