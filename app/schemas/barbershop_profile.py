from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BarberShopProfileBase(BaseModel):
    description: Optional[str] = None
    services: Optional[str] = None
    logo_url: Optional[str] = None
    banner_url: Optional[str] = None


class BarberShopProfileCreate(BarberShopProfileBase):
    barbershop_id: int


class BarberShopProfileUpdate(BarberShopProfileBase):
    pass


class BarberShopProfile(BarberShopProfileBase):
    id: int
    barbershop_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
