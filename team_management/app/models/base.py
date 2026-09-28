import uuid
from datetime import datetime

from sqlalchemy.orm import (MappedAsDataclass,
                            DeclarativeBase)

from sqlalchemy.orm import (Mapped,
                            mapped_column)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import (func)


class Base(MappedAsDataclass, DeclarativeBase, kw_only=True):

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        insert_default=uuid.uuid7,
        init=False,
        sort_order=-100
    )
    created_at: Mapped[datetime] = mapped_column(default=func.now(),
                                                 sort_order=100)
    updated_at: Mapped[datetime] = mapped_column(default=func.now(),
                                                 onupdate=func.now(),
                                                 sort_order=101)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(id={self.id})>"
