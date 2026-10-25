import enum
import typing
import uuid

from sqlalchemy import UUID, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.infrastructure.db.models.base import Base

if typing.TYPE_CHECKING:
    from app.core.infrastructure.db.models.meetings import Meetings
    from app.core.infrastructure.db.models.tasks import Tasks
    from app.core.infrastructure.db.models.users import Users


class TeamsRoles(enum.StrEnum):
    manager = 'manager'
    member = 'member'

    @property
    def access_level(self) -> int:
        """Assigns a numeric access level to each string role."""
        levels = {
            TeamsRoles.manager: 2,
            TeamsRoles.member: 1
        }
        return levels[self]

    def __ge__(self, other) -> bool:
        if not isinstance(other, TeamsRoles):
            return NotImplemented
        return self.access_level >= other.access_level

    def __gt__(self, other) -> bool:
        if not isinstance(other, TeamsRoles):
            return NotImplemented
        return self.access_level > other.access_level

    def __le__(self, other) -> bool:
        if not isinstance(other, TeamsRoles):
            return NotImplemented
        return self.access_level <= other.access_level

    def __lt__(self, other) -> bool:
        if not isinstance(other, TeamsRoles):
            return NotImplemented
        return self.access_level < other.access_level

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class Teams(Base):
    __tablename__ = 'teams'

    name: Mapped[str] = mapped_column(String(100),
                                      unique=True,
                                      nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000),
                                                    nullable=True)

    # ----- RELATIONSHIP -----
    membership: Mapped[list[TeamMembership]] = relationship(
        back_populates='team',
        init=False
        )
    tasks: Mapped[list[Tasks]] = relationship(
        back_populates='team',
        init=False
    )
    meetings: Mapped[list[Meetings]] = relationship(
        back_populates='team',
        init=False
    )

    def __repr__(self):
        return (f'team [id:{self.id}, name:{self.name}]')


class TeamMembership(Base, kw_only=True):
    __tablename__ = 'teams_membership'

    team_role: Mapped[TeamsRoles] = mapped_column(
        Enum(TeamsRoles, native_enum=True),
        default=TeamsRoles.member,
        nullable=False
        )

    # ------ ForeignKey ------
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        )
    team_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('teams.id', ondelete='CASCADE')
        )

    # ------ RELATIONSHIP ------
    member: Mapped[Users] = relationship(
        'Users',
        foreign_keys=[user_id],
        back_populates='membership',
        init=False
        )
    team: Mapped[Teams] = relationship(
        'Teams',
        foreign_keys=[team_id],
        back_populates='membership',
        init=False
        )

    __table_args__ = (
        UniqueConstraint("user_id", "team_id", name="uс_user_id_team_id"),
    )
