from app.models.user_progress import UserProgress
from app.repositories.user_progress import (
    create_progress,
    get_last_attempt,
    get_ranking,
)
from app.clients.dictionary_client import get_hanzi
from app.core.config import settings
import requests


def calculate_points(accuracy_score: float) -> int:
    return int(accuracy_score * 100)


def _sync_difficulty_to_flashcard_service(user_id, hanzi_id, accuracy_score: float, is_correct: bool):
    """Notify flashcard-service to auto-mark character as difficult if needed."""
    try:
        url = f"{settings.flashcard_service_url.rstrip('/')}/flashcards/internal/sync-difficulty/{user_id}/{hanzi_id}"
        requests.post(
            url,
            params={"accuracy_score": accuracy_score, "is_correct": is_correct},
            timeout=5,
        )
    except Exception as e:
        # Don't fail the progress recording if flashcard sync fails
        print(f"Warning: Failed to sync difficulty to flashcard service: {e}")


def record_progress(db, event):
    points = calculate_points(event.accuracy_score)

    progress = UserProgress(
        user_id=event.user_id,
        hanzi_id=event.hanzi_id,
        is_correct=event.is_correct,
        accuracy_score=event.accuracy_score,
        points_earned=points,
        attempt_date=event.attempt_date,
    )

    result = create_progress(db, progress)

    _sync_difficulty_to_flashcard_service(
        event.user_id,
        event.hanzi_id,
        event.accuracy_score,
        event.is_correct,
    )

    return result


def last_attempt(db, user_id, hanzi_id):
    return get_last_attempt(db, user_id, hanzi_id)


def ranking(db, limit: int = 100):
    return get_ranking(db, limit)
