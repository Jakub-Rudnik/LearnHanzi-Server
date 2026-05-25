from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.refresh_token_session import RefreshTokenSession


def get_refresh_session_by_hash(
    db: Session,
    token_hash: str,
) -> RefreshTokenSession | None:
    stmt = select(RefreshTokenSession).where(
        RefreshTokenSession.token_hash == token_hash,
    )
    return db.scalar(stmt)


def revoke_all_user_refresh_sessions(db: Session, user_id: UUID) -> None:
    stmt = (
        update(RefreshTokenSession)
        .where(
            RefreshTokenSession.user_id == user_id,
            RefreshTokenSession.revoked_at.is_(None),
        )
        .values(revoked_at=datetime.now(timezone.utc))
    )
    db.execute(stmt)

