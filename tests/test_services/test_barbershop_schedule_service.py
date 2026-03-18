import pytest
from fastapi import HTTPException
from app.services.barbershop_schedule_service import BarberShopScheduleService
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
    barbershop_repo_test = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo_test)

    schedule_data = BarberShopScheduleCreate(
        barbershop_id=barbershop.id,
        monday={"enabled": True, "start_time": "09:00", "end_time": "18:00"},
    )
    schedule = schedule_service.create_schedule(schedule_data)

    assert schedule.id is not None


def test_create_schedule_invalid_barbershop(db):
    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo)

    schedule_data = BarberShopScheduleCreate(barbershop_id=999)

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.create_schedule(schedule_data)

    assert exc_info.value.status_code == 404


def test_create_schedule_duplicate(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo_test)

    schedule_service.create_schedule(
        BarberShopScheduleCreate(barbershop_id=barbershop.id, monday={"enabled": True})
    )

    schedule_data = BarberShopScheduleCreate(
        barbershop_id=barbershop.id, monday={"enabled": False}
    )

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.create_schedule(schedule_data)

    assert exc_info.value.status_code == 400


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
    barbershop_repo_test = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo_test)

    schedule_service.create_schedule(
        BarberShopScheduleCreate(barbershop_id=barbershop.id, monday={"enabled": True})
    )

    schedule = schedule_service.get_schedule_by_barbershop(barbershop.id)

    assert schedule.id is not None


def test_get_schedule_by_barbershop_no_schedule(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.get_schedule_by_barbershop(barbershop.id)

    assert exc_info.value.status_code == 404


def test_get_schedule_invalid_barbershop(db):
    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.get_schedule_by_barbershop(999)

    assert exc_info.value.status_code == 404


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
    barbershop_repo_test = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo_test)

    schedule = schedule_service.create_schedule(
        BarberShopScheduleCreate(barbershop_id=barbershop.id, monday={"enabled": True})
    )

    update_data = BarberShopScheduleUpdate(monday={"enabled": False})
    updated_schedule = schedule_service.update_schedule(
        schedule.id, update_data, barbershop.id
    )

    assert updated_schedule.id == schedule.id


def test_update_schedule_invalid_barbershop(db):
    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.update_schedule(
            999, BarberShopScheduleUpdate(monday={"enabled": False}), 999
        )

    assert exc_info.value.status_code == 404


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
    barbershop_repo_test = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo_test)

    schedule = schedule_service.create_schedule(
        BarberShopScheduleCreate(barbershop_id=barbershop.id, monday={"enabled": True})
    )

    result = schedule_service.soft_delete_schedule(schedule.id, barbershop.id)

    assert result is True


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
    barbershop_repo_test = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo_test)

    schedule = schedule_service.create_schedule(
        BarberShopScheduleCreate(barbershop_id=barbershop.id, monday={"enabled": True})
    )

    schedule_service.soft_delete_schedule(schedule.id, barbershop.id)
    restored_schedule = schedule_service.restore_schedule(schedule.id, barbershop.id)

    assert restored_schedule.is_active is True


def test_restore_schedule_invalid_barbershop(db):
    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.restore_schedule(999, 999)

    assert exc_info.value.status_code == 404


def test_update_schedule_not_found(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.update_schedule(
            999, BarberShopScheduleUpdate(monday={"enabled": False}), barbershop.id
        )

    assert exc_info.value.status_code == 404


def test_soft_delete_schedule_not_found(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.soft_delete_schedule(999, barbershop.id)

    assert exc_info.value.status_code == 404


def test_restore_schedule_not_found(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.restore_schedule(999, barbershop.id)

    assert exc_info.value.status_code == 404


def test_update_schedule_access_denied(db):
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

    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo_test)

    schedule = schedule_service.create_schedule(
        BarberShopScheduleCreate(barbershop_id=barbershop1.id, monday={"enabled": True})
    )

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.update_schedule(
            schedule.id,
            BarberShopScheduleUpdate(monday={"enabled": False}),
            barbershop2.id,
        )

    assert exc_info.value.status_code == 403


def test_soft_delete_schedule_access_denied(db):
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

    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo_test)

    schedule = schedule_service.create_schedule(
        BarberShopScheduleCreate(barbershop_id=barbershop1.id, monday={"enabled": True})
    )

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.soft_delete_schedule(schedule.id, barbershop2.id)

    assert exc_info.value.status_code == 403


def test_soft_delete_schedule_item_not_found(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.soft_delete_schedule(999, barbershop.id)

    assert exc_info.value.status_code == 404


def test_soft_delete_schedule_barbershop_not_found(db):
    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.soft_delete_schedule(999, 999)

    assert exc_info.value.status_code == 404


def test_restore_schedule_access_denied(db):
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

    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo_test)

    schedule = schedule_service.create_schedule(
        BarberShopScheduleCreate(barbershop_id=barbershop1.id, monday={"enabled": True})
    )

    schedule_service.soft_delete_schedule(schedule.id, barbershop1.id)

    with pytest.raises(HTTPException) as exc_info:
        schedule_service.restore_schedule(schedule.id, barbershop2.id)

    assert exc_info.value.status_code == 403
