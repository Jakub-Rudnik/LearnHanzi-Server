from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_current_active_user,
    get_current_token_payload,
    get_db,
)
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    PasswordChange,
    PasswordResetConfirm,
    PasswordResetRequest,
    PasswordResetRequestResponse,
    RefreshTokenRequest,
    SessionRead,
    TokenClaimsRead,
    TokenPairResponse,
    UserCreate,
    UserLogin,
    UserRead,
)
from app.services.auth_service import (
    authenticate_user,
    change_password,
    confirm_password_reset,
    register_user,
    request_password_reset,
)
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


@router.post("/password-reset/request", response_model=PasswordResetRequestResponse)
def password_reset_request(
    payload: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> PasswordResetRequestResponse:
    reset_token = request_password_reset(
        db=db,
        email=payload.email,
        requested_ip=request.client.host if request.client else None,
    )

    return PasswordResetRequestResponse(
        detail=(
            "If an account with this email exists, reset instructions were sent"
        ),
        reset_token=reset_token,
    )


@router.post("/password-reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
def password_reset_confirm(
    payload: PasswordResetConfirm,
    db: Session = Depends(get_db),
) -> Response:
    confirm_password_reset(
        db=db,
        token=payload.token,
        new_password=payload.new_password,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_user_password(
    payload: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> Response:
    change_password(
        db=db,
        user=current_user,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(get_current_active_user)) -> UserRead:
    return current_user


@router.get("/session", response_model=SessionRead)
def session(
    current_user=Depends(get_current_active_user),
    token_payload: dict = Depends(get_current_token_payload),
) -> SessionRead:
    return SessionRead(
        user=current_user,
        token=TokenClaimsRead.model_validate(token_payload),
    )