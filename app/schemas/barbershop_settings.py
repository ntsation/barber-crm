from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class BarberShopSettingsBase(BaseModel):
    accept_online_booking: Optional[bool] = None
    require_payment_confirmation: Optional[bool] = None
    advance_booking_hours: Optional[int] = None
    max_advance_booking_days: Optional[int] = None
    cancellation_hours: Optional[int] = None
    notification_email: Optional[EmailStr] = None
    notification_phone: Optional[str] = None
    default_duration_minutes: Optional[int] = None
    allow_walk_ins: Optional[bool] = None
    max_walk_ins_per_day: Optional[int] = None


class BarberShopSettingsCreate(BarberShopSettingsBase):
    barbershop_id: int


class BarberShopSettingsUpdate(BarberShopSettingsBase):
    pass


class BarberShopSettings(BarberShopSettingsBase):
    id: int
    barbershop_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
