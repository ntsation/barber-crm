import pytest
from app.repositories.barber_schedule_repository import (
    BarberScheduleRepository,
    IBarberScheduleRepository,
)
from app.repositories.barber_repository import BarberRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.user_repository import UserRepository
from app.schemas.barber_schedule import BarberScheduleCreate, BarberScheduleUpdate
from app.schemas.barber import BarberCreate
from app.schemas.user import UserCreate
from app.schemas.barbershop import BarberShopCreate


def test_create_schedule(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(BarberCreate(name="John", barbershop_id=barbershop.id))

    schedule_repo = BarberScheduleRepository(db)
    schedule_data = BarberScheduleCreate(
        barber_id=barber.id,
        day_of_week=1,
        start_time="09:00",
        end_time="18:00",
    )
    schedule = schedule_repo.create(schedule_data)

    assert schedule.id is not None
    assert schedule.day_of_week == 1
    assert schedule.start_time == "09:00"


def test_get_schedule_by_id(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(BarberCreate(name="John", barbershop_id=barbershop.id))

    schedule_repo = BarberScheduleRepository(db)
    schedule_data = BarberScheduleCreate(
        barber_id=barber.id,
        day_of_week=1,
        start_time="09:00",
        end_time="18:00",
    )
    schedule = schedule_repo.create(schedule_data)

    retrieved = schedule_repo.get_by_id(schedule.id)
    assert retrieved is not None
    assert retrieved.day_of_week == 1


def test_get_schedule_by_id_not_found(db):
    schedule_repo = BarberScheduleRepository(db)
    schedule = schedule_repo.get_by_id(999)
    assert schedule is None


def test_get_by_barber(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(BarberCreate(name="John", barbershop_id=barbershop.id))

    schedule_repo = BarberScheduleRepository(db)
    schedule_repo.create(
        BarberScheduleCreate(
            barber_id=barber.id,
            day_of_week=1,
            start_time="09:00",
            end_time="18:00",
        )
    )
    schedule_repo.create(
        BarberScheduleCreate(
            barber_id=barber.id,
            day_of_week=2,
            start_time="09:00",
            end_time="18:00",
        )
    )

    schedules = schedule_repo.get_by_barber(barber.id)
    assert len(schedules) == 2


def test_get_by_barber_and_day(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(BarberCreate(name="John", barbershop_id=barbershop.id))

    schedule_repo = BarberScheduleRepository(db)
    schedule_repo.create(
        BarberScheduleCreate(
            barber_id=barber.id,
            day_of_week=1,
            start_time="09:00",
            end_time="18:00",
        )
    )

    schedule = schedule_repo.get_by_barber_and_day(barber.id, 1)
    assert schedule is not None
    assert schedule.day_of_week == 1


def test_get_by_barber_and_day_not_found(db):
    schedule_repo = BarberScheduleRepository(db)
    schedule = schedule_repo.get_by_barber_and_day(999, 1)
    assert schedule is None


def test_get_available_by_barber(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(BarberCreate(name="John", barbershop_id=barbershop.id))

    schedule_repo = BarberScheduleRepository(db)
    schedule_repo.create(
        BarberScheduleCreate(
            barber_id=barber.id,
            day_of_week=1,
            start_time="09:00",
            end_time="18:00",
            is_available=True,
        )
    )
    schedule_repo.create(
        BarberScheduleCreate(
            barber_id=barber.id,
            day_of_week=2,
            start_time="09:00",
            end_time="18:00",
            is_available=False,
        )
    )

    schedules = schedule_repo.get_available_by_barber(barber.id)
    assert len(schedules) == 1
    assert schedules[0].day_of_week == 1


def test_update_schedule(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(BarberCreate(name="John", barbershop_id=barbershop.id))

    schedule_repo = BarberScheduleRepository(db)
    schedule_data = BarberScheduleCreate(
        barber_id=barber.id,
        day_of_week=1,
        start_time="09:00",
        end_time="18:00",
    )
    schedule = schedule_repo.create(schedule_data)

    update_data = BarberScheduleUpdate(
        start_time="08:00",
        end_time="19:00",
    )
    updated = schedule_repo.update(schedule.id, update_data)

    assert updated is not None
    assert updated.start_time == "08:00"
    assert updated.end_time == "19:00"


def test_update_schedule_not_found(db):
    schedule_repo = BarberScheduleRepository(db)
    update_data = BarberScheduleUpdate(start_time="08:00")
    updated = schedule_repo.update(999, update_data)
    assert updated is None


def test_delete_schedule(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(BarberCreate(name="John", barbershop_id=barbershop.id))

    schedule_repo = BarberScheduleRepository(db)
    schedule_data = BarberScheduleCreate(
        barber_id=barber.id,
        day_of_week=1,
        start_time="09:00",
        end_time="18:00",
    )
    schedule = schedule_repo.create(schedule_data)

    result = schedule_repo.delete(schedule.id)
    assert result is True

    deleted = schedule_repo.get_by_id(schedule.id)
    assert deleted is None


def test_delete_schedule_not_found(db):
    schedule_repo = BarberScheduleRepository(db)
    result = schedule_repo.delete(999)
    assert result is False


def test_repository_implements_interface():
    assert issubclass(BarberScheduleRepository, IBarberScheduleRepository)
