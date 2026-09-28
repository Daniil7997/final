from typing import Annotated, Optional
import uuid

from pydantic import Field, EmailStr
from app.models.users import UsersRoles
from app.models.tasks import TaskStatus


IdType = uuid.UUID

# USERS
UserNameType = Annotated[str, Field(max_length=50)]
PasswordType = Annotated[str, Field(max_length=30)]
EmailType = Annotated[EmailStr, Field(max_length=50)]
UserRoleType = UsersRoles

# TEAMS
TeamNameType = Annotated[str, Field(max_length=100)]
TeamDescriptionType = Annotated[Optional[str], Field(max_length=1000)]

# TASKS
TaskDescriptionType = Annotated[str, Field(max_length=5000)]
TaskStatusType = TaskStatus
TaskCommentTextType = Annotated[str, Field(max_length=2000)]

# EVALUATIONS
EvaluationsCommentType = Annotated[str | None, Field(max_length=2000,
                                                     default=None)]
EvaluationsGradeType = Annotated[int, Field(ge=1, le=5)]

# MEETINGS
MeetingsDescriptionType = Annotated[str, Field(max_length=500)]
