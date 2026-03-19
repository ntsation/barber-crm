"""Tests for appointment time constraints validation."""
import pytest
from fastapi import HTTPException
from datetime import datetime, timedelta

from app.services.appointment_service import AppointmentService
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.barber_repository import BarberRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.user_repository import UserRepository
from app.schemas.appointment import AppointmentCreate
from app.schemas.user import UserCreate
from app.schemas.barbershop import BarberShopCreate
from app.schemas.customer import CustomerCreate
from app.schemas.barber import BarberCreate
from app.schemas.service import ServiceCreate


def create_test_data(db):
    """Helper to create test data."""
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

    return barbershop, customer, barber, service


def get_service(db):
    """Helper to create service with all dependencies."""
    return AppointmentService(
        appointment_repo=AppointmentRepository(db),
        barbershop_repo=BarberShopRepository(db),
        customer_repo=CustomerRepository(db),
        barber_repo=BarberRepository(db),
        service_repo=ServiceRepository(db),
    )


class TestMinimumAdvanceNotice:
    """Tests for minimum advance notice (1 hour)."""

    def test_appointment_less_than_1_hour_advance(self, db):
        """Test that appointment cannot be scheduled less than 1 hour in advance."""
        barbershop, customer, barber, service = create_test_data(db)
        appointment_service = get_service(db)

        # Schedule 30 minutes from now (should fail)
        appointment_time = datetime.now() + timedelta(minutes=30)
        
        appointment_data = AppointmentCreate(
            barbershop_id=barbershop.id,
            customer_id=customer.id,
            barber_id=barber.id,
            service_id=service.id,
            scheduled_date=appointment_time,
            scheduled_time=appointment_time.strftime("%H:%M"),
        )

        with pytest.raises(HTTPException) as exc_info:
            appointment_service.create_appointment(appointment_data)

        assert exc_info.value.status_code == 400
        assert "at least 1 hour in advance" in exc_info.value.detail

    def test_appointment_exactly_1_hour_advance(self, db):
        """Test that appointment can be scheduled exactly 1 hour in advance."""
        barbershop, customer, barber, service = create_test_data(db)
        appointment_service = get_service(db)

        # Schedule exactly 1 hour from now (should pass)
        appointment_time = datetime.now() + timedelta(hours=1, minutes=1)
        
        appointment_data = AppointmentCreate(
            barbershop_id=barbershop.id,
            customer_id=customer.id,
            barber_id=barber.id,
            service_id=service.id,
            scheduled_date=appointment_time,
            scheduled_time=appointment_time.strftime("%H:%M"),
        )

        appointment = appointment_service.create_appointment(appointment_data)
        assert appointment.status == "pending"

    def test_appointment_more_than_1_hour_advance(self, db):
        """Test that appointment can be scheduled more than 1 hour in advance."""
        barbershop, customer, barber, service = create_test_data(db)
        appointment_service = get_service(db)

        # Schedule 2 hours from now (should pass)
        appointment_time = datetime.now() + timedelta(hours=2)
        
        appointment_data = AppointmentCreate(
            barbershop_id=barbershop.id,
            customer_id=customer.id,
            barber_id=barber.id,
            service_id=service.id,
            scheduled_date=appointment_time,
            scheduled_time=appointment_time.strftime("%H:%M"),
        )

        appointment = appointment_service.create_appointment(appointment_data)
        assert appointment.status == "pending"


class TestMaximumAdvanceNotice:
    """Tests for maximum advance notice (30 days)."""

    def test_appointment_more_than_30_days_advance(self, db):
        """Test that appointment cannot be scheduled more than 30 days in advance."""
        barbershop, customer, barber, service = create_test_data(db)
        appointment_service = get_service(db)

        # Schedule 31 days from now (should fail)
        appointment_time = datetime.now() + timedelta(days=31)
        
        appointment_data = AppointmentCreate(
            barbershop_id=barbershop.id,
            customer_id=customer.id,
            barber_id=barber.id,
            service_id=service.id,
            scheduled_date=appointment_time,
            scheduled_time=appointment_time.strftime("%H:%M"),
        )

        with pytest.raises(HTTPException) as exc_info:
            appointment_service.create_appointment(appointment_data)

        assert exc_info.value.status_code == 400
        assert "more than 30 days in advance" in exc_info.value.detail

    def test_appointment_exactly_30_days_advance(self, db):
        """Test that appointment can be scheduled exactly 30 days in advance."""
        barbershop, customer, barber, service = create_test_data(db)
        appointment_service = get_service(db)

        # Schedule 29 days and 23 hours from now (should pass - within 30 days)
        appointment_time = datetime.now() + timedelta(days=29, hours=23)
        
        appointment_data = AppointmentCreate(
            barbershop_id=barbershop.id,
            customer_id=customer.id,
            barber_id=barber.id,
            service_id=service.id,
            scheduled_date=appointment_time,
            scheduled_time=appointment_time.strftime("%H:%M"),
        )

        appointment = appointment_service.create_appointment(appointment_data)
        assert appointment.status == "pending"

    def test_appointment_within_30_days_advance(self, db):
        """Test that appointment can be scheduled within 30 days."""
        barbershop, customer, barber, service = create_test_data(db)
        appointment_service = get_service(db)

        # Schedule 15 days from now (should pass)
        appointment_time = datetime.now() + timedelta(days=15)
        
        appointment_data = AppointmentCreate(
            barbershop_id=barbershop.id,
            customer_id=customer.id,
            barber_id=barber.id,
            service_id=service.id,
            scheduled_date=appointment_time,
            scheduled_time=appointment_time.strftime("%H:%M"),
        )

        appointment = appointment_service.create_appointment(appointment_data)
        assert appointment.status == "pending"


class TestTimeConstraintsEdgeCases:
    """Tests for edge cases in time constraints."""

    def test_appointment_past_date(self, db):
        """Test that appointment cannot be scheduled in the past."""
        barbershop, customer, barber, service = create_test_data(db)
        appointment_service = get_service(db)

        # Schedule 1 day in the past (should fail - less than 1 hour advance)
        appointment_time = datetime.now() - timedelta(days=1)
        
        appointment_data = AppointmentCreate(
            barbershop_id=barbershop.id,
            customer_id=customer.id,
            barber_id=barber.id,
            service_id=service.id,
            scheduled_date=appointment_time,
            scheduled_time=appointment_time.strftime("%H:%M"),
        )

        with pytest.raises(HTTPException) as exc_info:
            appointment_service.create_appointment(appointment_data)

        assert exc_info.value.status_code == 400
        assert "at least 1 hour in advance" in exc_info.value.detail

    def test_appointment_valid_time_window(self, db):
        """Test that appointment can be scheduled within valid time window."""
        barbershop, customer, barber, service = create_test_data(db)
        appointment_service = get_service(db)

        # Schedule 12 hours from now (should pass - between 1 hour and 30 days)
        appointment_time = datetime.now() + timedelta(hours=12)
        
        appointment_data = AppointmentCreate(
            barbershop_id=barbershop.id,
            customer_id=customer.id,
            barber_id=barber.id,
            service_id=service.id,
            scheduled_date=appointment_time,
            scheduled_time=appointment_time.strftime("%H:%M"),
        )

        appointment = appointment_service.create_appointment(appointment_data)
        assert appointment.status == "pending"
