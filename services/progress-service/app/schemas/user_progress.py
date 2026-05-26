from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProgressEvent(BaseModel):
    user_id: UUID
    hanzi_id: UUID

    is_correct: bool
    accuracy_score: float = Field(ge=0.0, le=1.0)

    attempt_date: datetime | None = None


class ProgressResponse(BaseModel):
    id: UUID
    user_id: UUID
    hanzi_id: UUID

    is_correct: bool
    accuracy_score: float
    points_earned: int
    attempt_date: datetime

    class Config:
        from_attributes = True


class RankingItem(BaseModel):
    user_id: UUID
    total_points: int
