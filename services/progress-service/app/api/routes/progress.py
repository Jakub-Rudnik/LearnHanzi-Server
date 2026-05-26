from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user_progress import ProgressEvent, ProgressResponse, RankingItem, UserHanziProgress
from app.services.user_progress import (
    record_progress,
    last_attempt,
    ranking,
    user_hanzi_progress,
)
from app.api.deps import get_db

router = APIRouter(prefix="/progress", tags=["progress"])

@router.post("/", response_model=ProgressResponse)
def create(event: ProgressEvent, db: Session = Depends(get_db)):
    return record_progress(db, event)

@router.get("/last")
def last(user_id: str, hanzi_id: str, db: Session = Depends(get_db)):
    result = last_attempt(db, user_id, hanzi_id)

    if not result:
        raise HTTPException(status_code=404, detail="Not found")

    return result

@router.get("/ranking", response_model=list[RankingItem])
def get_ranking_endpoint(limit: int = 100, db: Session = Depends(get_db)):
    return ranking(db, limit)

@router.get(
    "/user/{user_id}/hanzi",
    response_model=list[UserHanziProgress],
)
def get_user_hanzi_progress_endpoint(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    return user_hanzi_progress(db, user_id)
