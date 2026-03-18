from pydantic import BaseModel
from datetime import datetime


class BarberShopBase(BaseModel):
    name: str
    address: str
    phone: str


class BarberShopCreate(BarberShopBase):
    owner_id: int


class BarberShopUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None


class BarberShop(BarberShopBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    deleted_at: datetime | None

    class Config:
        from_attributes = True
