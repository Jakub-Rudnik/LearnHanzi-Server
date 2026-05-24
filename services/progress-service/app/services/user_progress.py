from app.models.user_progress import UserProgress
from app.repositories.user_progress import (
    create_progress,
    get_last_attempt,
    get_ranking,
)
from app.clients.dictionary_client import get_hanzi


def calculate_points(accuracy_score: float, difficulty_level: int) -> int:
    return int(accuracy_score * difficulty_level)


def record_progress(db, event):
    hanzi = get_hanzi(event.hanzi_id)
    difficulty = hanzi["difficulty_level"]

    points = calculate_points(event.accuracy_score, difficulty)

    progress = UserProgress(
        user_id=event.user_id,
        hanzi_id=event.hanzi_id,
        is_correct=event.is_correct,
        accuracy_score=event.accuracy_score,
        points_earned=points,
        attempt_date=event.attempt_date,
    )

    return create_progress(db, progress)


def last_attempt(db, user_id, hanzi_id):
    return get_last_attempt(db, user_id, hanzi_id)


def ranking(db, limit: int = 100):
    return get_ranking(db, limit)

