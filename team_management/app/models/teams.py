import typing
import uuid

from sqlalchemy.orm import (Mapped,
                            mapped_column,
                            relationship)
from sqlalchemy import UUID, ForeignKey, String, UniqueConstraint

from app.models.base import Base


if typing.TYPE_CHECKING:
    from app.models.users import Users
    from app.models.tasks import Tasks
    from app.models.meetings import Meetings


class Teams(Base):
    __tablename__ = 'teams'

    name: Mapped[str] = mapped_column(String(100),
                                      unique=True,
                                      nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000),
                                                    nullable=True)

    # ----- RELATIONSHIP -----
    membership: Mapped[list['TeamMembership']] = relationship(
        back_populates='team',
        init=False
        )
    tasks: Mapped[list['Tasks']] = relationship(
        back_populates='team',
        init=False
    )
    meetings: Mapped[list['Meetings']] = relationship(
        back_populates='team',
        init=False
    )

    def __repr__(self):
        return (f'team [id:{self.id}, name:{self.name}]')


class TeamMembership(Base, kw_only=True):
    __tablename__ = 'teams_membership'

    team_role: Mapped[str | None] = mapped_column(String(100),
                                                  default='intern')

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
