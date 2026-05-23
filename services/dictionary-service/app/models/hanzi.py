import uuid
from sqlalchemy import String, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Hanzi(Base):
    __tablename__ = "hanzi"

    id: Mapped[int] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4
    )

    character: Mapped[str] = mapped_column(
        String(10), 
        unique=True, 
        index=True, 
        nullable=False
    )

    pinyin: Mapped[str] = mapped_column(
        String(50), 
        nullable=False
    )

    meaning_pl: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )

    meaning_en: Mapped[str] = mapped_column(
        String(255), 
        nullable=False
    )

    difficulty_level: Mapped[int] = mapped_column(
        Integer, 
        nullable=False
    )

    theme_category: Mapped[str] = mapped_column(
        String(100), 
        nullable=True
    )
