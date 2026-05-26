from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class UserFlashcardState(Base):
    __tablename__ = "user_flashcard_states"
    __table_args__ = (
        UniqueConstraint("user_id", "hanzi_id", name="uq_user_flashcard_state_user_hanzi"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        index=True,
        nullable=False,
    )
    hanzi_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        index=True,
        nullable=False,
    )
    is_favorite: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_difficult: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

