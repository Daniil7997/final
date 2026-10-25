import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
)


class Base(MappedAsDataclass, DeclarativeBase, kw_only=True):

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        insert_default=uuid.uuid7,
        init=False,
        sort_order=-100
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        insert_default=lambda: datetime.now(UTC),
        default_factory=lambda: datetime.now(UTC),
        sort_order=100
        )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        insert_default=lambda: datetime.now(UTC),
        default_factory=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        sort_order=101
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
