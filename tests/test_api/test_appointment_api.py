import pytest
from fastapi.testclient import TestClient
from app.repositories.user_repository import UserRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.barber_repository import BarberRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.appointment_repository import AppointmentRepository
from app.schemas.user import UserCreate
from app.schemas.barbershop import BarberShopCreate
from app.schemas.customer import CustomerCreate
from app.schemas.barber import BarberCreate
from app.schemas.service import ServiceCreate
from app.schemas.appointment import AppointmentCreate
from datetime import datetime


def test_create_appointment(client, db):
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

    appointment_data = {
        "barbershop_id": barbershop.id,
        "customer_id": customer.id,
        "barber_id": barber.id,
        "service_id": service.id,
        "scheduled_date": "2024-01-01T10:00:00",
        "scheduled_time": "10:00",
        "status": "pending",
    }

    response = client.post("/api/appointments/", json=appointment_data)
    assert response.status_code == 201

    data = response.json()
    assert data["status"] == "pending"


def test_create_appointment_invalid_barbershop(client, db):
    appointment_data = {
        "barbershop_id": 999,
        "customer_id": 1,
        "barber_id": 1,
        "service_id": 1,
        "scheduled_date": "2024-01-01T10:00:00",
        "scheduled_time": "10:00",
    }

    response = client.post("/api/appointments/", json=appointment_data)
    assert response.status_code == 404
    assert "Barbershop not found" in response.json()["detail"]


def test_get_appointment(client, db):
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

    response = client.get(f"/api/appointments/{appointment.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == appointment.id


def test_get_appointment_not_found(client, db):
    response = client.get("/api/appointments/999")
    assert response.status_code == 404
    assert "Appointment not found" in response.json()["detail"]


def test_get_barbershop_appointments(client, db):
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

    response = client.get(f"/api/appointments/barbershop/{barbershop.id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1


def test_get_barbershop_appointments_with_status(client, db):
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

    response = client.get(
        f"/api/appointments/barbershop/{barbershop.id}?status=confirmed"
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["status"] == "confirmed"


def test_get_customer_appointments(client, db):
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

    response = client.get(f"/api/appointments/customer/{customer.id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1


def test_get_customer_appointments_not_found(client, db):
    response = client.get("/api/appointments/customer/999")
    assert response.status_code == 404
    assert "Customer not found" in response.json()["detail"]


def test_get_barber_appointments(client, db):
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

    response = client.get(f"/api/appointments/barber/{barber.id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1


def test_get_barber_appointments_not_found(client, db):
    response = client.get("/api/appointments/barber/999")
    assert response.status_code == 404
    assert "Barber not found" in response.json()["detail"]


def test_update_appointment(client, db):
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

    update_data = {"status": "confirmed"}

    response = client.put(f"/api/appointments/{appointment.id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "confirmed"


def test_update_appointment_invalid_status(client, db):
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

    update_data = {"status": "invalid_status"}

    response = client.put(f"/api/appointments/{appointment.id}", json=update_data)
    assert response.status_code == 400
    assert "Invalid status" in response.json()["detail"]


def test_update_appointment_not_found(client, db):
    update_data = {"status": "confirmed"}

    response = client.put("/api/appointments/999", json=update_data)
    assert response.status_code == 404
    assert "Appointment not found" in response.json()["detail"]


def test_delete_appointment(client, db):
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

    response = client.delete(f"/api/appointments/{appointment.id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


def test_delete_appointment_not_found(client, db):
    response = client.delete("/api/appointments/999")
    assert response.status_code == 404
    assert "Appointment not found" in response.json()["detail"]
