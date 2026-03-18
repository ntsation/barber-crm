from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List


class WorkingHoursSlot(BaseModel):
    start_time: str
    end_time: str

    @field_validator('start_time', 'end_time')
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        if v:
            import re
            if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', v):
                raise ValueError('Time must be in HH:MM format')
        return v


class WorkingDaySchedule(BaseModel):
    enabled: bool = True
    slots: List[WorkingHoursSlot] = []


class BarberBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = True
    working_days: Optional[List[str]] = None
    working_hours: Optional[WorkingDaySchedule] = None


class BarberCreate(BarberBase):
    barbershop_id: int
    user_id: Optional[int] = None


class BarberUpdate(BaseModel):
    name: Optional[str] = None
    specialty: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    working_days: Optional[List[str]] = None
    working_hours: Optional[WorkingDaySchedule] = None


class Barber(BarberBase):
    id: int
    barbershop_id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
