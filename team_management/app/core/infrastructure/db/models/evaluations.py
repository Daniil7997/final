import uuid
import typing

from sqlalchemy.orm import (Mapped,
                            mapped_column,
                            relationship)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (ForeignKey,
                        String)

from app.core.infrastructure.db.models.base import Base
from app.core.infrastructure.db.models.constraints import range_1_to_5


if typing.TYPE_CHECKING:
    from app.core.infrastructure.db.models.users import Users
    from app.core.infrastructure.db.models.tasks import Tasks


class Evaluations(Base, kw_only=True):
    __tablename__ = 'evaluations'

    grade: Mapped[int] = mapped_column(
        range_1_to_5(table_name='evaluations', column_name='grade')
    )
    comment: Mapped[str | None] = mapped_column(String(2000),
                                                nullable=True,
                                                default=None)
    # ------ ForeignKey ------
    grader_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE')
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE')
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('tasks.id', ondelete='CASCADE')
    )
    # ------ RELATIONSHIP ------
    # Users
    grader: Mapped['Users'] = relationship(
        back_populates='grades_given',
        foreign_keys=[grader_id],
        init=False
    )
    author: Mapped['Users'] = relationship(
        back_populates='grades_recieved',
        foreign_keys=[author_id],
        init=False
    )
    tasks: Mapped['Tasks'] = relationship(
        back_populates='evaluations',
        foreign_keys=[task_id],
        init=False
    )
