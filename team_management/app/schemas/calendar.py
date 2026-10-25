from pydantic import BaseModel

from app.schemas.structural import MeetingsSchema, TaskSchema


class GetCalendarResponse(BaseModel):
    tasks: list[TaskSchema]
    meetings: list[MeetingsSchema]
