import pytest
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
    barbershop_data = BarberShopCreate(
        name="Test Barbershop",
        address="123 Main St",
        phone="123456789",
        owner_id=owner.id,
    )
    barbershop = barbershop_repo.create(barbershop_data)

    assert barbershop.id is not None
    assert barbershop.name == "Test Barbershop"
    assert barbershop.address == "123 Main St"
    assert barbershop.phone == "123456789"
    assert barbershop.owner_id == owner.id
    assert barbershop.is_active is True


def test_get_barbershop_by_id(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="owner@example.com", full_name="Owner", password="pass123"
    )
    owner = user_repo.create(user_data)

    barbershop_repo = BarberShopRepository(db)
    barbershop_data = BarberShopCreate(
        name="Test Barbershop",
        address="123 Main St",
        phone="123456789",
        owner_id=owner.id,
    )
    created_barbershop = barbershop_repo.create(barbershop_data)

    barbershop = barbershop_repo.get_by_id(created_barbershop.id)

    assert barbershop is not None
    assert barbershop.id == created_barbershop.id


def test_get_barbershops_by_owner(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="owner@example.com", full_name="Owner", password="pass123"
    )
    owner = user_repo.create(user_data)

    barbershop_repo = BarberShopRepository(db)
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

    barbershops = barbershop_repo.get_by_owner(owner.id)

    assert len(barbershops) == 2


def test_update_barbershop(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="owner@example.com", full_name="Owner", password="pass123"
    )
    owner = user_repo.create(user_data)

    barbershop_repo = BarberShopRepository(db)
    barbershop_data = BarberShopCreate(
        name="Test Barbershop",
        address="123 Main St",
        phone="123456789",
        owner_id=owner.id,
    )
    created_barbershop = barbershop_repo.create(barbershop_data)

    update_data = BarberShopUpdate(name="Updated Barbershop")
    updated_barbershop = barbershop_repo.update(created_barbershop.id, update_data)

    assert updated_barbershop.name == "Updated Barbershop"


def test_soft_delete_barbershop(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="owner@example.com", full_name="Owner", password="pass123"
    )
    owner = user_repo.create(user_data)

    barbershop_repo = BarberShopRepository(db)
    barbershop_data = BarberShopCreate(
        name="Test Barbershop",
        address="123 Main St",
        phone="123456789",
        owner_id=owner.id,
    )
    created_barbershop = barbershop_repo.create(barbershop_data)

    result = barbershop_repo.soft_delete(created_barbershop.id)

    assert result is True

    deleted_barbershop = barbershop_repo.get_by_id(created_barbershop.id)
    assert deleted_barbershop is None


def test_restore_barbershop(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="owner@example.com", full_name="Owner", password="pass123"
    )
    owner = user_repo.create(user_data)

    barbershop_repo = BarberShopRepository(db)
    barbershop_data = BarberShopCreate(
        name="Test Barbershop",
        address="123 Main St",
        phone="123456789",
        owner_id=owner.id,
    )
    created_barbershop = barbershop_repo.create(barbershop_data)

    barbershop_repo.soft_delete(created_barbershop.id)
    restored_barbershop = barbershop_repo.restore(created_barbershop.id)

    assert restored_barbershop.is_active is True
    assert restored_barbershop.deleted_at is None


def test_get_nonexistent_barbershop(db):
    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.get_by_id(999)

    assert barbershop is None


def test_update_nonexistent_barbershop(db):
    barbershop_repo = BarberShopRepository(db)
    update_data = BarberShopUpdate(name="Updated Barbershop")
    updated_barbershop = barbershop_repo.update(999, update_data)

    assert updated_barbershop is None


def test_soft_delete_nonexistent_barbershop(db):
    barbershop_repo = BarberShopRepository(db)
    result = barbershop_repo.soft_delete(999)

    assert result is False


def test_restore_nonexistent_barbershop(db):
    barbershop_repo = BarberShopRepository(db)
    restored_barbershop = barbershop_repo.restore(999)

    assert restored_barbershop is None
