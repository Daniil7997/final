import datetime as dt

from pydantic import BaseModel, ConfigDict

from app.schemas.types import (
    EmailType,
    IdType,
    TaskDescriptionType,
    TaskStatusType,
    TeamDescriptionType,
    TeamNameType,
    TeamsRoleType,
    UserNameType,
)


class BaseSchema(BaseModel):
    id: IdType
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = ConfigDict(from_attributes=True)


class UsersSchema(BaseSchema):
    name: UserNameType
    email: EmailType
    password: str
    is_active: bool


class TeamsSchema(BaseSchema):
    name: TeamNameType
    description: TeamDescriptionType


class TaskSchema(BaseSchema):
    description: TaskDescriptionType
    due_date: dt.date
    status: TaskStatusType
    verification_url: str | None
    creator_id: IdType
    assignee_id: IdType | None


class TeamMembershipSchema(BaseModel):
    id: IdType
    name: str
    email: str
    team_role: TeamsRoleType

    model_config = ConfigDict(from_attributes=True)


class UserEmailPassword(BaseModel):
    password: str
    email: EmailType


class MeetingsSchema(BaseSchema):
    description: str
    start_meeting: dt.datetime
    end_meeting: dt.datetime
    team_id: IdType
