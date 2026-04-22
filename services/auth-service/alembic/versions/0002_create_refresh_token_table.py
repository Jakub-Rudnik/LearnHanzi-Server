"""create refresh token sessions table

Revision ID: 0002_create_refresh_token_table
Revises: 0001_create_users_table
Create Date: 2026-04-22 21:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_create_refresh_token_table"
down_revision: Union[str, None] = "0001_create_users_table"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "refresh_token_sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "token_hash",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "expires_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "user_agent",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "ip_address",
            sa.String(length=45),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_refresh_token_sessions_user_id",
        "refresh_token_sessions",
        ["user_id"],
    )
    op.create_index(
        "ix_refresh_token_sessions_token_hash",
        "refresh_token_sessions",
        ["token_hash"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_refresh_token_sessions_token_hash",
        table_name="refresh_token_sessions",
    )
    op.drop_index(
        "ix_refresh_token_sessions_user_id",
        table_name="refresh_token_sessions",
    )
    op.drop_table("refresh_token_sessions")