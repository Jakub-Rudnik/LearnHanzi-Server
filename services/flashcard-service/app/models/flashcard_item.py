from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class FlashcardItem(Base):
    __tablename__ = "flashcard_items"
    __table_args__ = (
        UniqueConstraint("set_id", "position", name="uq_flashcard_items_set_position"),
        UniqueConstraint("set_id", "hanzi_id", name="uq_flashcard_items_set_hanzi"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("flashcard_sets.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    hanzi_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        index=True,
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    flashcard_set: Mapped["FlashcardSet"] = relationship(back_populates="cards")

