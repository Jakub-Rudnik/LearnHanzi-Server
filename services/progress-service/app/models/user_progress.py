import uuid
from sqlalchemy import Column, String, Boolean, Float, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(UUID(as_uuid=True), nullable=False)
    hanzi_id = Column(UUID(as_uuid=True), nullable=False)

    is_correct = Column(Boolean, nullable=False)
    accuracy_score = Column(Float, nullable=False)
    points_earned = Column(Integer, nullable=False, default=0)

    attempt_date = Column(DateTime(timezone=True), server_default=func.now())
