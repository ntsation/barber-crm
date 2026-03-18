import pytest
from fastapi import HTTPException
from app.services.barber_schedule_service import BarberScheduleService
from app.repositories.barber_schedule_repository import BarberScheduleRepository
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
    barber_repo_test = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo_test)

    schedule_data = BarberScheduleCreate(
        barber_id=barber.id,
        day_of_week=1,
        start_time="09:00",
        end_time="18:00",
    )
    schedule = schedule_service.create_schedule(schedule_data)

    assert schedule.day_of_week == 1


def test_create_schedule_invalid_barber(db):
    schedule_repo = BarberScheduleRepository(db)
    barber_repo = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo)

    schedule_data = BarberScheduleCreate(
        barber_id=999,
        day_of_week=1,
        start_time="09:00",
        end_time="18:00",
    )

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.create_schedule(schedule_data)

    assert exc_info.value.status_code == 404
    assert "Barber not found" in exc_info.value.detail


def test_create_schedule_duplicate_day(db):
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
    barber_repo_test = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo_test)

    schedule_data = BarberScheduleCreate(
        barber_id=barber.id,
        day_of_week=1,
        start_time="09:00",
        end_time="18:00",
    )
    schedule_service.create_schedule(schedule_data)

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.create_schedule(schedule_data)

    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail


def test_get_schedule(db):
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

    barber_repo_test = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo_test)

    retrieved = schedule_service.get_schedule(schedule.id)
    assert retrieved.id == schedule.id


def test_get_schedule_not_found(db):
    schedule_repo = BarberScheduleRepository(db)
    barber_repo = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo)

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.get_schedule(999)

    assert exc_info.value.status_code == 404
    assert "Schedule not found" in exc_info.value.detail


def test_get_barber_schedules(db):
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

    barber_repo_test = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo_test)

    schedules = schedule_service.get_barber_schedules(barber.id)
    assert len(schedules) == 2


def test_get_barber_schedules_invalid_barber(db):
    schedule_repo = BarberScheduleRepository(db)
    barber_repo = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo)

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.get_barber_schedules(999)

    assert exc_info.value.status_code == 404
    assert "Barber not found" in exc_info.value.detail


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

    barber_repo_test = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo_test)

    update_data = BarberScheduleUpdate(start_time="08:00")
    updated = schedule_service.update_schedule(schedule.id, update_data)

    assert updated.start_time == "08:00"


def test_update_schedule_not_found(db):
    schedule_repo = BarberScheduleRepository(db)
    barber_repo = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo)

    update_data = BarberScheduleUpdate(start_time="08:00")

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.update_schedule(999, update_data)

    assert exc_info.value.status_code == 404
    assert "Schedule not found" in exc_info.value.detail


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

    barber_repo_test = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo_test)

    result = schedule_service.delete_schedule(schedule.id)
    assert result is True


def test_delete_schedule_not_found(db):
    schedule_repo = BarberScheduleRepository(db)
    barber_repo = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo)

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.delete_schedule(999)

    assert exc_info.value.status_code == 404
    assert "Schedule not found" in exc_info.value.detail


def test_get_barber_available_schedules(db):
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

    barber_repo_test = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo_test)

    schedules = schedule_service.get_barber_available_schedules(barber.id)
    assert len(schedules) == 1
    assert schedules[0].day_of_week == 1


def test_get_barber_available_schedules_invalid_barber(db):
    schedule_repo = BarberScheduleRepository(db)
    barber_repo = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo)

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.get_barber_available_schedules(999)

    assert exc_info.value.status_code == 404
    assert "Barber not found" in exc_info.value.detail
