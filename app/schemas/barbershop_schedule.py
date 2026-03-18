from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DaySchedule(BaseModel):
    enabled: bool = True
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    break_start: Optional[str] = None
    break_end: Optional[str] = None


class BarberShopScheduleBase(BaseModel):
    monday: Optional[DaySchedule] = None
    tuesday: Optional[DaySchedule] = None
    wednesday: Optional[DaySchedule] = None
    thursday: Optional[DaySchedule] = None
    friday: Optional[DaySchedule] = None
    saturday: Optional[DaySchedule] = None
    sunday: Optional[DaySchedule] = None


class BarberShopScheduleCreate(BarberShopScheduleBase):
    barbershop_id: int


class BarberShopScheduleUpdate(BarberShopScheduleBase):
    pass


class BarberShopSchedule(BarberShopScheduleBase):
    id: int
    barbershop_id: int
    created_at: datetime
    updated_at: datetime
    is_active: bool
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
