from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User, UserRole
from app.repositories.users import (
    get_user_by_email,
    get_user_by_identifier,
    get_user_by_username,
)


def _normalize(value: str) -> str:
    return value.strip().lower()


def register_user(
    db: Session,
    username: str,
    email: str,
    password: str,
) -> User:
    normalized_username = _normalize(username)
    normalized_email = _normalize(email)

    if get_user_by_email(db, normalized_email) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    if get_user_by_username(db, normalized_username) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    user = User(
        username=normalized_username,
        email=normalized_email,
        password_hash=hash_password(password),
        role=UserRole.USER,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(
    db: Session,
    identifier: str,
    password: str,
) -> User:
    user = get_user_by_identifier(db, _normalize(identifier))

    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user