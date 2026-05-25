from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.jwt import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
)
from app.models.refresh_token_session import RefreshTokenSession
from app.models.user import AccountStatus, User
from app.repositories.refresh_tokens import get_refresh_session_by_hash
from app.repositories.users import get_user_by_id


def _refresh_expires_at() -> datetime:
    return datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days,
    )


def issue_token_pair(
    db: Session,
    user: User,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> tuple[str, str]:
    access_token = create_access_token(user)
    refresh_token = create_refresh_token()

    session = RefreshTokenSession(
        user_id=user.id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=_refresh_expires_at(),
        user_agent=user_agent[:255] if user_agent else None,
        ip_address=ip_address,
    )
    db.add(session)
    db.commit()

    return access_token, refresh_token


def rotate_refresh_token(
    db: Session,
    raw_refresh_token: str,
    user_agent: str | None = None,
    ip_address: str | None = None,
) -> tuple[User, str, str]:
    token_hash = hash_refresh_token(raw_refresh_token)
    session = get_refresh_session_by_hash(db, token_hash)

    if (
        session is None
        or session.revoked_at is not None
        or session.expires_at <= datetime.now(timezone.utc)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = get_user_by_id(db, session.user_id)
    if user is None or user.account_status != AccountStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    session.revoked_at = datetime.now(timezone.utc)

    access_token, refresh_token = issue_token_pair(
        db=db,
        user=user,
        user_agent=user_agent or session.user_agent,
        ip_address=ip_address or session.ip_address,
    )

    return user, access_token, refresh_token


def revoke_refresh_token(
    db: Session,
    raw_refresh_token: str,
) -> None:
    token_hash = hash_refresh_token(raw_refresh_token)
    session = get_refresh_session_by_hash(db, token_hash)

    if session is None:
        return

    if session.revoked_at is None:
        session.revoked_at = datetime.now(timezone.utc)
        db.commit()