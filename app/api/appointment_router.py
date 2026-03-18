from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.appointment import Appointment, AppointmentCreate, AppointmentUpdate
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.barber_repository import BarberRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.barbershop_schedule_repository import BarberShopScheduleRepository
from app.repositories.barber_schedule_repository import BarberScheduleRepository
from app.services.appointment_service import AppointmentService

router = APIRouter()


def get_appointment_service(db: Session):
    """Factory function to create AppointmentService with all dependencies."""
    return AppointmentService(
        appointment_repo=AppointmentRepository(db),
        barbershop_repo=BarberShopRepository(db),
        customer_repo=CustomerRepository(db),
        barber_repo=BarberRepository(db),
        service_repo=ServiceRepository(db),
        barbershop_schedule_repo=BarberShopScheduleRepository(db),
        barber_schedule_repo=BarberScheduleRepository(db),
    )


@router.post("/", response_model=Appointment, status_code=201)
def create_appointment(
    appointment_in: AppointmentCreate, db: Session = Depends(get_db)
):
    appointment_service = get_appointment_service(db)
    return appointment_service.create_appointment(appointment_in)


@router.get("/{appointment_id}", response_model=Appointment)
def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment_service = get_appointment_service(db)
    return appointment_service.get_appointment(appointment_id)


@router.get("/barbershop/{barbershop_id}", response_model=List[Appointment])
def get_barbershop_appointments(
    barbershop_id: int,
    status: str = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    appointment_service = get_appointment_service(db)
    return appointment_service.get_barbershop_appointments(barbershop_id, status)


@router.get("/customer/{customer_id}", response_model=List[Appointment])
def get_customer_appointments(customer_id: int, db: Session = Depends(get_db)):
    appointment_service = get_appointment_service(db)
    return appointment_service.get_customer_appointments(customer_id)


@router.get("/barber/{barber_id}", response_model=List[Appointment])
def get_barber_appointments(barber_id: int, db: Session = Depends(get_db)):
    appointment_service = get_appointment_service(db)
    return appointment_service.get_barber_appointments(barber_id)


@router.put("/{appointment_id}", response_model=Appointment)
def update_appointment(
    appointment_id: int,
    appointment_in: AppointmentUpdate,
    db: Session = Depends(get_db),
):
    appointment_service = get_appointment_service(db)
    return appointment_service.update_appointment(appointment_id, appointment_in)


@router.delete("/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    appointment_service = get_appointment_service(db)
    appointment_service.delete_appointment(appointment_id)
    return {"message": "Appointment deleted successfully"}
