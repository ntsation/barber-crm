import pytest
from app.repositories.barbershop_schedule_repository import BarberShopScheduleRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.user_repository import UserRepository
from app.schemas.barbershop_schedule import (
    BarberShopScheduleCreate,
    BarberShopScheduleUpdate,
)
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

    schedule_repo = BarberShopScheduleRepository(db)
    schedule_data = BarberShopScheduleCreate(
        barbershop_id=barbershop.id,
        monday={"enabled": True, "start_time": "09:00", "end_time": "18:00"},
        tuesday={"enabled": True, "start_time": "09:00", "end_time": "18:00"},
        wednesday={"enabled": True, "start_time": "09:00", "end_time": "18:00"},
        thursday={"enabled": True, "start_time": "09:00", "end_time": "18:00"},
        friday={"enabled": True, "start_time": "09:00", "end_time": "18:00"},
        saturday={"enabled": False},
        sunday={"enabled": False},
    )
    schedule = schedule_repo.create(schedule_data)

    assert schedule.id is not None
    assert schedule.barbershop_id == barbershop.id


def test_get_schedule_by_id(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    schedule_repo = BarberShopScheduleRepository(db)
    schedule = schedule_repo.create(
        BarberShopScheduleCreate(
            barbershop_id=barbershop.id,
            monday={"enabled": True, "start_time": "09:00", "end_time": "18:00"},
        )
    )

    found_schedule = schedule_repo.get_by_id(schedule.id)

    assert found_schedule is not None
    assert found_schedule.id == schedule.id


def test_get_schedule_by_barbershop(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    schedule_repo = BarberShopScheduleRepository(db)

    schedule = schedule_repo.create(
        BarberShopScheduleCreate(barbershop_id=barbershop.id, monday={"enabled": True})
    )

    found_schedule = schedule_repo.get_by_barbershop(barbershop.id)

    assert found_schedule is not None
    assert found_schedule.id == schedule.id


def test_update_schedule(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    schedule_repo = BarberShopScheduleRepository(db)
    schedule = schedule_repo.create(
        BarberShopScheduleCreate(
            barbershop_id=barbershop.id,
            monday={"enabled": True, "start_time": "09:00", "end_time": "18:00"},
        )
    )

    update_data = BarberShopScheduleUpdate(monday={"enabled": False})
    updated_schedule = schedule_repo.update(schedule.id, update_data)

    assert updated_schedule.id == schedule.id


def test_soft_delete_schedule(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    schedule_repo = BarberShopScheduleRepository(db)
    schedule = schedule_repo.create(
        BarberShopScheduleCreate(
            barbershop_id=barbershop.id,
            monday={"enabled": True, "start_time": "09:00", "end_time": "18:00"},
        )
    )

    result = schedule_repo.soft_delete(schedule.id)

    assert result is True

    deleted_schedule = schedule_repo.get_by_id(schedule.id)
    assert deleted_schedule is None


def test_restore_schedule(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    schedule_repo = BarberShopScheduleRepository(db)
    schedule = schedule_repo.create(
        BarberShopScheduleCreate(
            barbershop_id=barbershop.id,
            monday={"enabled": True, "start_time": "09:00", "end_time": "18:00"},
        )
    )

    schedule_repo.soft_delete(schedule.id)
    restored_schedule = schedule_repo.restore(schedule.id)

    assert restored_schedule.is_active is True
    assert restored_schedule.deleted_at is None


def test_update_nonexistent_schedule(db):
    schedule_repo = BarberShopScheduleRepository(db)
    update_data = BarberShopScheduleUpdate(monday={"enabled": False})
    updated_schedule = schedule_repo.update(999, update_data)

    assert updated_schedule is None


def test_soft_delete_nonexistent_schedule(db):
    schedule_repo = BarberShopScheduleRepository(db)
    result = schedule_repo.soft_delete(999)

    assert result is False


def test_restore_nonexistent_schedule(db):
    schedule_repo = BarberShopScheduleRepository(db)
    restored_schedule = schedule_repo.restore(999)

    assert restored_schedule is None
