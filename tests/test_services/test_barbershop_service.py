import pytest
from fastapi import HTTPException
from app.services.barbershop_service import BarberShopService
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.user_repository import UserRepository
from app.schemas.barbershop import BarberShopCreate, BarberShopUpdate
from app.schemas.user import UserCreate


def test_create_barbershop(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="owner@example.com", full_name="Owner", password="pass123"
    )
    owner = user_repo.create(user_data)

    barbershop_repo = BarberShopRepository(db)
    barbershop_service = BarberShopService(barbershop_repo)
    barbershop_data = BarberShopCreate(
        name="Test Barbershop",
        address="123 Main St",
        phone="123456789",
        owner_id=owner.id,
    )

    barbershop = barbershop_service.create_barbershop(barbershop_data)

    assert barbershop.name == "Test Barbershop"
    assert barbershop.owner_id == owner.id


def test_get_barbershop(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="owner@example.com", full_name="Owner", password="pass123"
    )
    owner = user_repo.create(user_data)

    barbershop_repo = BarberShopRepository(db)
    barbershop_service = BarberShopService(barbershop_repo)
    barbershop_data = BarberShopCreate(
        name="Test Barbershop",
        address="123 Main St",
        phone="123456789",
        owner_id=owner.id,
    )
    created_barbershop = barbershop_repo.create(barbershop_data)

    barbershop = barbershop_service.get_barbershop(created_barbershop.id, owner.id)

    assert barbershop.id == created_barbershop.id


def test_get_barbershop_not_found(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="owner@example.com", full_name="Owner", password="pass123"
    )
    owner = user_repo.create(user_data)

    barbershop_repo = BarberShopRepository(db)
    barbershop_service = BarberShopService(barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        barbershop_service.get_barbershop(999, owner.id)

    assert exc_info.value.status_code == 404


def test_get_barbershop_access_denied(db):
    user_repo = UserRepository(db)
    owner_data = UserCreate(
        email="owner@example.com", full_name="Owner", password="pass123"
    )
    owner = user_repo.create(owner_data)
    other_user_data = UserCreate(
        email="other@example.com", full_name="Other", password="pass456"
    )
    other_user = user_repo.create(other_user_data)

    barbershop_repo = BarberShopRepository(db)
    barbershop_service = BarberShopService(barbershop_repo)
    barbershop_data = BarberShopCreate(
        name="Test Barbershop",
        address="123 Main St",
        phone="123456789",
        owner_id=owner.id,
    )
    created_barbershop = barbershop_repo.create(barbershop_data)

    with pytest.raises(HTTPException) as exc_info:
        barbershop_service.get_barbershop(created_barbershop.id, other_user.id)

    assert exc_info.value.status_code == 403


def test_get_owner_barbershops(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="owner@example.com", full_name="Owner", password="pass123"
    )
    owner = user_repo.create(user_data)

    barbershop_repo = BarberShopRepository(db)
    barbershop_service = BarberShopService(barbershop_repo)
    barbershop_repo.create(
        BarberShopCreate(
            name="Shop 1", address="1 Main St", phone="123456789", owner_id=owner.id
        )
    )
    barbershop_repo.create(
        BarberShopCreate(
            name="Shop 2", address="2 Main St", phone="987654321", owner_id=owner.id
        )
    )

    barbershops = barbershop_service.get_owner_barbershops(owner.id)

    assert len(barbershops) == 2


def test_update_barbershop(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="owner@example.com", full_name="Owner", password="pass123"
    )
    owner = user_repo.create(user_data)

    barbershop_repo = BarberShopRepository(db)
    barbershop_service = BarberShopService(barbershop_repo)
    barbershop_data = BarberShopCreate(
        name="Test Barbershop",
        address="123 Main St",
        phone="123456789",
        owner_id=owner.id,
    )
    created_barbershop = barbershop_repo.create(barbershop_data)

    update_data = BarberShopUpdate(name="Updated Barbershop")
    updated_barbershop = barbershop_service.update_barbershop(
        created_barbershop.id, update_data, owner.id
    )

    assert updated_barbershop.name == "Updated Barbershop"


def test_soft_delete_barbershop(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="owner@example.com", full_name="Owner", password="pass123"
    )
    owner = user_repo.create(user_data)

    barbershop_repo = BarberShopRepository(db)
    barbershop_service = BarberShopService(barbershop_repo)
    barbershop_data = BarberShopCreate(
        name="Test Barbershop",
        address="123 Main St",
        phone="123456789",
        owner_id=owner.id,
    )
    created_barbershop = barbershop_repo.create(barbershop_data)

    result = barbershop_service.soft_delete_barbershop(created_barbershop.id, owner.id)

    assert result is True


def test_restore_barbershop(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="owner@example.com", full_name="Owner", password="pass123"
    )
    owner = user_repo.create(user_data)

    barbershop_repo = BarberShopRepository(db)
    barbershop_service = BarberShopService(barbershop_repo)
    barbershop_data = BarberShopCreate(
        name="Test Barbershop",
        address="123 Main St",
        phone="123456789",
        owner_id=owner.id,
    )
    created_barbershop = barbershop_repo.create(barbershop_data)

    barbershop_service.soft_delete_barbershop(created_barbershop.id, owner.id)
    restored_barbershop = barbershop_service.restore_barbershop(
        created_barbershop.id, owner.id
    )

    assert restored_barbershop.is_active is True


def test_restore_barbershop_access_denied(db):
    user_repo = UserRepository(db)
    owner_data = UserCreate(
        email="owner@example.com", full_name="Owner", password="pass123"
    )
    owner = user_repo.create(owner_data)
    other_user_data = UserCreate(
        email="other@example.com", full_name="Other", password="pass456"
    )
    other_user = user_repo.create(other_user_data)

    barbershop_repo = BarberShopRepository(db)
    barbershop_service = BarberShopService(barbershop_repo)
    barbershop_data = BarberShopCreate(
        name="Test Barbershop",
        address="123 Main St",
        phone="123456789",
        owner_id=owner.id,
    )
    created_barbershop = barbershop_repo.create(barbershop_data)

    barbershop_service.soft_delete_barbershop(created_barbershop.id, owner.id)

    with pytest.raises(HTTPException) as exc_info:
        barbershop_service.restore_barbershop(created_barbershop.id, other_user.id)

    assert exc_info.value.status_code == 403
