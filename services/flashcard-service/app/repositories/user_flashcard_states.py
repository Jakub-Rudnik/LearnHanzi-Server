from __future__ import annotations

from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.user_flashcard_state import UserFlashcardState


def get_flashcard_state(db: Session, user_id: UUID, hanzi_id: UUID) -> UserFlashcardState | None:
    stmt = select(UserFlashcardState).where(
        UserFlashcardState.user_id == user_id,
        UserFlashcardState.hanzi_id == hanzi_id,
    )
    return db.execute(stmt).scalar_one_or_none()


def list_flashcard_states_for_hanzi_ids(
    db: Session,
    user_id: UUID,
    hanzi_ids: list[UUID],
) -> list[UserFlashcardState]:
    if not hanzi_ids:
        return []

    stmt = select(UserFlashcardState).where(
        UserFlashcardState.user_id == user_id,
        UserFlashcardState.hanzi_id.in_(hanzi_ids),
    )
    return list(db.execute(stmt).scalars().all())


def list_flashcard_states_by_flag(
    db: Session,
    user_id: UUID,
    flag: str,
) -> list[UserFlashcardState]:
    if flag == "favorite":
        clause = UserFlashcardState.is_favorite.is_(True)
    elif flag == "difficult":
        clause = UserFlashcardState.is_difficult.is_(True)
    else:
        raise ValueError("Unsupported flag")

    stmt = (
        select(UserFlashcardState)
        .where(UserFlashcardState.user_id == user_id, clause)
        .order_by(desc(UserFlashcardState.updated_at))
    )
    return list(db.execute(stmt).scalars().all())


def save_flashcard_state(db: Session, state: UserFlashcardState) -> UserFlashcardState:
    db.add(state)
    db.commit()
    db.refresh(state)
    return state


def delete_flashcard_state(db: Session, state: UserFlashcardState) -> None:
    db.delete(state)
    db.commit()

