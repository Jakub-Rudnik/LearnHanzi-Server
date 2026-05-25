from hashlib import sha256
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import (
    hash_password,
    validate_password_strength,
    verify_password,
)
from app.models.user import AccountStatus, User, UserRole
from app.repositories.password_reset_tokens import (
    create_password_reset_token,
    get_password_reset_token_by_hash,
    mark_password_reset_token_used,
    revoke_active_password_reset_tokens_for_user,
)
from app.repositories.refresh_tokens import revoke_all_user_refresh_sessions
from app.repositories.users import (
    email_taken_by_other,
    get_user_by_email,
    get_user_by_identifier,
    get_user_by_id,
    get_user_by_username,
    username_taken_by_other,
)
from app.utils.email import send_password_reset_email


def _normalize(value: str) -> str:
    return value.strip().lower()


def _hash_reset_token(raw_token: str) -> str:
    return sha256(raw_token.encode("utf-8")).hexdigest()


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

    try:
        validate_password_strength(password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    user = User(
        username=normalized_username,
        email=normalized_email,
        password_hash=hash_password(password),
        role=UserRole.USER,
        account_status=AccountStatus.ACTIVE,
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

    if user.account_status != AccountStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.account_status.value.lower()}",
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user


def update_profile(
    db: Session,
    user: User,
    username: str | None,
    email: str | None,
) -> User:
    if username is None and email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No profile fields provided",
        )

    if username is not None:
        normalized_username = _normalize(username)
        if username_taken_by_other(db, normalized_username, user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )
        user.username = normalized_username

    if email is not None:
        normalized_email = _normalize(email)
        if email_taken_by_other(db, normalized_email, user.id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        user.email = normalized_email

    db.commit()
    db.refresh(user)
    return user


def request_password_reset(
    db: Session,
    email: str,
    requested_ip: str | None,
) -> str | None:
    user = get_user_by_email(db, _normalize(email))
    if user is None:
        return None

    reset_token = token_urlsafe(48)
    expires_at = datetime.now(timezone.utc).replace(microsecond=0)
    expires_at = expires_at + timedelta(
        minutes=settings.password_reset_token_expire_minutes,
    )

    revoke_active_password_reset_tokens_for_user(db, user.id)
    reset_token_row = create_password_reset_token(
        db=db,
        user_id=user.id,
        token_hash=_hash_reset_token(reset_token),
        expires_at=expires_at,
        requested_ip=requested_ip,
    )
    db.commit()

    try:
        email_sent = send_password_reset_email(
            recipient=user.email,
            reset_token=reset_token,
        )
    except Exception as exc:
        mark_password_reset_token_used(db, reset_token_row)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cannot send reset email",
        ) from exc

    if email_sent:
        return None

    if settings.password_reset_debug_return_token:
        return reset_token

    mark_password_reset_token_used(db, reset_token_row)
    db.commit()

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Password reset email is not configured",
    )


def confirm_password_reset(
    db: Session,
    token: str,
    new_password: str,
) -> None:
    try:
        validate_password_strength(new_password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    reset_token = get_password_reset_token_by_hash(db, _hash_reset_token(token))
    now = datetime.now(timezone.utc)

    if (
        reset_token is None
        or reset_token.used_at is not None
        or reset_token.expires_at <= now
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user = get_user_by_id(db, reset_token.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    user.password_hash = hash_password(new_password)

    mark_password_reset_token_used(db, reset_token)
    revoke_all_user_refresh_sessions(db, user.id)
    db.commit()


def change_password(
    db: Session,
    user: User,
    current_password: str,
    new_password: str,
) -> None:
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    try:
        validate_password_strength(new_password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if current_password == new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )

    user.password_hash = hash_password(new_password)
    revoke_all_user_refresh_sessions(db, user.id)
    db.commit()


