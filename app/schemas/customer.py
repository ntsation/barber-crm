from pydantic import BaseModel, EmailStr
from datetime import datetime


class CustomerBase(BaseModel):
    name: str
    email: EmailStr | None = None
    phone: str


class CustomerCreate(CustomerBase):
    barbershop_id: int


class CustomerUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None


class Customer(CustomerBase):
    id: int
    barbershop_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    deleted_at: datetime | None

    class Config:
        from_attributes = True
