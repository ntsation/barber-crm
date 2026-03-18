import pytest
from fastapi import HTTPException
from app.services.barbershop_settings_service import BarberShopSettingsService
from app.repositories.barbershop_settings_repository import BarberShopSettingsRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.user_repository import UserRepository
from app.schemas.barbershop_settings import (
    BarberShopSettingsCreate,
    BarberShopSettingsUpdate,
)
from app.schemas.user import UserCreate
from app.schemas.barbershop import BarberShopCreate


def test_create_settings(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    settings_data = BarberShopSettingsCreate(
        barbershop_id=barbershop.id,
        accept_online_booking=True,
        require_payment_confirmation=False,
        advance_booking_hours=2,
        max_advance_booking_days=30,
        cancellation_hours=24,
        notification_email="notify@email.com",
        notification_phone="11999999999",
        default_duration_minutes=60,
        allow_walk_ins=True,
        max_walk_ins_per_day=5,
    )
    settings = settings_service.create_settings(settings_data)

    assert settings.accept_online_booking is True
    assert settings.default_duration_minutes == 60


def test_create_settings_invalid_barbershop(db):
    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo)

    settings_data = BarberShopSettingsCreate(
        barbershop_id=999, accept_online_booking=True
    )

    with pytest.raises(HTTPException) as exc_info:
        settings_service.create_settings(settings_data)

    assert exc_info.value.status_code == 404


def test_get_settings_by_id(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    settings_data = BarberShopSettingsCreate(
        barbershop_id=barbershop.id, accept_online_booking=True
    )
    settings = settings_service.create_settings(settings_data)

    found_settings = settings_service.get_settings_by_barbershop(barbershop.id)

    assert found_settings.id == settings.id


def test_get_settings_by_barbershop(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    settings_data = BarberShopSettingsCreate(barbershop_id=barbershop.id)
    settings = settings_service.create_settings(settings_data)

    found_settings = settings_service.get_settings_by_barbershop(barbershop.id)

    assert found_settings.id == settings.id


def test_get_settings_by_barbershop_no_settings(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        settings_service.get_settings_by_barbershop(barbershop.id)

    assert exc_info.value.status_code == 404


def test_update_settings_not_found(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        settings_service.update_settings(
            999, BarberShopSettingsUpdate(advance_booking_hours=4), barbershop.id
        )

    assert exc_info.value.status_code == 404


def test_soft_delete_settings_not_found(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        settings_service.soft_delete_settings(999, barbershop.id)

    assert exc_info.value.status_code == 404


def test_get_settings_invalid_barbershop(db):
    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        settings_service.get_settings_by_barbershop(999)

    assert exc_info.value.status_code == 404


def test_update_settings(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    settings_data = BarberShopSettingsCreate(
        barbershop_id=barbershop.id, accept_online_booking=True
    )
    settings = settings_service.create_settings(settings_data)

    update_data = BarberShopSettingsUpdate(advance_booking_hours=4)
    updated_settings = settings_service.update_settings(
        settings.id, update_data, barbershop.id
    )

    assert updated_settings.advance_booking_hours == 4


def test_update_invalid_barbershop(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    settings_data = BarberShopSettingsCreate(
        barbershop_id=barbershop.id, accept_online_booking=True
    )
    settings = settings_service.create_settings(settings_data)

    update_data = BarberShopSettingsUpdate(advance_booking_hours=4)

    with pytest.raises(HTTPException) as exc_info:
        settings_service.update_settings(999, update_data, barbershop.id)

    assert exc_info.value.status_code == 404


def test_soft_delete_settings(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    settings_data = BarberShopSettingsCreate(barbershop_id=barbershop.id)
    settings = settings_service.create_settings(settings_data)

    result = settings_service.soft_delete_settings(settings.id, barbershop.id)

    assert result is True


def test_restore_settings(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    settings_data = BarberShopSettingsCreate(barbershop_id=barbershop.id)
    settings = settings_service.create_settings(settings_data)

    settings_service.soft_delete_settings(settings.id, barbershop.id)
    restored_settings = settings_service.restore_settings(settings.id, barbershop.id)

    assert restored_settings.is_active is True
    assert restored_settings.deleted_at is None


def test_restore_invalid_settings(db):
    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo = BarberShopRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        settings_service.restore_settings(999, 1)

    assert exc_info.value.status_code == 404


def test_update_settings_access_denied(db):
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

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    settings = settings_service.create_settings(
        BarberShopSettingsCreate(
            barbershop_id=barbershop1.id, accept_online_booking=True
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        settings_service.update_settings(
            settings.id,
            BarberShopSettingsUpdate(advance_booking_hours=4),
            barbershop2.id,
        )

    assert exc_info.value.status_code == 403


def test_soft_delete_settings_access_denied(db):
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

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    settings = settings_service.create_settings(
        BarberShopSettingsCreate(
            barbershop_id=barbershop1.id, accept_online_booking=True
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        settings_service.soft_delete_settings(settings.id, barbershop2.id)

    assert exc_info.value.status_code == 403


def test_create_settings_duplicate(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    settings_service.create_settings(
        BarberShopSettingsCreate(
            barbershop_id=barbershop.id, accept_online_booking=True
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        settings_service.create_settings(
            BarberShopSettingsCreate(
                barbershop_id=barbershop.id, accept_online_booking=False
            )
        )

    assert exc_info.value.status_code == 400


def test_update_settings_item_not_found(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        settings_service.update_settings(
            999, BarberShopSettingsUpdate(advance_booking_hours=4), barbershop.id
        )

    assert exc_info.value.status_code == 404


def test_soft_delete_settings_item_not_found(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        settings_service.soft_delete_settings(999, barbershop.id)

    assert exc_info.value.status_code == 404


def test_soft_delete_settings_barbershop_not_found(db):
    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        settings_service.soft_delete_settings(999, 999)

    assert exc_info.value.status_code == 404


def test_update_settings_barbershop_not_found(db):
    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        settings_service.update_settings(
            999, BarberShopSettingsUpdate(advance_booking_hours=4), 999
        )

    assert exc_info.value.status_code == 404


def test_restore_settings_not_found(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        settings_service.restore_settings(999, barbershop.id)

    assert exc_info.value.status_code == 404


def test_restore_settings_not_found(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        settings_service.restore_settings(999, barbershop.id)

    assert exc_info.value.status_code == 404


def test_restore_settings_access_denied(db):
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

    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo_test)

    settings = settings_service.create_settings(
        BarberShopSettingsCreate(
            barbershop_id=barbershop1.id, accept_online_booking=True
        )
    )

    settings_service.soft_delete_settings(settings.id, barbershop1.id)

    with pytest.raises(HTTPException) as exc_info:
        settings_service.restore_settings(settings.id, barbershop2.id)

    assert exc_info.value.status_code == 403
