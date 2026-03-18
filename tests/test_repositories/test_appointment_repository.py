import pytest
from app.repositories.appointment_repository import (
    AppointmentRepository,
    IAppointmentRepository,
)
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.barber_repository import BarberRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.user_repository import UserRepository
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.schemas.user import UserCreate
from app.schemas.barbershop import BarberShopCreate
from app.schemas.customer import CustomerCreate
from app.schemas.barber import BarberCreate
from app.schemas.service import ServiceCreate
from datetime import datetime


def test_create_appointment(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    customer = customer_repo.create(
        CustomerCreate(
            name="Customer",
            email="customer@example.com",
            phone="555-1234",
            barbershop_id=barbershop.id,
        )
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(
        BarberCreate(name="Barber", barbershop_id=barbershop.id)
    )

    service_repo = ServiceRepository(db)
    service = service_repo.create(
        ServiceCreate(
            name="Haircut",
            description="Classic",
            price=25.0,
            duration_minutes=30,
            barbershop_id=barbershop.id,
        )
    )

    appointment_repo = AppointmentRepository(db)
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:00",
        status="pending",
    )
    appointment = appointment_repo.create(appointment_data)

    assert appointment.id is not None
    assert appointment.status == "pending"


def test_get_by_id(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    customer = customer_repo.create(
        CustomerCreate(
            name="Customer",
            email="customer@example.com",
            phone="555-1234",
            barbershop_id=barbershop.id,
        )
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(
        BarberCreate(name="Barber", barbershop_id=barbershop.id)
    )

    service_repo = ServiceRepository(db)
    service = service_repo.create(
        ServiceCreate(
            name="Haircut",
            description="Classic",
            price=25.0,
            duration_minutes=30,
            barbershop_id=barbershop.id,
        )
    )

    appointment_repo = AppointmentRepository(db)
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:00",
    )
    appointment = appointment_repo.create(appointment_data)

    retrieved = appointment_repo.get_by_id(appointment.id)
    assert retrieved is not None
    assert retrieved.status == "pending"


def test_get_by_id_not_found(db):
    appointment_repo = AppointmentRepository(db)
    appointment = appointment_repo.get_by_id(999)
    assert appointment is None


def test_get_by_barbershop(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    customer = customer_repo.create(
        CustomerCreate(
            name="Customer",
            email="customer@example.com",
            phone="555-1234",
            barbershop_id=barbershop.id,
        )
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(
        BarberCreate(name="Barber", barbershop_id=barbershop.id)
    )

    service_repo = ServiceRepository(db)
    service = service_repo.create(
        ServiceCreate(
            name="Haircut",
            description="Classic",
            price=25.0,
            duration_minutes=30,
            barbershop_id=barbershop.id,
        )
    )

    appointment_repo = AppointmentRepository(db)
    appointment_repo.create(
        AppointmentCreate(
            barbershop_id=barbershop.id,
            customer_id=customer.id,
            barber_id=barber.id,
            service_id=service.id,
            scheduled_date=datetime(2024, 1, 1, 10, 0),
            scheduled_time="10:00",
        )
    )

    appointments = appointment_repo.get_by_barbershop(barbershop.id)
    assert len(appointments) == 1


def test_get_by_customer(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    customer = customer_repo.create(
        CustomerCreate(
            name="Customer",
            email="customer@example.com",
            phone="555-1234",
            barbershop_id=barbershop.id,
        )
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(
        BarberCreate(name="Barber", barbershop_id=barbershop.id)
    )

    service_repo = ServiceRepository(db)
    service = service_repo.create(
        ServiceCreate(
            name="Haircut",
            description="Classic",
            price=25.0,
            duration_minutes=30,
            barbershop_id=barbershop.id,
        )
    )

    appointment_repo = AppointmentRepository(db)
    appointment_repo.create(
        AppointmentCreate(
            barbershop_id=barbershop.id,
            customer_id=customer.id,
            barber_id=barber.id,
            service_id=service.id,
            scheduled_date=datetime(2024, 1, 1, 10, 0),
            scheduled_time="10:00",
        )
    )

    appointments = appointment_repo.get_by_customer(customer.id)
    assert len(appointments) == 1


def test_get_by_barber(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    customer = customer_repo.create(
        CustomerCreate(
            name="Customer",
            email="customer@example.com",
            phone="555-1234",
            barbershop_id=barbershop.id,
        )
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(
        BarberCreate(name="Barber", barbershop_id=barbershop.id)
    )

    service_repo = ServiceRepository(db)
    service = service_repo.create(
        ServiceCreate(
            name="Haircut",
            description="Classic",
            price=25.0,
            duration_minutes=30,
            barbershop_id=barbershop.id,
        )
    )

    appointment_repo = AppointmentRepository(db)
    appointment_repo.create(
        AppointmentCreate(
            barbershop_id=barbershop.id,
            customer_id=customer.id,
            barber_id=barber.id,
            service_id=service.id,
            scheduled_date=datetime(2024, 1, 1, 10, 0),
            scheduled_time="10:00",
        )
    )

    appointments = appointment_repo.get_by_barber(barber.id)
    assert len(appointments) == 1


def test_get_by_barbershop_and_status(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    customer = customer_repo.create(
        CustomerCreate(
            name="Customer",
            email="customer@example.com",
            phone="555-1234",
            barbershop_id=barbershop.id,
        )
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(
        BarberCreate(name="Barber", barbershop_id=barbershop.id)
    )

    service_repo = ServiceRepository(db)
    service = service_repo.create(
        ServiceCreate(
            name="Haircut",
            description="Classic",
            price=25.0,
            duration_minutes=30,
            barbershop_id=barbershop.id,
        )
    )

    appointment_repo = AppointmentRepository(db)
    appointment_repo.create(
        AppointmentCreate(
            barbershop_id=barbershop.id,
            customer_id=customer.id,
            barber_id=barber.id,
            service_id=service.id,
            scheduled_date=datetime(2024, 1, 1, 10, 0),
            scheduled_time="10:00",
            status="confirmed",
        )
    )

    appointments = appointment_repo.get_by_barbershop_and_status(
        barbershop.id, "confirmed"
    )
    assert len(appointments) == 1


def test_update_appointment(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    customer = customer_repo.create(
        CustomerCreate(
            name="Customer",
            email="customer@example.com",
            phone="555-1234",
            barbershop_id=barbershop.id,
        )
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(
        BarberCreate(name="Barber", barbershop_id=barbershop.id)
    )

    service_repo = ServiceRepository(db)
    service = service_repo.create(
        ServiceCreate(
            name="Haircut",
            description="Classic",
            price=25.0,
            duration_minutes=30,
            barbershop_id=barbershop.id,
        )
    )

    appointment_repo = AppointmentRepository(db)
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:00",
    )
    appointment = appointment_repo.create(appointment_data)

    update_data = AppointmentUpdate(
        status="confirmed",
        notes="Updated notes",
    )
    updated = appointment_repo.update(appointment.id, update_data)

    assert updated is not None
    assert updated.status == "confirmed"
    assert updated.notes == "Updated notes"


def test_update_appointment_not_found(db):
    appointment_repo = AppointmentRepository(db)
    update_data = AppointmentUpdate(status="confirmed")
    updated = appointment_repo.update(999, update_data)
    assert updated is None


def test_delete_appointment(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    customer = customer_repo.create(
        CustomerCreate(
            name="Customer",
            email="customer@example.com",
            phone="555-1234",
            barbershop_id=barbershop.id,
        )
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(
        BarberCreate(name="Barber", barbershop_id=barbershop.id)
    )

    service_repo = ServiceRepository(db)
    service = service_repo.create(
        ServiceCreate(
            name="Haircut",
            description="Classic",
            price=25.0,
            duration_minutes=30,
            barbershop_id=barbershop.id,
        )
    )

    appointment_repo = AppointmentRepository(db)
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:00",
    )
    appointment = appointment_repo.create(appointment_data)

    result = appointment_repo.delete(appointment.id)
    assert result is True

    deleted = appointment_repo.get_by_id(appointment.id)
    assert deleted is None


def test_delete_appointment_not_found(db):
    appointment_repo = AppointmentRepository(db)
    result = appointment_repo.delete(999)
    assert result is False


def test_get_by_date(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    customer = customer_repo.create(
        CustomerCreate(
            name="Customer",
            email="customer@example.com",
            phone="555-1234",
            barbershop_id=barbershop.id,
        )
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(
        BarberCreate(name="Barber", barbershop_id=barbershop.id)
    )

    service_repo = ServiceRepository(db)
    service = service_repo.create(
        ServiceCreate(
            name="Haircut",
            description="Classic",
            price=25.0,
            duration_minutes=30,
            barbershop_id=barbershop.id,
        )
    )

    appointment_repo = AppointmentRepository(db)
    appointment_date = datetime(2024, 1, 1, 10, 0)
    appointment_repo.create(
        AppointmentCreate(
            barbershop_id=barbershop.id,
            customer_id=customer.id,
            barber_id=barber.id,
            service_id=service.id,
            scheduled_date=appointment_date,
            scheduled_time="10:00",
        )
    )

    # Use the date in ISO format (YYYY-MM-DD)
    date_str = appointment_date.strftime("%Y-%m-%d")
    appointments = appointment_repo.get_by_date(date_str, barbershop.id)
    assert len(appointments) == 1


def test_repository_implements_interface():
    assert issubclass(AppointmentRepository, IAppointmentRepository)
