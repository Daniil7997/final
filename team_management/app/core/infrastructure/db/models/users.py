import typing

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.infrastructure.db.models.base import Base

if typing.TYPE_CHECKING:
    from app.core.infrastructure.db.models.evaluations import Evaluations
    from app.core.infrastructure.db.models.meetings import Meetings
    from app.core.infrastructure.db.models.tasks import Tasks, TasksComments
    from app.core.infrastructure.db.models.teams import TeamMembership


class Users(Base):
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String(50),
                                      nullable=False)
    email: Mapped[str] = mapped_column(String(50),
                                       unique=True,
                                       nullable=False)
    password: Mapped[str] = mapped_column(String(255),
                                          nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False,
                                           nullable=False,
                                           init=True)
    is_active: Mapped[bool] = mapped_column(default=True,
                                            nullable=False,
                                            init=False)

    # ------ RELATIONSHIP ------
    # Teams
    membership: Mapped[TeamMembership | None] = relationship(
        'TeamMembership',
        back_populates='member',
        init=False,
        default=None
        )
    # Meetings
    meetings: Mapped[list[Meetings]] = relationship(
        secondary='meetings_participants',
        back_populates='users',
        init=False,
        default_factory=list
    )
    # Tasks
    created_tasks: Mapped[list[Tasks]] = relationship(
        foreign_keys='[Tasks.creator_id]',
        back_populates='creator',
        init=False,
        default_factory=list
        )
    assigned_tasks: Mapped[list[Tasks]] = relationship(
        foreign_keys='[Tasks.assignee_id]',
        back_populates='assignee',
        init=False,
        default_factory=list
        )
    # TasksComments
    tasks_comments: Mapped[list[TasksComments]] = relationship(
        back_populates='author',
        init=False,
        default_factory=list
        )
    # Evaluations
    grades_given: Mapped[list[Evaluations]] = relationship(
        back_populates='grader',
        init=False,
        default_factory=list,
        foreign_keys='[Evaluations.grader_id]'
    )
    grades_recieved: Mapped[list[Evaluations]] = relationship(
        back_populates='author',
        init=False,
        default_factory=list,
        foreign_keys='[Evaluations.author_id]'
    )

    def __repr__(self):
        return (f'users_obj [id:{self.id}, is_active:{self.is_active}]')
