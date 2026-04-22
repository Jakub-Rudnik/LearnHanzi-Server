from sqlalchemy import select
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