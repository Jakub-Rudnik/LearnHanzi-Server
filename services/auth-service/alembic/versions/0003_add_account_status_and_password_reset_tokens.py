"""add account status and password reset tokens

Revision ID: 0003_account_status_reset_tokens
Revises: 0002_create_refresh_token_table
Create Date: 2026-05-25 19:00:00.000000
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_account_status_reset_tokens"
down_revision: Union[str, None] = "0002_create_refresh_token_table"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


account_status_enum = sa.Enum(
    "ACTIVE",
    "BANNED",
    "SUSPENDED",
    name="account_status",
)


def upgrade() -> None:
    account_status_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "account_status",
            account_status_enum,
            nullable=False,
            server_default="ACTIVE",
        ),
    )

    op.execute(
        """
        UPDATE users
        SET account_status = CASE
            WHEN is_active = true THEN 'ACTIVE'::account_status
            ELSE 'SUSPENDED'::account_status
        END
        """
    )

    op.create_table(
        "password_reset_tokens",
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
            "used_at",
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
            "requested_ip",
            sa.String(length=45),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_password_reset_tokens_user_id",
        "password_reset_tokens",
        ["user_id"],
    )
    op.create_index(
        "ix_password_reset_tokens_token_hash",
        "password_reset_tokens",
        ["token_hash"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_password_reset_tokens_token_hash",
        table_name="password_reset_tokens",
    )
    op.drop_index(
        "ix_password_reset_tokens_user_id",
        table_name="password_reset_tokens",
    )
    op.drop_table("password_reset_tokens")

    op.drop_column("users", "account_status")
    account_status_enum.drop(op.get_bind(), checkfirst=True)

