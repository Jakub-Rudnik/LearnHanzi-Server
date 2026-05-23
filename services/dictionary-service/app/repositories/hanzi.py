from uuid import UUID
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.hanzi import Hanzi

def get_all_hanzi(db: Session, limit: int = 100, offset: int = 0) -> List[Hanzi]:
    stmt = select(Hanzi).offset(offset).limit(limit)
    return db.execute(stmt).scalars().all()

def get_hanzi_by_id(db: Session, hanzi_id: UUID) -> Hanzi | None:
    stmt = select(Hanzi).where(Hanzi.id == hanzi_id)
    return db.execute(stmt).scalar_one_or_none()

def get_hanzi_by_character(db: Session, character: str) -> Hanzi | None:
    stmt = select(Hanzi).where(Hanzi.character == character)
    return db.execute(stmt).scalar_one_or_none()

def create_hanzi(db: Session, hanzi: Hanzi) -> Hanzi:
    db.add(hanzi)
    db.commit()
    db.refresh(hanzi)
    return hanzi
