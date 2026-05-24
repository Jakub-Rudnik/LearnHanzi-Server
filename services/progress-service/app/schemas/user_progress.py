from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ProgressEvent(BaseModel):
    user_id: UUID
    hanzi_id: UUID
    is_correct: bool
    accuracy_score: float
    attempt_date: datetime | None = None

class ProgressResponse(ProgressEvent):
    id: UUID
    points_earned: int

    class Config:
        from_attributes = True


class RankingItem(BaseModel):
    user_id: UUID
    total_points: int
