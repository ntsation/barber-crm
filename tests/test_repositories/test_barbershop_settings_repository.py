import pytest
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
    settings = settings_repo.create(settings_data)

    assert settings.id is not None
    assert settings.barbershop_id == barbershop.id


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
    settings = settings_repo.create(
        BarberShopSettingsCreate(barbershop_id=barbershop.id)
    )

    found_settings = settings_repo.get_by_id(settings.id)

    assert found_settings is not None
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

    settings = settings_repo.create(
        BarberShopSettingsCreate(barbershop_id=barbershop.id)
    )

    found_settings = settings_repo.get_by_barbershop(barbershop.id)

    assert found_settings is not None
    assert found_settings.id == settings.id


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
    settings = settings_repo.create(
        BarberShopSettingsCreate(barbershop_id=barbershop.id)
    )

    update_data = BarberShopSettingsUpdate(advance_booking_hours=4)
    updated_settings = settings_repo.update(settings.id, update_data)

    assert updated_settings.id == settings.id


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
    settings = settings_repo.create(
        BarberShopSettingsCreate(barbershop_id=barbershop.id)
    )

    result = settings_repo.soft_delete(settings.id)

    assert result is True

    deleted_settings = settings_repo.get_by_id(settings.id)
    assert deleted_settings is None


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
    settings = settings_repo.create(
        BarberShopSettingsCreate(barbershop_id=barbershop.id)
    )

    settings_repo.soft_delete(settings.id)
    restored_settings = settings_repo.restore(settings.id)

    assert restored_settings.is_active is True
    assert restored_settings.deleted_at is None


def test_update_nonexistent_settings(db):
    settings_repo = BarberShopSettingsRepository(db)
    update_data = BarberShopSettingsUpdate(advance_booking_hours=4)
    updated_settings = settings_repo.update(999, update_data)

    assert updated_settings is None


def test_soft_delete_nonexistent_settings(db):
    settings_repo = BarberShopSettingsRepository(db)
    result = settings_repo.soft_delete(999)

    assert result is False


def test_restore_nonexistent_settings(db):
    settings_repo = BarberShopSettingsRepository(db)
    restored_settings = settings_repo.restore(999)

    assert restored_settings is None
