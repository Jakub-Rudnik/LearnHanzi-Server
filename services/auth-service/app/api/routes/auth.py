from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.jwt import create_access_token
from app.schemas.auth import (
    AuthResponse,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserRead,
)
from app.services.auth_service import authenticate_user, register_user


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: UserCreate,
    db: Session = Depends(get_db),
) -> AuthResponse:
    user = register_user(
        db=db,
        username=payload.username,
        email=payload.email,
        password=payload.password,
    )

    return AuthResponse(
        user=user,
        token=TokenResponse(access_token=create_access_token(user)),
    )


@router.post("/login", response_model=AuthResponse)
def login(
    payload: UserLogin,
    db: Session = Depends(get_db),
) -> AuthResponse:
    user = authenticate_user(
        db=db,
        identifier=payload.identifier,
        password=payload.password,
    )

    return AuthResponse(
        user=user,
        token=TokenResponse(access_token=create_access_token(user)),
    )


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(get_current_user)) -> UserRead:
    return current_user