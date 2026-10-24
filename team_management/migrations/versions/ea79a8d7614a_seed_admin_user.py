"""seed_admin_user

Revision ID: ea79a8d7614a
Revises: 4a3ee906c3af
Create Date: 2026-10-23 21:25:12.610889

"""
from typing import Sequence, Union
import uuid
import datetime as dt

from alembic import op
import sqlalchemy as sa

from app.core.config import settings


# revision identifiers, used by Alembic.
revision: str = 'ea79a8d7614a'
down_revision: Union[str, Sequence[str], None] = '4a3ee906c3af'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


now = dt.datetime.now(dt.timezone.utc)


def upgrade():
    users_table = sa.table(
        "users",
        sa.column('id', sa.UUID),
        sa.column('name', sa.String),
        sa.column('email', sa.String),
        sa.column('password', sa.String),
        sa.column('is_admin', sa.Boolean),
        sa.column('is_active', sa.Boolean),
        sa.column('created_at', sa.DateTime(timezone=True)),
        sa.column('updated_at', sa.DateTime(timezone=True)),
    )


    op.bulk_insert(
        users_table,
        [
            {
                "id": uuid.uuid7(),
                "name": "Admin",
                "email": "admin@example.com",
                "password": settings.app.hashed_admin_password,
                "is_admin": True,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
