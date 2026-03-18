from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BarberScheduleBase(BaseModel):
    day_of_week: int
    start_time: str
    end_time: str
    is_available: Optional[bool] = True


class BarberScheduleCreate(BarberScheduleBase):
    barber_id: int


class BarberScheduleUpdate(BaseModel):
    day_of_week: Optional[int] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    is_available: Optional[bool] = None


class BarberSchedule(BarberScheduleBase):
    id: int
    barber_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
