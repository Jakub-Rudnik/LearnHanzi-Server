from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_id(db: Session, user_id: UUID) -> User | None:
    stmt = select(User).where(User.id == user_id)
    return db.scalar(stmt)


def get_user_by_email(db: Session, email: str) -> User | None:
    normalized = email.strip().lower()
    stmt = select(User).where(func.lower(User.email) == normalized)
    return db.scalar(stmt)


def get_user_by_username(db: Session, username: str) -> User | None:
    normalized = username.strip().lower()
    stmt = select(User).where(func.lower(User.username) == normalized)
    return db.scalar(stmt)


def get_user_by_identifier(db: Session, identifier: str) -> User | None:
    normalized = identifier.strip().lower()
    stmt = select(User).where(
        or_(
            func.lower(User.email) == normalized,
            func.lower(User.username) == normalized,
        )
    )
    return db.scalar(stmt)