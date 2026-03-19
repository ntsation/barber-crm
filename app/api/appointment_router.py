from typing import List
from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.db.session import get_db
from app.schemas.appointment import Appointment, AppointmentCreate, AppointmentUpdate
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.barber_repository import BarberRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.barbershop_schedule_repository import BarberShopScheduleRepository
from app.repositories.barber_schedule_repository import BarberScheduleRepository
from app.repositories.audit_log_repository import AuditLogRepository
from app.services.appointment_service import AppointmentService
from app.core.logging import get_logger
from app.core.audit_middleware import get_request_info

logger = get_logger(__name__)
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def get_appointment_service(request: Request, db: Session = Depends(get_db)):
    """Factory function to create AppointmentService with all dependencies."""
    request_info = get_request_info(request)
    return AppointmentService(
        appointment_repo=AppointmentRepository(db),
        barbershop_repo=BarberShopRepository(db),
        customer_repo=CustomerRepository(db),
        barber_repo=BarberRepository(db),
        service_repo=ServiceRepository(db),
        barbershop_schedule_repo=BarberShopScheduleRepository(db),
        barber_schedule_repo=BarberScheduleRepository(db),
        audit_repo=AuditLogRepository(db),
        request_info=request_info,
    )


@router.post("/", response_model=Appointment, status_code=201)
@limiter.limit("30/minute")
def create_appointment(
    request: Request,
    appointment_in: AppointmentCreate,
    appointment_service: AppointmentService = Depends(get_appointment_service),
):
    """Create a new appointment."""
    logger.info(f"Creating appointment for barbershop {appointment_in.barbershop_id}")
    return appointment_service.create_appointment(appointment_in)


@router.get("/{appointment_id}", response_model=Appointment)
@limiter.limit("100/minute")
def get_appointment(
    request: Request,
    appointment_id: int,
    appointment_service: AppointmentService = Depends(get_appointment_service),
):
    """Get an appointment by ID."""
    return appointment_service.get_appointment(appointment_id)


@router.get("/barbershop/{barbershop_id}", response_model=List[Appointment])
@limiter.limit("100/minute")
def get_barbershop_appointments(
    request: Request,
    barbershop_id: int,
    status: str = Query(None, description="Filter by status"),
    appointment_service: AppointmentService = Depends(get_appointment_service),
):
    """Get all appointments for a barbershop."""
    return appointment_service.get_barbershop_appointments(barbershop_id, status)


@router.get("/customer/{customer_id}", response_model=List[Appointment])
@limiter.limit("100/minute")
def get_customer_appointments(
    request: Request,
    customer_id: int,
    appointment_service: AppointmentService = Depends(get_appointment_service),
):
    """Get all appointments for a customer."""
    return appointment_service.get_customer_appointments(customer_id)


@router.get("/barber/{barber_id}", response_model=List[Appointment])
@limiter.limit("100/minute")
def get_barber_appointments(
    request: Request,
    barber_id: int,
    appointment_service: AppointmentService = Depends(get_appointment_service),
):
    """Get all appointments for a barber."""
    return appointment_service.get_barber_appointments(barber_id)


@router.put("/{appointment_id}", response_model=Appointment)
@limiter.limit("60/minute")
def update_appointment(
    request: Request,
    appointment_id: int,
    appointment_in: AppointmentUpdate,
    appointment_service: AppointmentService = Depends(get_appointment_service),
):
    """Update an appointment."""
    return appointment_service.update_appointment(appointment_id, appointment_in)


@router.delete("/{appointment_id}")
@limiter.limit("20/minute")
def delete_appointment(
    request: Request,
    appointment_id: int,
    appointment_service: AppointmentService = Depends(get_appointment_service),
):
    """Delete an appointment."""
    appointment_service.delete_appointment(appointment_id)
    return {"message": "Appointment deleted successfully"}
