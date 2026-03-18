import pytest
from fastapi import HTTPException
from app.services.barbershop_profile_service import BarberShopProfileService
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
    barbershop_repo_test = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo_test)

    profile_data = BarberShopProfileCreate(
        description="Test", services="Services", barbershop_id=barbershop.id
    )
    profile = profile_service.create_profile(profile_data)

    assert profile.description == "Test"


def test_create_profile_invalid_barbershop(db):
    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo)

    profile_data = BarberShopProfileCreate(
        description="Test", services="Services", barbershop_id=999
    )

    with pytest.raises(HTTPException) as exc_info:
        profile_service.create_profile(profile_data)

    assert exc_info.value.status_code == 404


def test_create_profile_duplicate(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo_test)

    profile_service.create_profile(
        BarberShopProfileCreate(
            description="Test", services="Services", barbershop_id=barbershop.id
        )
    )

    profile_data = BarberShopProfileCreate(
        description="Updated", services="Updated", barbershop_id=barbershop.id
    )

    with pytest.raises(HTTPException) as exc_info:
        profile_service.create_profile(profile_data)

    assert exc_info.value.status_code == 400


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
    barbershop_repo_test = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo_test)

    profile_service.create_profile(
        BarberShopProfileCreate(
            description="Test", services="Services", barbershop_id=barbershop.id
        )
    )

    profile = profile_service.get_profile_by_barbershop(barbershop.id)

    assert profile.id is not None


def test_get_profile_by_barbershop_no_profile(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        profile_service.get_profile_by_barbershop(barbershop.id)

    assert exc_info.value.status_code == 404


def test_get_profile_invalid_barbershop(db):
    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        profile_service.get_profile_by_barbershop(999)

    assert exc_info.value.status_code == 404


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
    barbershop_repo_test = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo_test)

    profile = profile_service.create_profile(
        BarberShopProfileCreate(
            description="Test", services="Services", barbershop_id=barbershop.id
        )
    )

    update_data = BarberShopProfileUpdate(description="Updated")
    updated_profile = profile_service.update_profile(
        profile.id, update_data, barbershop.id
    )

    assert updated_profile.description == "Updated"


def test_update_profile_invalid_barbershop(db):
    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        profile_service.update_profile(
            999, BarberShopProfileUpdate(description="Test"), 999
        )

    assert exc_info.value.status_code == 404


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
    barbershop_repo_test = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo_test)

    profile = profile_service.create_profile(
        BarberShopProfileCreate(
            description="Test", services="Services", barbershop_id=barbershop.id
        )
    )

    result = profile_service.soft_delete_profile(profile.id, barbershop.id)

    assert result is True


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
    barbershop_repo_test = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo_test)

    profile = profile_service.create_profile(
        BarberShopProfileCreate(
            description="Test", services="Services", barbershop_id=barbershop.id
        )
    )

    profile_service.soft_delete_profile(profile.id, barbershop.id)
    restored_profile = profile_service.restore_profile(profile.id, barbershop.id)

    assert restored_profile.is_active is True


def test_restore_profile_invalid_barbershop(db):
    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        profile_service.restore_profile(999, 999)

    assert exc_info.value.status_code == 404


def test_update_profile_not_found(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        profile_service.update_profile(
            999, BarberShopProfileUpdate(description="Test"), barbershop.id
        )

    assert exc_info.value.status_code == 404


def test_soft_delete_profile_not_found(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        profile_service.soft_delete_profile(999, barbershop.id)

    assert exc_info.value.status_code == 404


def test_restore_profile_not_found(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        profile_service.restore_profile(999, barbershop.id)

    assert exc_info.value.status_code == 404


def test_update_profile_access_denied(db):
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

    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo_test)

    profile = profile_service.create_profile(
        BarberShopProfileCreate(
            description="Test", services="Services", barbershop_id=barbershop1.id
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        profile_service.update_profile(
            profile.id, BarberShopProfileUpdate(description="Test"), barbershop2.id
        )

    assert exc_info.value.status_code == 403


def test_soft_delete_profile_access_denied(db):
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

    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo_test)

    profile = profile_service.create_profile(
        BarberShopProfileCreate(
            description="Test", services="Services", barbershop_id=barbershop1.id
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        profile_service.soft_delete_profile(profile.id, barbershop2.id)

    assert exc_info.value.status_code == 403


def test_soft_delete_profile_barbershop_not_found(db):
    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        profile_service.soft_delete_profile(999, 999)

    assert exc_info.value.status_code == 404


def test_soft_delete_profile_item_not_found(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        profile_service.soft_delete_profile(999, barbershop.id)

    assert exc_info.value.status_code == 404


def test_restore_profile_access_denied(db):
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

    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo_test)

    profile = profile_service.create_profile(
        BarberShopProfileCreate(
            description="Test", services="Services", barbershop_id=barbershop1.id
        )
    )

    profile_service.soft_delete_profile(profile.id, barbershop1.id)

    with pytest.raises(HTTPException) as exc_info:
        profile_service.restore_profile(profile.id, barbershop2.id)

    assert exc_info.value.status_code == 403
