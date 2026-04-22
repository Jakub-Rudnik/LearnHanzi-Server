"""create users table

Revision ID: 0001_create_users_table
Revises:
Create Date: 2026-04-22 19:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0001_create_users_table"
down_revision: Union[str, None] = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "username",
            sa.String(length=50),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.Enum("USER", "ADMIN", name="user_role"),
            nullable=False,
            server_default="USER",
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "last_login_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("users")
    sa.Enum("USER", "ADMIN", name="user_role").drop(
        op.get_bind(),
        checkfirst=True,
    )