from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ServiceBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: float
    duration_minutes: int
    is_active: Optional[bool] = True


class ServiceCreate(ServiceBase):
    barbershop_id: int


class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    duration_minutes: Optional[int] = None
    is_active: Optional[bool] = None


class Service(ServiceBase):
    id: int
    barbershop_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
