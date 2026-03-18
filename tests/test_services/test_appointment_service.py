import pytest
from fastapi import HTTPException
from app.services.appointment_service import AppointmentService
from app.repositories.appointment_repository import AppointmentRepository
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
    barbershop_repo_test = BarberShopRepository(db)
    customer_repo_test = CustomerRepository(db)
    barber_repo_test = BarberRepository(db)
    service_repo_test = ServiceRepository(db)
    appointment_service = AppointmentService(
        appointment_repo,
        barbershop_repo_test,
        customer_repo_test,
        barber_repo_test,
        service_repo_test,
    )

    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:00",
        status="pending",
    )
    appointment = appointment_service.create_appointment(appointment_data)

    assert appointment.status == "pending"


def test_create_appointment_invalid_barbershop(db):
    appointment_repo = AppointmentRepository(db)
    barbershop_repo = BarberShopRepository(db)
    customer_repo = CustomerRepository(db)
    barber_repo = BarberRepository(db)
    service_repo = ServiceRepository(db)
    appointment_service = AppointmentService(
        appointment_repo, barbershop_repo, customer_repo, barber_repo, service_repo
    )

    appointment_data = AppointmentCreate(
        barbershop_id=999,
        customer_id=1,
        barber_id=1,
        service_id=1,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(appointment_data)

    assert exc_info.value.status_code == 404
    assert "Barbershop not found" in exc_info.value.detail


def test_create_appointment_invalid_customer(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    appointment_repo = AppointmentRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    customer_repo = CustomerRepository(db)
    barber_repo = BarberRepository(db)
    service_repo = ServiceRepository(db)
    appointment_service = AppointmentService(
        appointment_repo, barbershop_repo_test, customer_repo, barber_repo, service_repo
    )

    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=999,
        barber_id=1,
        service_id=1,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(appointment_data)

    assert exc_info.value.status_code == 404
    assert "Customer not found" in exc_info.value.detail


def test_create_appointment_invalid_barber(db):
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
    barbershop_repo_test = BarberShopRepository(db)
    customer_repo_test = CustomerRepository(db)
    barber_repo = BarberRepository(db)
    service_repo_test = ServiceRepository(db)
    appointment_service = AppointmentService(
        appointment_repo,
        barbershop_repo_test,
        customer_repo_test,
        barber_repo,
        service_repo_test,
    )

    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=999,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(appointment_data)

    assert exc_info.value.status_code == 404
    assert "Barber not found" in exc_info.value.detail


def test_create_appointment_invalid_service(db):
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

    appointment_repo = AppointmentRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    customer_repo_test = CustomerRepository(db)
    barber_repo_test = BarberRepository(db)
    service_repo = ServiceRepository(db)
    appointment_service = AppointmentService(
        appointment_repo,
        barbershop_repo_test,
        customer_repo_test,
        barber_repo_test,
        service_repo,
    )

    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=999,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(appointment_data)

    assert exc_info.value.status_code == 404
    assert "Service not found" in exc_info.value.detail


def test_create_appointment_barber_wrong_barbershop(db):
    user_repo = UserRepository(db)
    owner1 = user_repo.create(
        UserCreate(email="owner1@example.com", full_name="Owner1", password="pass")
    )
    owner2 = user_repo.create(
        UserCreate(email="owner2@example.com", full_name="Owner2", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop1 = barbershop_repo.create(
        BarberShopCreate(name="Shop1", address="123", phone="123", owner_id=owner1.id)
    )
    barbershop2 = barbershop_repo.create(
        BarberShopCreate(name="Shop2", address="456", phone="456", owner_id=owner2.id)
    )

    customer_repo = CustomerRepository(db)
    customer = customer_repo.create(
        CustomerCreate(
            name="Customer",
            email="customer@example.com",
            phone="555-1234",
            barbershop_id=barbershop1.id,
        )
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(
        BarberCreate(name="Barber", barbershop_id=barbershop2.id)
    )

    service_repo = ServiceRepository(db)
    service = service_repo.create(
        ServiceCreate(
            name="Haircut",
            description="Classic",
            price=25.0,
            duration_minutes=30,
            barbershop_id=barbershop1.id,
        )
    )

    appointment_repo = AppointmentRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    customer_repo_test = CustomerRepository(db)
    barber_repo_test = BarberRepository(db)
    service_repo_test = ServiceRepository(db)
    appointment_service = AppointmentService(
        appointment_repo,
        barbershop_repo_test,
        customer_repo_test,
        barber_repo_test,
        service_repo_test,
    )

    appointment_data = AppointmentCreate(
        barbershop_id=barbershop1.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(appointment_data)

    assert exc_info.value.status_code == 400
    assert "does not belong to this barbershop" in exc_info.value.detail


def test_create_appointment_service_wrong_barbershop(db):
    user_repo = UserRepository(db)
    owner1 = user_repo.create(
        UserCreate(email="owner1@example.com", full_name="Owner1", password="pass")
    )
    owner2 = user_repo.create(
        UserCreate(email="owner2@example.com", full_name="Owner2", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop1 = barbershop_repo.create(
        BarberShopCreate(name="Shop1", address="123", phone="123", owner_id=owner1.id)
    )
    barbershop2 = barbershop_repo.create(
        BarberShopCreate(name="Shop2", address="456", phone="456", owner_id=owner2.id)
    )

    customer_repo = CustomerRepository(db)
    customer = customer_repo.create(
        CustomerCreate(
            name="Customer",
            email="customer@example.com",
            phone="555-1234",
            barbershop_id=barbershop1.id,
        )
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(
        BarberCreate(name="Barber", barbershop_id=barbershop1.id)
    )

    service_repo = ServiceRepository(db)
    service = service_repo.create(
        ServiceCreate(
            name="Haircut",
            description="Classic",
            price=25.0,
            duration_minutes=30,
            barbershop_id=barbershop2.id,
        )
    )

    appointment_repo = AppointmentRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    customer_repo_test = CustomerRepository(db)
    barber_repo_test = BarberRepository(db)
    service_repo_test = ServiceRepository(db)
    appointment_service = AppointmentService(
        appointment_repo,
        barbershop_repo_test,
        customer_repo_test,
        barber_repo_test,
        service_repo_test,
    )

    appointment_data = AppointmentCreate(
        barbershop_id=barbershop1.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(appointment_data)

    assert exc_info.value.status_code == 400
    assert "does not belong to this barbershop" in exc_info.value.detail


def test_get_appointment(db):
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

    barbershop_repo_test = BarberShopRepository(db)
    customer_repo_test = CustomerRepository(db)
    barber_repo_test = BarberRepository(db)
    service_repo_test = ServiceRepository(db)
    appointment_service = AppointmentService(
        appointment_repo,
        barbershop_repo_test,
        customer_repo_test,
        barber_repo_test,
        service_repo_test,
    )

    retrieved = appointment_service.get_appointment(appointment.id)
    assert retrieved.id == appointment.id


def test_get_appointment_not_found(db):
    appointment_repo = AppointmentRepository(db)
    barbershop_repo = BarberShopRepository(db)
    customer_repo = CustomerRepository(db)
    barber_repo = BarberRepository(db)
    service_repo = ServiceRepository(db)
    appointment_service = AppointmentService(
        appointment_repo, barbershop_repo, customer_repo, barber_repo, service_repo
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.get_appointment(999)

    assert exc_info.value.status_code == 404
    assert "Appointment not found" in exc_info.value.detail


def test_get_barbershop_appointments(db):
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
    barbershop_repo_test = BarberShopRepository(db)
    customer_repo_test = CustomerRepository(db)
    barber_repo_test = BarberRepository(db)
    service_repo_test = ServiceRepository(db)
    appointment_service = AppointmentService(
        appointment_repo,
        barbershop_repo_test,
        customer_repo_test,
        barber_repo_test,
        service_repo_test,
    )

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

    appointments = appointment_service.get_barbershop_appointments(barbershop.id)
    assert len(appointments) == 1


def test_get_barbershop_appointments_invalid_barbershop(db):
    appointment_repo = AppointmentRepository(db)
    barbershop_repo = BarberShopRepository(db)
    customer_repo = CustomerRepository(db)
    barber_repo = BarberRepository(db)
    service_repo = ServiceRepository(db)
    appointment_service = AppointmentService(
        appointment_repo, barbershop_repo, customer_repo, barber_repo, service_repo
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.get_barbershop_appointments(999)

    assert exc_info.value.status_code == 404
    assert "Barbershop not found" in exc_info.value.detail


def test_get_barbershop_appointments_with_status(db):
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
    barbershop_repo_test = BarberShopRepository(db)
    customer_repo_test = CustomerRepository(db)
    barber_repo_test = BarberRepository(db)
    service_repo_test = ServiceRepository(db)
    appointment_service = AppointmentService(
        appointment_repo,
        barbershop_repo_test,
        customer_repo_test,
        barber_repo_test,
        service_repo_test,
    )

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

    appointments = appointment_service.get_barbershop_appointments(
        barbershop.id, "confirmed"
    )
    assert len(appointments) == 1
    assert appointments[0].status == "confirmed"


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

    barbershop_repo_test = BarberShopRepository(db)
    customer_repo_test = CustomerRepository(db)
    barber_repo_test = BarberRepository(db)
    service_repo_test = ServiceRepository(db)
    appointment_service = AppointmentService(
        appointment_repo,
        barbershop_repo_test,
        customer_repo_test,
        barber_repo_test,
        service_repo_test,
    )

    update_data = AppointmentUpdate(status="confirmed")
    updated = appointment_service.update_appointment(appointment.id, update_data)

    assert updated.status == "confirmed"


def test_update_appointment_invalid_status(db):
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

    barbershop_repo_test = BarberShopRepository(db)
    customer_repo_test = CustomerRepository(db)
    barber_repo_test = BarberRepository(db)
    service_repo_test = ServiceRepository(db)
    appointment_service = AppointmentService(
        appointment_repo,
        barbershop_repo_test,
        customer_repo_test,
        barber_repo_test,
        service_repo_test,
    )

    update_data = AppointmentUpdate(status="invalid_status")

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.update_appointment(appointment.id, update_data)

    assert exc_info.value.status_code == 400
    assert "Invalid status" in exc_info.value.detail


def test_update_appointment_not_found(db):
    appointment_repo = AppointmentRepository(db)
    barbershop_repo = BarberShopRepository(db)
    customer_repo = CustomerRepository(db)
    barber_repo = BarberRepository(db)
    service_repo = ServiceRepository(db)
    appointment_service = AppointmentService(
        appointment_repo, barbershop_repo, customer_repo, barber_repo, service_repo
    )

    update_data = AppointmentUpdate(status="confirmed")

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.update_appointment(999, update_data)

    assert exc_info.value.status_code == 404
    assert "Appointment not found" in exc_info.value.detail


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

    barbershop_repo_test = BarberShopRepository(db)
    customer_repo_test = CustomerRepository(db)
    barber_repo_test = BarberRepository(db)
    service_repo_test = ServiceRepository(db)
    appointment_service = AppointmentService(
        appointment_repo,
        barbershop_repo_test,
        customer_repo_test,
        barber_repo_test,
        service_repo_test,
    )

    result = appointment_service.delete_appointment(appointment.id)
    assert result is True


def test_delete_appointment_not_found(db):
    appointment_repo = AppointmentRepository(db)
    barbershop_repo = BarberShopRepository(db)
    customer_repo = CustomerRepository(db)
    barber_repo = BarberRepository(db)
    service_repo = ServiceRepository(db)
    appointment_service = AppointmentService(
        appointment_repo, barbershop_repo, customer_repo, barber_repo, service_repo
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.delete_appointment(999)

    assert exc_info.value.status_code == 404
    assert "Appointment not found" in exc_info.value.detail
