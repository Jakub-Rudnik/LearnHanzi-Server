from __future__ import annotations

from collections.abc import Iterable
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.flashcard_item import FlashcardItem
from app.models.flashcard_set import FlashcardSet
from app.models.user_flashcard_state import UserFlashcardState
from app.repositories.flashcard_sets import (
    delete_flashcard_set,
    get_flashcard_set_by_id,
    list_flashcard_sets_by_user,
    save_flashcard_set,
)
from app.repositories.user_flashcard_states import (
    delete_flashcard_state,
    get_flashcard_state,
    list_flashcard_states_by_flag,
    list_flashcard_states_for_hanzi_ids,
    save_flashcard_state,
)
from app.schemas.flashcard import (
    FlashcardItemRead,
    FlashcardSetCreate,
    FlashcardSetRead,
    FlashcardSetSummary,
    FlashcardSetUpdate,
    FlashcardStateRead,
    HanziRead,
    MarkedHanziRead,
    StudyCardRead,
    StudySetRead,
)
from app.services.dictionary_client import (
    DictionaryServiceError,
    HanziNotFoundError,
    get_hanzi,
)


def _normalize_hanzi_ids(hanzi_ids: Iterable[UUID]) -> list[UUID]:
    normalized = list(hanzi_ids)
    if not normalized:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one hanzi is required",
        )

    if len(normalized) != len(set(normalized)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hanzi ids must be unique",
        )

    return normalized


def _get_hanzi_read(hanzi_id: UUID) -> HanziRead:
    try:
        hanzi = get_hanzi(hanzi_id)
    except HanziNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except DictionaryServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc

    return HanziRead.model_validate(hanzi)


def _get_state_read(state: UserFlashcardState) -> FlashcardStateRead:
    return FlashcardStateRead.model_validate(state)


def _serialize_flashcard_set(flashcard_set: FlashcardSet) -> FlashcardSetRead:
    cards = [FlashcardItemRead.model_validate(card) for card in flashcard_set.cards]
    return FlashcardSetRead(
        id=flashcard_set.id,
        user_id=flashcard_set.user_id,
        name=flashcard_set.name,
        description=flashcard_set.description,
        cards_count=len(cards),
        cards=cards,
        created_at=flashcard_set.created_at,
        updated_at=flashcard_set.updated_at,
    )


def _serialize_flashcard_summary(flashcard_set: FlashcardSet) -> FlashcardSetSummary:
    return FlashcardSetSummary(
        id=flashcard_set.id,
        user_id=flashcard_set.user_id,
        name=flashcard_set.name,
        description=flashcard_set.description,
        cards_count=len(flashcard_set.cards),
        created_at=flashcard_set.created_at,
        updated_at=flashcard_set.updated_at,
    )


def _ensure_set_owner(flashcard_set: FlashcardSet | None, user_id: UUID) -> FlashcardSet:
    if flashcard_set is None or flashcard_set.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flashcard set not found",
        )
    return flashcard_set


def _replace_cards(flashcard_set: FlashcardSet, hanzi_ids: list[UUID], db: Session | None = None) -> None:
    """Replace flashcard items in a set.
    
    For existing sets, must delete old cards first to avoid constraint violations.
    The unique constraints on (set_id, position) and (set_id, hanzi_id) require
    this two-phase approach.
    """
    # For existing sets flush deletions before inserts to avoid unique collisions
    # on (set_id, position) and (set_id, hanzi_id).
    flashcard_set.cards.clear()
    if flashcard_set.id is not None and db is not None:
        db.flush()
    
    for index, hanzi_id in enumerate(hanzi_ids):
        item_data = {
            "hanzi_id": hanzi_id,
            "position": index + 1,
        }
        # Only set set_id for existing flashcard sets (already in DB)
        if flashcard_set.id is not None:
            item_data["set_id"] = flashcard_set.id
        
        flashcard_set.cards.append(FlashcardItem(**item_data))


def create_flashcard_set(
    db: Session,
    user_id: UUID,
    payload: FlashcardSetCreate,
) -> FlashcardSetRead:
    hanzi_ids = _normalize_hanzi_ids(payload.hanzi_ids)
    for hanzi_id in hanzi_ids:
        _get_hanzi_read(hanzi_id)

    flashcard_set = FlashcardSet(
        user_id=user_id,
        name=payload.name,
        description=payload.description,
    )
    _replace_cards(flashcard_set, hanzi_ids, db)
    flashcard_set = save_flashcard_set(db, flashcard_set)
    return _serialize_flashcard_set(flashcard_set)


def list_user_flashcard_sets(db: Session, user_id: UUID) -> list[FlashcardSetSummary]:
    sets = list_flashcard_sets_by_user(db, user_id)
    return [_serialize_flashcard_summary(flashcard_set) for flashcard_set in sets]


def get_user_flashcard_set(db: Session, user_id: UUID, set_id: UUID) -> FlashcardSetRead:
    flashcard_set = _ensure_set_owner(get_flashcard_set_by_id(db, set_id), user_id)
    return _serialize_flashcard_set(flashcard_set)


def update_flashcard_set(
    db: Session,
    user_id: UUID,
    set_id: UUID,
    payload: FlashcardSetUpdate,
) -> FlashcardSetRead:
    flashcard_set = _ensure_set_owner(get_flashcard_set_by_id(db, set_id), user_id)

    if payload.name is not None:
        flashcard_set.name = payload.name
    if payload.description is not None:
        flashcard_set.description = payload.description
    if payload.hanzi_ids is not None:
        hanzi_ids = _normalize_hanzi_ids(payload.hanzi_ids)
        for hanzi_id in hanzi_ids:
            _get_hanzi_read(hanzi_id)
        _replace_cards(flashcard_set, hanzi_ids, db)

    try:
        flashcard_set = save_flashcard_set(db, flashcard_set)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not update flashcard set due to card order conflict",
        ) from exc

    return _serialize_flashcard_set(flashcard_set)


def remove_flashcard_set(db: Session, user_id: UUID, set_id: UUID) -> None:
    flashcard_set = _ensure_set_owner(get_flashcard_set_by_id(db, set_id), user_id)
    delete_flashcard_set(db, flashcard_set)


def add_card_to_set(db: Session, user_id: UUID, set_id: UUID, hanzi_id: UUID) -> FlashcardSetRead:
    """Add a single hanzi card to an existing flashcard set."""
    flashcard_set = _ensure_set_owner(get_flashcard_set_by_id(db, set_id), user_id)
    
    # Check if hanzi exists and is valid
    _get_hanzi_read(hanzi_id)
    
    # Check if hanzi_id is already in the set
    if any(card.hanzi_id == hanzi_id for card in flashcard_set.cards):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Hanzi is already in this flashcard set",
        )
    
    # Add new card with next position
    new_position = len(flashcard_set.cards) + 1
    new_card = FlashcardItem(
        set_id=flashcard_set.id,
        hanzi_id=hanzi_id,
        position=new_position,
    )
    flashcard_set.cards.append(new_card)
    
    flashcard_set = save_flashcard_set(db, flashcard_set)
    return _serialize_flashcard_set(flashcard_set)


def remove_card_from_set(db: Session, user_id: UUID, set_id: UUID, hanzi_id: UUID) -> FlashcardSetRead:
    """Remove a single hanzi card from a flashcard set."""
    flashcard_set = _ensure_set_owner(get_flashcard_set_by_id(db, set_id), user_id)

    card_to_remove = next((card for card in flashcard_set.cards if card.hanzi_id == hanzi_id), None)
    if card_to_remove is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hanzi not found in this flashcard set",
        )

    removed_position = card_to_remove.position
    flashcard_set.cards.remove(card_to_remove)
    db.delete(card_to_remove)
    db.flush()

    # Reindex cards after the removed slot.
    for card in sorted(flashcard_set.cards, key=lambda item: item.position):
        if card.position > removed_position:
            card.position -= 1

    try:
        flashcard_set = save_flashcard_set(db, flashcard_set)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Could not reorder flashcard positions for this set",
        ) from exc

    return _serialize_flashcard_set(flashcard_set)


def get_study_set(db: Session, user_id: UUID, set_id: UUID) -> StudySetRead:
    flashcard_set = _ensure_set_owner(get_flashcard_set_by_id(db, set_id), user_id)
    states = list_flashcard_states_for_hanzi_ids(
        db,
        user_id,
        [card.hanzi_id for card in flashcard_set.cards],
    )
    states_by_hanzi_id = {state.hanzi_id: state for state in states}

    study_cards: list[StudyCardRead] = []
    for card in flashcard_set.cards:
        state = states_by_hanzi_id.get(card.hanzi_id)
        state_favorite = state.is_favorite if state else False
        state_difficult = state.is_difficult if state else False

        study_cards.append(
            StudyCardRead(
                card_id=card.id,
                set_id=flashcard_set.id,
                position=card.position,
                hanzi=_get_hanzi_read(card.hanzi_id),
                is_favorite=state_favorite,
                is_difficult=state_difficult,
            )
        )

    return StudySetRead(
        set_id=flashcard_set.id,
        set_name=flashcard_set.name,
        description=flashcard_set.description,
        cards=study_cards,
    )


def _upsert_state(
    db: Session,
    user_id: UUID,
    hanzi_id: UUID,
    *,
    is_favorite: bool | None = None,
    is_difficult: bool | None = None,
) -> UserFlashcardState | None:
    _get_hanzi_read(hanzi_id)
    state = get_flashcard_state(db, user_id, hanzi_id)
    is_new_state = state is None

    if state is None:
        state = UserFlashcardState(user_id=user_id, hanzi_id=hanzi_id)
        state.is_favorite = False
        state.is_difficult = False

    if is_favorite is not None:
        state.is_favorite = is_favorite
    if is_difficult is not None:
        state.is_difficult = is_difficult

    if not state.is_favorite and not state.is_difficult:
        if is_new_state:
            return None
        if state.id is not None:
            delete_flashcard_state(db, state)
            return None

    if is_new_state:
        db.add(state)

    return save_flashcard_state(db, state)


def set_favorite_state(db: Session, user_id: UUID, hanzi_id: UUID, value: bool) -> MarkedHanziRead:
    state = _upsert_state(db, user_id, hanzi_id, is_favorite=value)
    return _build_marked_hanzi_read(db, user_id, hanzi_id, state)


def set_difficult_state(db: Session, user_id: UUID, hanzi_id: UUID, value: bool) -> MarkedHanziRead:
    state = _upsert_state(db, user_id, hanzi_id, is_difficult=value)
    return _build_marked_hanzi_read(db, user_id, hanzi_id, state)


def _build_marked_hanzi_read(
    db: Session,
    user_id: UUID,
    hanzi_id: UUID,
    state: UserFlashcardState | None,
) -> MarkedHanziRead:
    fresh_state = state or get_flashcard_state(db, user_id, hanzi_id)
    return MarkedHanziRead(
        state=_get_state_read(fresh_state) if fresh_state else None,
        hanzi=_get_hanzi_read(hanzi_id),
    )


def list_favorite_hanzi(db: Session, user_id: UUID) -> list[MarkedHanziRead]:
    states = list_flashcard_states_by_flag(db, user_id, "favorite")
    return [
        MarkedHanziRead(state=_get_state_read(state), hanzi=_get_hanzi_read(state.hanzi_id))
        for state in states
    ]


def list_difficult_hanzi(db: Session, user_id: UUID) -> list[MarkedHanziRead]:
    states = list_flashcard_states_by_flag(db, user_id, "difficult")
    return [
        MarkedHanziRead(state=_get_state_read(state), hanzi=_get_hanzi_read(state.hanzi_id))
        for state in states
    ]


def mark_difficulty_from_result(
    db: Session,
    user_id: UUID,
    hanzi_id: UUID,
    accuracy_score: float,
    is_correct: bool,
) -> None:
    """Auto-mark character as difficult based on learning progress.

    Threshold: accuracy < configured threshold (default 0.6 = 60%) = mark as difficult
               accuracy >= configured threshold = remove from difficult

    This is called internally by progress-service after each attempt.
    It's not user-controlled; it's a suggestion system for the frontend.
    """
    # Only process if hanzi exists (don't throw, just skip)
    try:
        _get_hanzi_read(hanzi_id)
    except HTTPException:
        return

    should_be_difficult = accuracy_score < settings.accuracy_difficulty_threshold and not is_correct

    if should_be_difficult:
        _upsert_state(db, user_id, hanzi_id, is_difficult=True)
    else:
        # If accuracy is good, remove from difficult
        state = get_flashcard_state(db, user_id, hanzi_id)
        if state is not None and state.is_difficult:
            _upsert_state(db, user_id, hanzi_id, is_difficult=False)



