"""Tests for appointment validation features."""
import pytest
from fastapi import HTTPException
from datetime import datetime

from app.services.appointment_service import AppointmentService
from app.repositories.appointment_repository import AppointmentRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.barber_repository import BarberRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.barbershop_schedule_repository import BarberShopScheduleRepository
from app.repositories.barber_schedule_repository import BarberScheduleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.appointment import AppointmentCreate
from app.schemas.user import UserCreate
from app.schemas.barbershop import BarberShopCreate
from app.schemas.customer import CustomerCreate
from app.schemas.barber import BarberCreate
from app.schemas.service import ServiceCreate
from app.schemas.barbershop_schedule import BarberShopScheduleCreate, DaySchedule
from app.schemas.barber_schedule import BarberScheduleCreate


def create_test_data(db, barber_working_days=None, barber_working_hours=None, barber_is_active=True):
    """Helper to create test data with optional barber configurations."""
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
    barber_data = BarberCreate(
        name="Barber",
        barbershop_id=barbershop.id,
        is_active=barber_is_active,
    )
    if barber_working_days:
        barber_data.working_days = barber_working_days
    if barber_working_hours:
        barber_data.working_hours = barber_working_hours
    barber = barber_repo.create(barber_data)

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
        barbershop_schedule_repo=BarberShopScheduleRepository(db),
        barber_schedule_repo=BarberScheduleRepository(db),
    )


# Tests for barber availability validation


def test_create_appointment_inactive_barber(db):
    """Test that appointment cannot be created with inactive barber."""
    barbershop, customer, barber, service = create_test_data(
        db, barber_is_active=False
    )
    appointment_service = get_service(db)

    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),  # Monday
        scheduled_time="10:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(appointment_data)

    assert exc_info.value.status_code == 400
    assert "Barber is not active" in exc_info.value.detail


def test_create_appointment_barber_not_working_day(db):
    """Test that appointment cannot be created on barber's day off."""
    # Barber works only on monday
    barbershop, customer, barber, service = create_test_data(
        db, barber_working_days=["monday"]
    )
    appointment_service = get_service(db)

    # Try to create appointment on tuesday
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 2, 10, 0),  # Tuesday
        scheduled_time="10:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(appointment_data)

    assert exc_info.value.status_code == 400
    assert "Barber does not work on Tuesday" in exc_info.value.detail


def test_create_appointment_barber_outside_working_hours(db):
    """Test that appointment cannot be created outside barber's working hours."""
    # Barber works monday 09:00-17:00
    barbershop, customer, barber, service = create_test_data(
        db,
        barber_working_days=["monday"],
        barber_working_hours={
            "enabled": True,
            "slots": [{"start_time": "09:00", "end_time": "17:00"}]
        }
    )
    appointment_service = get_service(db)

    # Try to create appointment at 18:00 (outside working hours)
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),  # Monday
        scheduled_time="18:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(appointment_data)

    assert exc_info.value.status_code == 400
    assert "outside barber's working hours" in exc_info.value.detail


def test_create_appointment_barber_within_working_hours(db):
    """Test that appointment can be created within barber's working hours."""
    # Barber works monday 09:00-17:00
    barbershop, customer, barber, service = create_test_data(
        db,
        barber_working_days=["monday"],
        barber_working_hours={
            "enabled": True,
            "slots": [{"start_time": "09:00", "end_time": "17:00"}]
        }
    )
    appointment_service = get_service(db)

    # Create appointment at 10:00 (within working hours)
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),  # Monday
        scheduled_time="10:00",
    )

    appointment = appointment_service.create_appointment(appointment_data)
    assert appointment.status == "pending"


# Tests for conflicting appointments


def test_create_appointment_conflict_same_time(db):
    """Test that conflicting appointments cannot be created."""
    barbershop, customer, barber, service = create_test_data(db)
    appointment_service = get_service(db)

    # Create first appointment
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:00",
    )
    appointment_service.create_appointment(appointment_data)

    # Try to create second appointment at same time
    customer2_repo = CustomerRepository(db)
    customer2 = customer2_repo.create(
        CustomerCreate(
            name="Customer2",
            email="customer2@example.com",
            phone="555-5678",
            barbershop_id=barbershop.id,
        )
    )

    conflicting_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer2.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(conflicting_data)

    assert exc_info.value.status_code == 400
    assert "Barber already has an appointment at this time" in exc_info.value.detail


def test_create_appointment_conflict_overlapping(db):
    """Test that overlapping appointments cannot be created."""
    barbershop, customer, barber, service = create_test_data(db)
    appointment_service = get_service(db)

    # Create first appointment at 10:00 (30 min service = ends at 10:30)
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:00",
    )
    appointment_service.create_appointment(appointment_data)

    # Try to create second appointment at 10:15 (overlaps)
    customer2_repo = CustomerRepository(db)
    customer2 = customer2_repo.create(
        CustomerCreate(
            name="Customer2",
            email="customer2@example.com",
            phone="555-5678",
            barbershop_id=barbershop.id,
        )
    )

    overlapping_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer2.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:15",
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(overlapping_data)

    assert exc_info.value.status_code == 400


def test_create_appointment_no_conflict_different_times(db):
    """Test that non-overlapping appointments can be created."""
    barbershop, customer, barber, service = create_test_data(db)
    appointment_service = get_service(db)

    # Create first appointment at 10:00
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:00",
    )
    appointment_service.create_appointment(appointment_data)

    # Create second appointment at 11:00 (no overlap)
    customer2_repo = CustomerRepository(db)
    customer2 = customer2_repo.create(
        CustomerCreate(
            name="Customer2",
            email="customer2@example.com",
            phone="555-5678",
            barbershop_id=barbershop.id,
        )
    )

    non_conflicting_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer2.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="11:00",
    )

    appointment2 = appointment_service.create_appointment(non_conflicting_data)
    assert appointment2.status == "pending"


def test_create_appointment_no_conflict_cancelled_appointment(db):
    """Test that cancelled appointments don't block new ones."""
    barbershop, customer, barber, service = create_test_data(db)
    appointment_repo = AppointmentRepository(db)
    appointment_service = get_service(db)

    # Create first appointment
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:00",
        status="cancelled",
    )
    appointment_repo.create(appointment_data)

    # Create second appointment at same time (should work because first is cancelled)
    customer2_repo = CustomerRepository(db)
    customer2 = customer2_repo.create(
        CustomerCreate(
            name="Customer2",
            email="customer2@example.com",
            phone="555-5678",
            barbershop_id=barbershop.id,
        )
    )

    new_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer2.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),
        scheduled_time="10:00",
    )

    appointment2 = appointment_service.create_appointment(new_data)
    assert appointment2.status == "pending"


# Tests for barbershop schedule validation


def test_create_appointment_barbershop_closed(db):
    """Test that appointment cannot be created when barbershop is closed."""
    barbershop, customer, barber, service = create_test_data(db)
    appointment_service = get_service(db)

    # Create barbershop schedule with sunday disabled
    schedule_repo = BarberShopScheduleRepository(db)
    schedule_repo.create(
        BarberShopScheduleCreate(
            barbershop_id=barbershop.id,
            monday=DaySchedule(enabled=True, start_time="09:00", end_time="18:00"),
            tuesday=DaySchedule(enabled=True, start_time="09:00", end_time="18:00"),
            wednesday=DaySchedule(enabled=True, start_time="09:00", end_time="18:00"),
            thursday=DaySchedule(enabled=True, start_time="09:00", end_time="18:00"),
            friday=DaySchedule(enabled=True, start_time="09:00", end_time="18:00"),
            saturday=DaySchedule(enabled=True, start_time="09:00", end_time="18:00"),
            sunday=DaySchedule(enabled=False),  # Closed on sunday
        )
    )

    # Try to create appointment on sunday
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 7, 10, 0),  # Sunday
        scheduled_time="10:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(appointment_data)

    assert exc_info.value.status_code == 400
    assert "Barbershop is closed on Sunday" in exc_info.value.detail


def test_create_appointment_outside_barbershop_hours(db):
    """Test that appointment cannot be created outside barbershop hours."""
    barbershop, customer, barber, service = create_test_data(db)
    appointment_service = get_service(db)

    # Create barbershop schedule
    schedule_repo = BarberShopScheduleRepository(db)
    schedule_repo.create(
        BarberShopScheduleCreate(
            barbershop_id=barbershop.id,
            monday=DaySchedule(enabled=True, start_time="09:00", end_time="18:00"),
        )
    )

    # Try to create appointment before opening
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),  # Monday
        scheduled_time="08:00",  # Before opening
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(appointment_data)

    assert exc_info.value.status_code == 400
    assert "outside barbershop opening hours" in exc_info.value.detail


def test_create_appointment_within_barbershop_hours(db):
    """Test that appointment can be created within barbershop hours."""
    barbershop, customer, barber, service = create_test_data(db)
    appointment_service = get_service(db)

    # Create barbershop schedule
    schedule_repo = BarberShopScheduleRepository(db)
    schedule_repo.create(
        BarberShopScheduleCreate(
            barbershop_id=barbershop.id,
            monday=DaySchedule(enabled=True, start_time="09:00", end_time="18:00"),
        )
    )

    # Create appointment within hours
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),  # Monday
        scheduled_time="10:00",
    )

    appointment = appointment_service.create_appointment(appointment_data)
    assert appointment.status == "pending"


def test_create_appointment_during_break_time(db):
    """Test that appointment cannot be created during barbershop break."""
    barbershop, customer, barber, service = create_test_data(db)
    appointment_service = get_service(db)

    # Create barbershop schedule with lunch break 12:00-13:00
    schedule_repo = BarberShopScheduleRepository(db)
    schedule_repo.create(
        BarberShopScheduleCreate(
            barbershop_id=barbershop.id,
            monday=DaySchedule(
                enabled=True,
                start_time="09:00",
                end_time="18:00",
                break_start="12:00",
                break_end="13:00",
            ),
        )
    )

    # Try to create appointment during lunch break
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),  # Monday
        scheduled_time="12:15",
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(appointment_data)

    assert exc_info.value.status_code == 400
    assert "overlaps with barbershop break time" in exc_info.value.detail


# Tests for barber schedule table integration


def test_create_appointment_barber_schedule_not_available(db):
    """Test that appointment respects barber_schedule table availability."""
    barbershop, customer, barber, service = create_test_data(db)
    appointment_service = get_service(db)

    # Create barber schedule marking monday as unavailable
    barber_schedule_repo = BarberScheduleRepository(db)
    barber_schedule_repo.create(
        BarberScheduleCreate(
            barber_id=barber.id,
            day_of_week=0,  # Monday
            start_time="09:00",
            end_time="18:00",
            is_available=False,
        )
    )

    # Try to create appointment on monday
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),  # Monday
        scheduled_time="10:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(appointment_data)

    assert exc_info.value.status_code == 400
    assert "Barber is not available at this time" in exc_info.value.detail


def test_create_appointment_barber_schedule_outside_hours(db):
    """Test that appointment respects barber_schedule table hours."""
    barbershop, customer, barber, service = create_test_data(db)
    appointment_service = get_service(db)

    # Create barber schedule with limited hours
    barber_schedule_repo = BarberScheduleRepository(db)
    barber_schedule_repo.create(
        BarberScheduleCreate(
            barber_id=barber.id,
            day_of_week=0,  # Monday
            start_time="09:00",
            end_time="12:00",
            is_available=True,
        )
    )

    # Try to create appointment after barber's schedule ends
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),  # Monday
        scheduled_time="14:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(appointment_data)

    assert exc_info.value.status_code == 400
    assert "outside barber's schedule" in exc_info.value.detail


def test_create_appointment_barber_schedule_valid(db):
    """Test that appointment works when barber_schedule is valid."""
    barbershop, customer, barber, service = create_test_data(db)
    appointment_service = get_service(db)

    # Create barber schedule
    barber_schedule_repo = BarberScheduleRepository(db)
    barber_schedule_repo.create(
        BarberScheduleCreate(
            barber_id=barber.id,
            day_of_week=0,  # Monday
            start_time="09:00",
            end_time="18:00",
            is_available=True,
        )
    )

    # Create appointment within schedule
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),  # Monday
        scheduled_time="10:00",
    )

    appointment = appointment_service.create_appointment(appointment_data)
    assert appointment.status == "pending"


def test_create_appointment_barbershop_schedule_day_not_defined(db):
    """Test when barbershop schedule has no entry for the day (day_schedule is None)."""
    barbershop, customer, barber, service = create_test_data(db)
    appointment_service = get_service(db)

    # Create barbershop schedule with only monday defined
    schedule_repo = BarberShopScheduleRepository(db)
    schedule_repo.create(
        BarberShopScheduleCreate(
            barbershop_id=barbershop.id,
            monday=DaySchedule(enabled=True, start_time="09:00", end_time="18:00"),
        )
    )

    # Try to create appointment on tuesday (not defined in schedule)
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 2, 10, 0),  # Tuesday
        scheduled_time="10:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(appointment_data)

    assert exc_info.value.status_code == 400
    assert "Barbershop is closed on Tuesday" in exc_info.value.detail


def test_create_appointment_barbershop_schedule_no_hours_defined(db):
    """Test when barbershop schedule has no start/end times defined."""
    barbershop, customer, barber, service = create_test_data(db)
    appointment_service = get_service(db)

    # Create barbershop schedule with enabled day but no times
    schedule_repo = BarberShopScheduleRepository(db)
    schedule_repo.create(
        BarberShopScheduleCreate(
            barbershop_id=barbershop.id,
            monday=DaySchedule(enabled=True),  # No start_time or end_time
        )
    )

    # Try to create appointment on monday
    appointment_data = AppointmentCreate(
        barbershop_id=barbershop.id,
        customer_id=customer.id,
        barber_id=barber.id,
        service_id=service.id,
        scheduled_date=datetime(2024, 1, 1, 10, 0),  # Monday
        scheduled_time="10:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        appointment_service.create_appointment(appointment_data)

    assert exc_info.value.status_code == 400
    assert "Barbershop schedule not defined for Monday" in exc_info.value.detail
