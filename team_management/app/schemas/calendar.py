from pydantic import BaseModel

from app.schemas.structural import TaskSchema, MeetingsSchema


class GetCalendarResponse(BaseModel):
    tasks: list[TaskSchema]
    meetings: list[MeetingsSchema]
