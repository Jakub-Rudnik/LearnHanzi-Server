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


def username_taken_by_other(
    db: Session,
    username: str,
    excluded_user_id: UUID,
) -> bool:
    normalized = username.strip().lower()
    stmt = select(User.id).where(
        func.lower(User.username) == normalized,
        User.id != excluded_user_id,
    )
    return db.scalar(stmt) is not None


def email_taken_by_other(
    db: Session,
    email: str,
    excluded_user_id: UUID,
) -> bool:
    normalized = email.strip().lower()
    stmt = select(User.id).where(
        func.lower(User.email) == normalized,
        User.id != excluded_user_id,
    )
    return db.scalar(stmt) is not None
