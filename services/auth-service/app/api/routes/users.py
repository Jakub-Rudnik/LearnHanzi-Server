from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User, UserRole
from app.repositories.users import get_user_by_id
from app.schemas.auth import UserProfileUpdate, UserRead
from app.schemas.user_identity import UserBasicRead, UserIdentityRead
from app.services.auth_service import update_profile

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me/identity", response_model=UserIdentityRead)
def get_my_identity(
    current_user: User = Depends(get_current_active_user),
) -> UserIdentityRead:
    return current_user


@router.get("/{user_id}/identity", response_model=UserIdentityRead)
def get_user_identity(
    user_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> UserIdentityRead:
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.patch("/me", response_model=UserRead)
def patch_my_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> UserRead:
    return update_profile(
        db=db,
        user=current_user,
        username=payload.username,
        email=payload.email,
    )


@router.get("/{user_id}/basic", response_model=UserBasicRead)
def get_user_basic_data(
    user_id: UUID,
    _: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
) -> UserBasicRead:
    user = get_user_by_id(db, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user

