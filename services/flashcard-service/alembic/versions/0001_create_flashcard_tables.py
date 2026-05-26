"""create flashcard tables

Revision ID: 0001_create_flashcard_tables
Revises: 
Create Date: 2026-05-26 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "0001_create_flashcard_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "flashcard_sets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_flashcard_sets_user_id",
        "flashcard_sets",
        ["user_id"],
    )

    op.create_table(
        "flashcard_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "set_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("flashcard_sets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("hanzi_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("set_id", "position", name="uq_flashcard_items_set_position"),
        sa.UniqueConstraint("set_id", "hanzi_id", name="uq_flashcard_items_set_hanzi"),
    )
    op.create_index("ix_flashcard_items_set_id", "flashcard_items", ["set_id"])
    op.create_index("ix_flashcard_items_hanzi_id", "flashcard_items", ["hanzi_id"])

    op.create_table(
        "user_flashcard_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hanzi_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_favorite", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_difficult", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", "hanzi_id", name="uq_user_flashcard_state_user_hanzi"),
    )
    op.create_index(
        "ix_user_flashcard_states_user_id",
        "user_flashcard_states",
        ["user_id"],
    )
    op.create_index(
        "ix_user_flashcard_states_hanzi_id",
        "user_flashcard_states",
        ["hanzi_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_user_flashcard_states_hanzi_id", table_name="user_flashcard_states")
    op.drop_index("ix_user_flashcard_states_user_id", table_name="user_flashcard_states")
    op.drop_table("user_flashcard_states")

    op.drop_index("ix_flashcard_items_hanzi_id", table_name="flashcard_items")
    op.drop_index("ix_flashcard_items_set_id", table_name="flashcard_items")
    op.drop_table("flashcard_items")

    op.drop_index("ix_flashcard_sets_user_id", table_name="flashcard_sets")
    op.drop_table("flashcard_sets")


