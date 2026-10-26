import typing
import uuid
from datetime import date
from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.infrastructure.db.models.base import Base

if typing.TYPE_CHECKING:
    from app.core.infrastructure.db.models.evaluations import Evaluations
    from app.core.infrastructure.db.models.teams import Teams
    from app.core.infrastructure.db.models.users import Users


class TaskStatus(StrEnum):
    open = 'open'
    in_progress = 'in_progress'
    done = 'done'


class Tasks(Base, kw_only=True):
    __tablename__ = 'tasks'

    description: Mapped[str] = mapped_column(String(2000))
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus, native_enum=True),
        default=TaskStatus.open,
        nullable=False
        )
    due_date: Mapped[date] = mapped_column(nullable=False, index=True)
    verification_url: Mapped[str | None] = mapped_column(String(500),
                                                         default=None,
                                                         init=False)
    # ------ ForeignKey ------
    creator_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
    )
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        default=None,
        index=True
    )
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('teams.id', ondelete='CASCADE'),
        index=True
    )

    # ------ RELATIONSHIP ------
    # Users
    creator: Mapped[Users] = relationship(
        back_populates='created_tasks',
        foreign_keys=[creator_id],
        init=False
        )
    assignee: Mapped[Users | None] = relationship(
        back_populates='assigned_tasks',
        foreign_keys=[assignee_id],
        init=False
        )
    # TasksComments
    comments: Mapped[list[TasksComments]] = relationship(
        back_populates='task',
        init=False
        )
    team: Mapped[Teams] = relationship(
        foreign_keys=[team_id],
        back_populates='tasks',
        init=False
    )
    # Evaluations
    evaluations: Mapped[Evaluations] = relationship(
        back_populates='tasks',
        init=False
    )


class TasksComments(Base, kw_only=True):
    __tablename__ = 'tasks_comments'

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('tasks.id', ondelete='CASCADE'),
        index=True
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        index=True
    )
    comment: Mapped[str] = mapped_column(String(2000))

    # ------ RELATIONSHIP ------
    # Tasks
    task: Mapped[Tasks] = relationship(
        back_populates='comments',
        foreign_keys=[task_id],
        init=False
        )
    # Users
    author: Mapped[Users] = relationship(
        back_populates='tasks_comments',
        foreign_keys=[author_id],
        init=False
        )
