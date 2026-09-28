import datetime as dt

from pydantic import BaseModel

from app.schemas.types import (IdType,
                               TaskDescriptionType,
                               TaskStatusType)


# ======================================================
# REQUEST / RESPONSE (API CONTRACT)
# ======================================================
class CreateTaskRequest(BaseModel):
    description: TaskDescriptionType
    due_date: dt.date


class UpdateTaskRequest(BaseModel):
    description: TaskDescriptionType
    due_date: dt.date


class UpdateTaskResponse(BaseModel):
    id: IdType
    creator_id: IdType
    description: TaskDescriptionType
    status: str
    due_date: dt.date
    assignee_id: IdType | None


class GetTaskResponse(BaseModel):
    id: IdType
    creator_id: IdType
    description: TaskDescriptionType
    status: str
    due_date: dt.date
    assignee_id: IdType | None


class ChangeTaskStatusRequest(BaseModel):
    new_status: TaskStatusType


class ChangeTaskStatusResponse(BaseModel):
    id: IdType
    creator_id: IdType
    description: TaskDescriptionType
    status: str
    due_date: dt.date
    assignee_id: IdType | None


class CreateTaskCommentRequest(BaseModel):
    comment_text: str
