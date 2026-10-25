import uuid
from typing import Annotated

from pydantic import EmailStr, Field

from app.core.infrastructure.db.models.tasks import TaskStatus
from app.core.infrastructure.db.models.teams import TeamsRoles

IdType = uuid.UUID

# USERS
UserNameType = Annotated[str, Field(max_length=50)]
PasswordType = Annotated[str, Field(max_length=30)]
EmailType = Annotated[EmailStr, Field(max_length=50)]

# TEAMS
TeamNameType = Annotated[str, Field(max_length=100)]
TeamDescriptionType = Annotated[str | None, Field(max_length=1000)]
TeamsRoleType = TeamsRoles

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
