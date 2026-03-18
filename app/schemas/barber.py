from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict


class BarberBase(BaseModel):
    name: str
    specialty: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = True
    working_days: Optional[List[str]] = None
    working_hours: Optional[Dict[str, str]] = None


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
    working_hours: Optional[Dict[str, str]] = None


class Barber(BarberBase):
    id: int
    barbershop_id: int
    user_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
