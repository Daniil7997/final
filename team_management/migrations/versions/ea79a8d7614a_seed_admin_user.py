"""seed_admin_user

Revision ID: ea79a8d7614a
Revises: 4a3ee906c3af
Create Date: 2026-10-23 21:25:12.610889

"""
import datetime as dt
import uuid
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.core.config import settings

# revision identifiers, used by Alembic.
revision: str = 'ea79a8d7614a'
down_revision: str | Sequence[str] | None = '4a3ee906c3af'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


now = dt.datetime.now(dt.UTC)


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
