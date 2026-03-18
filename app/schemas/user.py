from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: str | None = None
    email: EmailStr | None = None


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    deleted_at: datetime | None

    class Config:
        from_attributes = True
