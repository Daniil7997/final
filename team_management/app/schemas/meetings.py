import datetime as dt
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.schemas.types import IdType, MeetingsDescriptionType


# ======================================================
# REQUEST / RESPONSE (API CONTRACT)
# ======================================================
class CreateMeetingRequest(BaseModel):
    description: MeetingsDescriptionType
    start_meeting: dt.datetime
    end_meeting: dt.datetime
    users_id: Annotated[
        list[IdType] | None,
        Field(max_length=30,
              default=None,
              description='List of participants in the meetings.')
        ]

    @field_validator('users_id', mode='before')
    @classmethod
    def remove_duplicates(cls, v: list):
        if isinstance(v, list):
            return list(set(v))
        return v


class CreateMeetingsResponse(BaseModel):
    meeting_id: IdType



class AddUserToMeetingRequest(BaseModel):
    users_id: Annotated[
        list[IdType],
        Field(max_length=30,
              description='List of participants in the meetings.')
        ]

    @field_validator('users_id', mode='before')
    @classmethod
    def remove_duplicates(cls, v: list):
        if isinstance(v, list):
            return list(set(v))
        return v


class GetTeamMeetingsResponse(BaseModel):
    id: IdType
    description: str
    start_meeting: dt.datetime
    end_meeting: dt.datetime
