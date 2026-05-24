from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc

from app.models.user_progress import UserProgress

def create_progress(db: Session, progress: UserProgress) -> UserProgress:
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress

def get_last_attempt(db: Session, user_id, hanzi_id):
    stmt = (
        select(UserProgress)
        .where(
            UserProgress.user_id == user_id,
            UserProgress.hanzi_id == hanzi_id,
        )
        .order_by(desc(UserProgress.attempt_date))
        .limit(1)
    )

    return db.execute(stmt).scalar_one_or_none()

def get_ranking(db: Session, limit: int = 100):
    stmt = (
        select(
            UserProgress.user_id,
            func.sum(UserProgress.points_earned).label("total_points")
        )
        .group_by(UserProgress.user_id)
        .order_by(desc("total_points"))
        .limit(limit)
    )

    return db.execute(stmt).all()
