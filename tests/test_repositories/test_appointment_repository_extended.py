"""Extended tests for AppointmentRepository with validation features."""
import pytest
from datetime import datetime, date

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


def create_test_appointment(db, scheduled_date, scheduled_time, status="pending"):
    """Helper to create test appointment data."""
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@test.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    customer = customer_repo.create(
        CustomerCreate(
            name="Customer",
            email="customer@test.com",
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
        scheduled_date=scheduled_date,
        scheduled_time=scheduled_time,
        status=status,
    )
    appointment = appointment_repo.create(appointment_data)

    return appointment, barber, barbershop


class TestGetByBarberAndDate:
    """Tests for get_by_barber_and_date method."""

    def test_get_by_barber_and_date_existing(self, db):
        """Test retrieving appointments by barber and date."""
        appointment, barber, _ = create_test_appointment(
            db, datetime(2024, 1, 15, 10, 0), "10:00"
        )

        appointment_repo = AppointmentRepository(db)
        results = appointment_repo.get_by_barber_and_date(
            barber.id, date(2024, 1, 15)
        )

        assert len(results) == 1
        assert results[0].id == appointment.id

    def test_get_by_barber_and_date_no_results(self, db):
        """Test retrieving appointments with no matches."""
        appointment, barber, _ = create_test_appointment(
            db, datetime(2024, 1, 15, 10, 0), "10:00"
        )

        appointment_repo = AppointmentRepository(db)
        results = appointment_repo.get_by_barber_and_date(
            barber.id, date(2024, 1, 16)  # Different date
        )

        assert len(results) == 0

    def test_get_by_barber_and_date_excludes_cancelled(self, db):
        """Test that cancelled appointments are excluded."""
        appointment, barber, _ = create_test_appointment(
            db, datetime(2024, 1, 15, 10, 0), "10:00", status="cancelled"
        )

        appointment_repo = AppointmentRepository(db)
        results = appointment_repo.get_by_barber_and_date(
            barber.id, date(2024, 1, 15)
        )

        assert len(results) == 0

    def test_get_by_barber_and_date_excludes_no_show(self, db):
        """Test that no_show appointments are excluded."""
        appointment, barber, _ = create_test_appointment(
            db, datetime(2024, 1, 15, 10, 0), "10:00", status="no_show"
        )

        appointment_repo = AppointmentRepository(db)
        results = appointment_repo.get_by_barber_and_date(
            barber.id, date(2024, 1, 15)
        )

        assert len(results) == 0

    def test_get_by_barber_and_date_includes_confirmed(self, db):
        """Test that confirmed appointments are included."""
        appointment, barber, _ = create_test_appointment(
            db, datetime(2024, 1, 15, 10, 0), "10:00", status="confirmed"
        )

        appointment_repo = AppointmentRepository(db)
        results = appointment_repo.get_by_barber_and_date(
            barber.id, date(2024, 1, 15)
        )

        assert len(results) == 1


class TestHasConflictingAppointment:
    """Tests for has_conflicting_appointment method."""

    def test_no_conflict_empty_schedule(self, db):
        """Test no conflict when no appointments exist."""
        _, barber, _ = create_test_appointment(
            db, datetime(2024, 1, 15, 10, 0), "10:00"
        )

        appointment_repo = AppointmentRepository(db)
        # Delete the appointment to have empty schedule
        appointments = appointment_repo.get_by_barber(barber.id)
        for appt in appointments:
            appointment_repo.delete(appt.id)

        has_conflict = appointment_repo.has_conflicting_appointment(
            barber_id=barber.id,
            date=date(2024, 1, 15),
            start_time="10:00",
            end_time="10:30",
        )

        assert has_conflict is False

    def test_conflict_same_time(self, db):
        """Test conflict with same start time."""
        _, barber, _ = create_test_appointment(
            db, datetime(2024, 1, 15, 10, 0), "10:00"
        )

        appointment_repo = AppointmentRepository(db)
        has_conflict = appointment_repo.has_conflicting_appointment(
            barber_id=barber.id,
            date=date(2024, 1, 15),
            start_time="10:00",
            end_time="10:30",
        )

        assert has_conflict is True

    def test_conflict_overlapping(self, db):
        """Test conflict with overlapping time."""
        _, barber, _ = create_test_appointment(
            db, datetime(2024, 1, 15, 10, 0), "10:00"  # Ends at 10:30
        )

        appointment_repo = AppointmentRepository(db)
        # New appointment starts at 10:15 (overlaps)
        has_conflict = appointment_repo.has_conflicting_appointment(
            barber_id=barber.id,
            date=date(2024, 1, 15),
            start_time="10:15",
            end_time="10:45",
        )

        assert has_conflict is True

    def test_no_conflict_different_times(self, db):
        """Test no conflict when times don't overlap."""
        _, barber, _ = create_test_appointment(
            db, datetime(2024, 1, 15, 10, 0), "10:00"  # Ends at 10:30
        )

        appointment_repo = AppointmentRepository(db)
        # New appointment starts at 11:00 (no overlap)
        has_conflict = appointment_repo.has_conflicting_appointment(
            barber_id=barber.id,
            date=date(2024, 1, 15),
            start_time="11:00",
            end_time="11:30",
        )

        assert has_conflict is False

    def test_no_conflict_different_barber(self, db):
        """Test no conflict with different barber."""
        _, barber, _ = create_test_appointment(
            db, datetime(2024, 1, 15, 10, 0), "10:00"
        )

        appointment_repo = AppointmentRepository(db)
        # Different barber id
        has_conflict = appointment_repo.has_conflicting_appointment(
            barber_id=99999,  # Different barber
            date=date(2024, 1, 15),
            start_time="10:00",
            end_time="10:30",
        )

        assert has_conflict is False

    def test_no_conflict_different_date(self, db):
        """Test no conflict on different date."""
        _, barber, _ = create_test_appointment(
            db, datetime(2024, 1, 15, 10, 0), "10:00"
        )

        appointment_repo = AppointmentRepository(db)
        # Different date
        has_conflict = appointment_repo.has_conflicting_appointment(
            barber_id=barber.id,
            date=date(2024, 1, 16),  # Different date
            start_time="10:00",
            end_time="10:30",
        )

        assert has_conflict is False

    def test_no_conflict_cancelled_appointment(self, db):
        """Test that cancelled appointments don't cause conflict."""
        _, barber, _ = create_test_appointment(
            db, datetime(2024, 1, 15, 10, 0), "10:00", status="cancelled"
        )

        appointment_repo = AppointmentRepository(db)
        has_conflict = appointment_repo.has_conflicting_appointment(
            barber_id=barber.id,
            date=date(2024, 1, 15),
            start_time="10:00",
            end_time="10:30",
        )

        assert has_conflict is False

    def test_no_conflict_no_show_appointment(self, db):
        """Test that no_show appointments don't cause conflict."""
        _, barber, _ = create_test_appointment(
            db, datetime(2024, 1, 15, 10, 0), "10:00", status="no_show"
        )

        appointment_repo = AppointmentRepository(db)
        has_conflict = appointment_repo.has_conflicting_appointment(
            barber_id=barber.id,
            date=date(2024, 1, 15),
            start_time="10:00",
            end_time="10:30",
        )

        assert has_conflict is False

    def test_conflict_with_exclude_id(self, db):
        """Test excluding specific appointment from conflict check."""
        appointment, barber, _ = create_test_appointment(
            db, datetime(2024, 1, 15, 10, 0), "10:00"
        )

        appointment_repo = AppointmentRepository(db)
        # Same time but excluding the existing appointment
        has_conflict = appointment_repo.has_conflicting_appointment(
            barber_id=barber.id,
            date=date(2024, 1, 15),
            start_time="10:00",
            end_time="10:30",
            exclude_id=appointment.id,
        )

        assert has_conflict is False

    def test_add_minutes_to_time_helper(self, db):
        """Test the _add_minutes_to_time helper method."""
        appointment_repo = AppointmentRepository(db)

        result = appointment_repo._add_minutes_to_time("10:00", 30)
        assert result == "10:30"

        result = appointment_repo._add_minutes_to_time("10:30", 30)
        assert result == "11:00"

        result = appointment_repo._add_minutes_to_time("23:30", 45)
        assert result == "00:15"
