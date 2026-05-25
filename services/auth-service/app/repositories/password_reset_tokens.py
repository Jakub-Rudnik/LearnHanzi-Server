from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken


def create_password_reset_token(
    db: Session,
    user_id: UUID,
    token_hash: str,
    expires_at: datetime,
    requested_ip: str | None = None,
) -> PasswordResetToken:
    token = PasswordResetToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        requested_ip=requested_ip,
    )
    db.add(token)
    return token


def get_password_reset_token_by_hash(
    db: Session,
    token_hash: str,
) -> PasswordResetToken | None:
    stmt = select(PasswordResetToken).where(
        PasswordResetToken.token_hash == token_hash,
    )
    return db.scalar(stmt)


def mark_password_reset_token_used(
    db: Session,
    token: PasswordResetToken,
) -> None:
    token.used_at = datetime.now(timezone.utc)


def revoke_active_password_reset_tokens_for_user(
    db: Session,
    user_id: UUID,
) -> None:
    now = datetime.now(timezone.utc)
    stmt = (
        update(PasswordResetToken)
        .where(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at > now,
        )
        .values(used_at=now)
    )
    db.execute(stmt)

