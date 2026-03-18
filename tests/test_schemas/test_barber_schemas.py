"""Tests for Barber schema validations."""
import pytest
from pydantic import ValidationError

from app.schemas.barber import WorkingHoursSlot, WorkingDaySchedule, BarberCreate


class TestWorkingHoursSlot:
    """Tests for WorkingHoursSlot schema."""

    def test_valid_time_format(self):
        """Test valid time format HH:MM."""
        slot = WorkingHoursSlot(start_time="09:00", end_time="17:00")
        assert slot.start_time == "09:00"
        assert slot.end_time == "17:00"

    def test_valid_time_format_variations(self):
        """Test various valid time formats."""
        # Single digit hour
        slot = WorkingHoursSlot(start_time="9:00", end_time="17:30")
        assert slot.start_time == "9:00"

        # Midnight
        slot = WorkingHoursSlot(start_time="00:00", end_time="23:59")
        assert slot.start_time == "00:00"

    def test_invalid_time_format_missing_colon(self):
        """Test invalid time format without colon."""
        with pytest.raises(ValidationError) as exc_info:
            WorkingHoursSlot(start_time="0900", end_time="17:00")
        assert "Time must be in HH:MM format" in str(exc_info.value)

    def test_invalid_time_format_wrong_separator(self):
        """Test invalid time format with wrong separator."""
        with pytest.raises(ValidationError) as exc_info:
            WorkingHoursSlot(start_time="09-00", end_time="17:00")
        assert "Time must be in HH:MM format" in str(exc_info.value)

    def test_invalid_time_format_hours_too_high(self):
        """Test invalid time with hours > 23."""
        with pytest.raises(ValidationError) as exc_info:
            WorkingHoursSlot(start_time="25:00", end_time="17:00")
        assert "Time must be in HH:MM format" in str(exc_info.value)

    def test_invalid_time_format_minutes_too_high(self):
        """Test invalid time with minutes > 59."""
        with pytest.raises(ValidationError) as exc_info:
            WorkingHoursSlot(start_time="09:60", end_time="17:00")
        assert "Time must be in HH:MM format" in str(exc_info.value)

    def test_invalid_time_format_alpha(self):
        """Test invalid time with alphabetic characters."""
        with pytest.raises(ValidationError) as exc_info:
            WorkingHoursSlot(start_time="ab:cd", end_time="17:00")
        assert "Time must be in HH:MM format" in str(exc_info.value)


class TestWorkingDaySchedule:
    """Tests for WorkingDaySchedule schema."""

    def test_default_values(self):
        """Test default values for WorkingDaySchedule."""
        schedule = WorkingDaySchedule()
        assert schedule.enabled is True
        assert schedule.slots == []

    def test_with_single_slot(self):
        """Test WorkingDaySchedule with single slot."""
        schedule = WorkingDaySchedule(
            enabled=True,
            slots=[WorkingHoursSlot(start_time="09:00", end_time="17:00")]
        )
        assert schedule.enabled is True
        assert len(schedule.slots) == 1
        assert schedule.slots[0].start_time == "09:00"

    def test_with_multiple_slots(self):
        """Test WorkingDaySchedule with multiple slots."""
        schedule = WorkingDaySchedule(
            enabled=True,
            slots=[
                WorkingHoursSlot(start_time="09:00", end_time="12:00"),
                WorkingHoursSlot(start_time="14:00", end_time="18:00"),
            ]
        )
        assert len(schedule.slots) == 2
        assert schedule.slots[1].start_time == "14:00"

    def test_disabled_day(self):
        """Test disabled WorkingDaySchedule."""
        schedule = WorkingDaySchedule(
            enabled=False,
            slots=[]
        )
        assert schedule.enabled is False


class TestBarberCreateWithWorkingHours:
    """Tests for BarberCreate with structured working_hours."""

    def test_barber_create_with_working_hours(self):
        """Test creating barber with structured working hours."""
        barber = BarberCreate(
            name="Test Barber",
            barbershop_id=1,
            working_days=["monday", "tuesday"],
            working_hours={
                "enabled": True,
                "slots": [
                    {"start_time": "09:00", "end_time": "12:00"},
                    {"start_time": "14:00", "end_time": "18:00"},
                ]
            }
        )
        assert barber.name == "Test Barber"
        assert barber.working_days == ["monday", "tuesday"]
        assert barber.working_hours.enabled is True
        assert len(barber.working_hours.slots) == 2

    def test_barber_create_with_invalid_working_hours_time(self):
        """Test creating barber with invalid time in working hours."""
        with pytest.raises(ValidationError) as exc_info:
            BarberCreate(
                name="Test Barber",
                barbershop_id=1,
                working_hours={
                    "enabled": True,
                    "slots": [
                        {"start_time": "25:00", "end_time": "12:00"},
                    ]
                }
            )
        assert "Time must be in HH:MM format" in str(exc_info.value)

    def test_barber_create_without_working_hours(self):
        """Test creating barber without working hours (optional)."""
        barber = BarberCreate(
            name="Test Barber",
            barbershop_id=1,
        )
        assert barber.working_hours is None
        assert barber.working_days is None

    def test_barber_create_with_empty_working_days(self):
        """Test creating barber with empty working days list."""
        barber = BarberCreate(
            name="Test Barber",
            barbershop_id=1,
            working_days=[],
        )
        assert barber.working_days == []
