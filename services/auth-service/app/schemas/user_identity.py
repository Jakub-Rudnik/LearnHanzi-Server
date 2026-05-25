from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.user import AccountStatus, UserRole


class UserIdentityRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: EmailStr
    role: UserRole
    account_status: AccountStatus
    created_at: datetime
    last_login_at: datetime | None = None


class UserBasicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    account_status: AccountStatus
