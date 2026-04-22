import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.config import settings
from app.models.user import User


def create_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(
        minutes=settings.access_token_expire_minutes,
    )

    payload = {
        "sub": str(user.id),
        "email": user.email,
        "username": user.username,
        "role": user.role.value,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "jti": uuid.uuid4().hex,
        "typ": "access",
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        issuer=settings.jwt_issuer,
        audience=settings.jwt_audience,
    )


def create_refresh_token() -> str:
    return secrets.token_urlsafe(64)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()