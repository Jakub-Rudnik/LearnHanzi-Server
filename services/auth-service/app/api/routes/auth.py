from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.schemas.auth import (
    AuthResponse,
    RefreshTokenRequest,
    TokenPairResponse,
    UserCreate,
    UserLogin,
    UserRead,
)
from app.services.auth_service import authenticate_user, register_user
from app.services.session_service import (
    issue_token_pair,
    revoke_refresh_token,
    rotate_refresh_token,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> AuthResponse:
    user = register_user(
        db=db,
        username=payload.username,
        email=payload.email,
        password=payload.password,
    )

    access_token, refresh_token = issue_token_pair(
        db=db,
        user=user,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    return AuthResponse(
        user=user,
        tokens=TokenPairResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        ),
    )


@router.post("/login", response_model=AuthResponse)
def login(
    payload: UserLogin,
    request: Request,
    db: Session = Depends(get_db),
) -> AuthResponse:
    user = authenticate_user(
        db=db,
        identifier=payload.identifier,
        password=payload.password,
    )

    access_token, refresh_token = issue_token_pair(
        db=db,
        user=user,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    return AuthResponse(
        user=user,
        tokens=TokenPairResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        ),
    )


@router.post("/refresh", response_model=AuthResponse)
def refresh(
    payload: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> AuthResponse:
    user, access_token, refresh_token = rotate_refresh_token(
        db=db,
        raw_refresh_token=payload.refresh_token,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )

    return AuthResponse(
        user=user,
        tokens=TokenPairResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        ),
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
) -> Response:
    revoke_refresh_token(
        db=db,
        raw_refresh_token=payload.refresh_token,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserRead)
def me(
    current_user=Depends(get_current_active_user),
) -> UserRead:
    return current_user