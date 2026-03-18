import pytest
from app.repositories.barbershop_profile_repository import BarberShopProfileRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.user_repository import UserRepository
from app.schemas.barbershop_profile import (
    BarberShopProfileCreate,
    BarberShopProfileUpdate,
)
from app.schemas.user import UserCreate
from app.schemas.barbershop import BarberShopCreate


def test_create_profile(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    profile_repo = BarberShopProfileRepository(db)
    profile_data = BarberShopProfileCreate(
        description="Test description",
        services="Test services",
        logo_url="http://logo.com",
        banner_url="http://banner.com",
        barbershop_id=barbershop.id,
    )
    profile = profile_repo.create(profile_data)

    assert profile.id is not None
    assert profile.description == "Test description"


def test_get_profile_by_id(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    profile_repo = BarberShopProfileRepository(db)
    profile = profile_repo.create(
        BarberShopProfileCreate(
            description="Test",
            services="Test",
            logo_url="logo",
            banner_url="banner",
            barbershop_id=barbershop.id,
        )
    )

    found_profile = profile_repo.get_by_id(profile.id)

    assert found_profile is not None
    assert found_profile.id == profile.id


def test_get_profile_by_barbershop(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    profile_repo = BarberShopProfileRepository(db)
    profile_repo.create(
        BarberShopProfileCreate(
            description="Test",
            services="Test",
            logo_url="logo",
            banner_url="banner",
            barbershop_id=barbershop.id,
        )
    )

    found_profile = profile_repo.get_by_barbershop(barbershop.id)

    assert found_profile is not None
    assert found_profile.barbershop_id == barbershop.id


def test_update_profile(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    profile_repo = BarberShopProfileRepository(db)
    profile = profile_repo.create(
        BarberShopProfileCreate(
            description="Test",
            services="Test",
            logo_url="logo",
            banner_url="banner",
            barbershop_id=barbershop.id,
        )
    )

    update_data = BarberShopProfileUpdate(description="Updated description")
    updated_profile = profile_repo.update(profile.id, update_data)

    assert updated_profile.description == "Updated description"


def test_update_nonexistent_profile(db):
    profile_repo = BarberShopProfileRepository(db)
    update_data = BarberShopProfileUpdate(description="Updated")
    updated_profile = profile_repo.update(999, update_data)

    assert updated_profile is None


def test_soft_delete_profile(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    profile_repo = BarberShopProfileRepository(db)
    profile = profile_repo.create(
        BarberShopProfileCreate(
            description="Test",
            services="Test",
            logo_url="logo",
            banner_url="banner",
            barbershop_id=barbershop.id,
        )
    )

    result = profile_repo.soft_delete(profile.id)

    assert result is True

    deleted_profile = profile_repo.get_by_id(profile.id)
    assert deleted_profile is None


def test_soft_delete_nonexistent_profile(db):
    profile_repo = BarberShopProfileRepository(db)
    result = profile_repo.soft_delete(999)

    assert result is False


def test_restore_profile(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    profile_repo = BarberShopProfileRepository(db)
    profile = profile_repo.create(
        BarberShopProfileCreate(
            description="Test",
            services="Test",
            logo_url="logo",
            banner_url="banner",
            barbershop_id=barbershop.id,
        )
    )

    profile_repo.soft_delete(profile.id)
    restored_profile = profile_repo.restore(profile.id)

    assert restored_profile.is_active is True
    assert restored_profile.deleted_at is None


def test_restore_nonexistent_profile(db):
    profile_repo = BarberShopProfileRepository(db)
    restored_profile = profile_repo.restore(999)

    assert restored_profile is None
