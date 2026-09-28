import enum
import typing

from sqlalchemy.orm import (Mapped,
                            mapped_column,
                            relationship)
from sqlalchemy import (Enum,
                        String)

from app.models.base import Base


if typing.TYPE_CHECKING:
    from app.models.teams import TeamMembership
    from app.models.meetings import Meetings
    from app.models.tasks import Tasks, TasksComments
    from app.models.evaluations import Evaluations


class UsersRoles(enum.StrEnum):
    admin = 'admin'
    manager = 'manager'
    member = 'member'

    @property
    def access_level(self) -> int:
        """Assigns a numeric access level to each string role."""
        levels = {
            UsersRoles.admin: 3,
            UsersRoles.manager: 2,
            UsersRoles.member: 1
        }
        return levels[self]

    def __ge__(self, other) -> bool:
        if not isinstance(other, UsersRoles):
            return NotImplemented
        return self.access_level >= other.access_level

    def __gt__(self, other) -> bool:
        if not isinstance(other, UsersRoles):
            return NotImplemented
        return self.access_level > other.access_level

    def __le__(self, other) -> bool:
        if not isinstance(other, UsersRoles):
            return NotImplemented
        return self.access_level <= other.access_level

    def __lt__(self, other) -> bool:
        if not isinstance(other, UsersRoles):
            return NotImplemented
        return self.access_level < other.access_level

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class Users(Base):
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String(50),
                                      nullable=False)
    email: Mapped[str] = mapped_column(String(50),
                                       unique=True,
                                       nullable=False)
    password: Mapped[str] = mapped_column(String(255),
                                          nullable=False)

    is_active: Mapped[bool] = mapped_column(default=True,
                                            nullable=False,
                                            init=False)
    user_role: Mapped[UsersRoles] = mapped_column(
        Enum(UsersRoles, native_enum=False),
        default=UsersRoles.member,
        nullable=False
        )

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
