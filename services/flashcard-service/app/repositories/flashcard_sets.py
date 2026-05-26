from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from app.models.flashcard_set import FlashcardSet


def save_flashcard_set(db: Session, flashcard_set: FlashcardSet) -> FlashcardSet:
    db.add(flashcard_set)
    db.commit()
    db.refresh(flashcard_set)
    return flashcard_set


def get_flashcard_set_by_id(db: Session, set_id: UUID) -> FlashcardSet | None:
    stmt = (
        select(FlashcardSet)
        .options(selectinload(FlashcardSet.cards))
        .where(FlashcardSet.id == set_id)
    )
    return db.execute(stmt).scalar_one_or_none()


def list_flashcard_sets_by_user(db: Session, user_id: UUID) -> list[FlashcardSet]:
    stmt = (
        select(FlashcardSet)
        .options(selectinload(FlashcardSet.cards))
        .where(FlashcardSet.user_id == user_id)
        .order_by(desc(FlashcardSet.created_at))
    )
    return list(db.execute(stmt).scalars().all())


def delete_flashcard_set(db: Session, flashcard_set: FlashcardSet) -> None:
    db.delete(flashcard_set)
    db.commit()

