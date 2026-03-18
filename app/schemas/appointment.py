from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AppointmentBase(BaseModel):
    scheduled_date: datetime
    scheduled_time: str
    status: Optional[str] = "pending"
    notes: Optional[str] = None
    total_price: Optional[float] = None


class AppointmentCreate(AppointmentBase):
    barbershop_id: int
    customer_id: int
    barber_id: int
    service_id: int


class AppointmentUpdate(BaseModel):
    status: Optional[str] = None
    notes: Optional[str] = None


class Appointment(AppointmentBase):
    id: int
    barbershop_id: int
    customer_id: int
    barber_id: int
    service_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
