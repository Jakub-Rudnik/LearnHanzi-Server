from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.auth import CurrentUser
from app.schemas.flashcard import (
    FlashcardSetCreate,
    FlashcardSetRead,
    FlashcardSetSummary,
    FlashcardSetUpdate,
    MarkedHanziRead,
    StudySetRead,
)
from app.services.flashcards import (
    add_card_to_set,
    create_flashcard_set,
    get_study_set,
    get_user_flashcard_set,
    list_difficult_hanzi,
    list_favorite_hanzi,
    list_user_flashcard_sets,
    mark_difficulty_from_result,
    remove_card_from_set,
    remove_flashcard_set,
    set_difficult_state,
    set_favorite_state,
    update_flashcard_set,
)

router = APIRouter(prefix="/flashcards", tags=["flashcards"])


@router.post("/sets", response_model=FlashcardSetRead, status_code=status.HTTP_201_CREATED)
def create_set(
    payload: FlashcardSetCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return create_flashcard_set(db, current_user.id, payload)


@router.get("/sets", response_model=list[FlashcardSetSummary])
def list_sets(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return list_user_flashcard_sets(db, current_user.id)


@router.get("/sets/{set_id}", response_model=FlashcardSetRead)
def get_set(
    set_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return get_user_flashcard_set(db, current_user.id, set_id)


@router.put("/sets/{set_id}", response_model=FlashcardSetRead)
def update_set(
    set_id: UUID,
    payload: FlashcardSetUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return update_flashcard_set(db, current_user.id, set_id, payload)


@router.delete("/sets/{set_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_set(
    set_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    remove_flashcard_set(db, current_user.id, set_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/sets/{set_id}/cards/{hanzi_id}", response_model=FlashcardSetRead)
def add_card_to_flashcard_set(
    set_id: UUID,
    hanzi_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Add a single hanzi card to a flashcard set."""
    return add_card_to_set(db, current_user.id, set_id, hanzi_id)


@router.delete("/sets/{set_id}/cards/{hanzi_id}", response_model=FlashcardSetRead)
def remove_card_from_flashcard_set(
    set_id: UUID,
    hanzi_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Remove a single hanzi card from a flashcard set."""
    return remove_card_from_set(db, current_user.id, set_id, hanzi_id)


@router.get("/sets/{set_id}/study", response_model=StudySetRead)
def study_set(
    set_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return get_study_set(db, current_user.id, set_id)


@router.get("/favorites", response_model=list[MarkedHanziRead])
def get_favorites(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return list_favorite_hanzi(db, current_user.id)


@router.post("/favorites/{hanzi_id}", response_model=MarkedHanziRead)
def add_favorite(
    hanzi_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return set_favorite_state(db, current_user.id, hanzi_id, True)


@router.delete("/favorites/{hanzi_id}", response_model=MarkedHanziRead)
def remove_favorite(
    hanzi_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return set_favorite_state(db, current_user.id, hanzi_id, False)


@router.get("/difficult", response_model=list[MarkedHanziRead])
def get_difficult(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return list_difficult_hanzi(db, current_user.id)


@router.post("/difficult/{hanzi_id}", response_model=MarkedHanziRead)
def add_difficult(
    hanzi_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return set_difficult_state(db, current_user.id, hanzi_id, True)


@router.delete("/difficult/{hanzi_id}", response_model=MarkedHanziRead)
def remove_difficult(
    hanzi_id: UUID,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    return set_difficult_state(db, current_user.id, hanzi_id, False)


# Internal endpoint — called by progress-service
@router.post("/internal/sync-difficulty/{user_id}/{hanzi_id}")
def sync_difficulty(
    user_id: UUID,
    hanzi_id: UUID,
    accuracy_score: float,
    is_correct: bool,
    db: Session = Depends(get_db),
):
    """Auto-mark character as difficult based on performance.

    Called internally by progress-service after recording an attempt.
    Threshold: accuracy < configured threshold (see ACCURACY_DIFFICULTY_THRESHOLD in config)
               Default: 0.6 (60%) = mark as difficult
               accuracy >= threshold = remove from difficult
    """
    mark_difficulty_from_result(db, user_id, hanzi_id, accuracy_score, is_correct)
    return {"status": "synced"}



