import typing
import uuid
from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.infrastructure.db.models.base import Base

if typing.TYPE_CHECKING:
    from app.core.infrastructure.db.models.teams import Teams
    from app.core.infrastructure.db.models.users import Users


class MeetingsParticipants(Base):
    __tablename__ = 'meetings_participants'

    # ------ ForeignKey ------
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        index=True
        )
    meeting_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('meetings.id', ondelete='CASCADE'),
        index=True
        )

    __table_args__ = (
        UniqueConstraint('user_id', 'meeting_id', name='uq_user_meeting'),
    )


class Meetings(Base, kw_only=True):
    __tablename__ = 'meetings'

    description: Mapped[str | None] = mapped_column(String(500),
                                                    nullable=True,
                                                    default=None)

    start_meeting: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                    index=True)
    end_meeting: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                  index=True)

    # ----- FOREIGNKEY -----
    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey('teams.id', ondelete='CASCADE'),
        index=True
    )

    # ----- RELATIONSHIP -----
    users: Mapped[list[Users]] = relationship(
        secondary=MeetingsParticipants.__table__,
        back_populates='meetings',
        init=False
    )
    team: Mapped[Teams] = relationship(
        back_populates='meetings',
        init=False
    )

    __table_args__ = (
        CheckConstraint("end_meeting > start_meeting",
                        name="valid_time_range_meetings"),
    )
