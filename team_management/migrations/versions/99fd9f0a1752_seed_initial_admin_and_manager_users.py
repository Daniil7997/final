"""seed initial admin and manager users

Revision ID: 99fd9f0a1752
Revises: 0ca11b08401b
Create Date: 2026-09-23 12:31:18.290748

"""
from typing import Sequence, Union
import datetime as dt
import uuid

from alembic import op
import sqlalchemy as sa

from app.core.security import hash_password
from app.models.users import UsersRoles


# revision identifiers, used by Alembic.
revision: str = '99fd9f0a1752'
down_revision: Union[str, Sequence[str], None] = '0ca11b08401b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


now = dt.datetime.now()
admin_password = hash_password("admin")
manager_password = hash_password("manager")


def upgrade():
    users_table = sa.table(
        "users",
        sa.column("id", sa.UUID),
        sa.column("name", sa.String),
        sa.column("email", sa.String),
        sa.column("password", sa.String),
        sa.column("user_role", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime)
    )

    op.bulk_insert(
        users_table,
        [
            {
                "id": uuid.uuid7(),
                "name": "Admin",
                "email": "admin@example.com",
                "password": admin_password,
                "user_role": UsersRoles.admin,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": uuid.uuid7(),
                "name": "Manager",
                "email": "manager@example.com",
                "password": manager_password,
                "user_role": UsersRoles.manager,
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
        ],
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
