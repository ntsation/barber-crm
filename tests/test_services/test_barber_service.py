import pytest
from fastapi import HTTPException
from app.services.barber_service import BarberService
from app.repositories.barber_repository import BarberRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.user_repository import UserRepository
from app.schemas.barber import BarberCreate, BarberUpdate
from app.schemas.user import UserCreate
from app.schemas.barbershop import BarberShopCreate


def test_create_barber(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    user_repo_test = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo_test, user_repo_test)

    barber_data = BarberCreate(
        name="John Doe",
        specialty="Haircuts",
        barbershop_id=barbershop.id,
    )
    barber = barber_service.create_barber(barber_data)

    assert barber.name == "John Doe"


def test_create_barber_invalid_barbershop(db):
    barber_repo = BarberRepository(db)
    barbershop_repo = BarberShopRepository(db)
    user_repo = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo, user_repo)

    barber_data = BarberCreate(
        name="John Doe",
        specialty="Haircuts",
        barbershop_id=999,
    )

    with pytest.raises(HTTPException) as exc_info:
        barber_service.create_barber(barber_data)

    assert exc_info.value.status_code == 404
    assert "Barbershop not found" in exc_info.value.detail


def test_create_barber_invalid_user(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    user_repo_test = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo_test, user_repo_test)

    barber_data = BarberCreate(
        name="John Doe",
        specialty="Haircuts",
        barbershop_id=barbershop.id,
        user_id=999,
    )

    with pytest.raises(HTTPException) as exc_info:
        barber_service.create_barber(barber_data)

    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail


def test_get_barber(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber_data = BarberCreate(
        name="John Doe",
        specialty="Haircuts",
        barbershop_id=barbershop.id,
    )
    barber = barber_repo.create(barber_data)

    barbershop_repo_test = BarberShopRepository(db)
    user_repo_test = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo_test, user_repo_test)

    retrieved = barber_service.get_barber(barber.id)
    assert retrieved.id == barber.id


def test_get_barber_not_found(db):
    barber_repo = BarberRepository(db)
    barbershop_repo = BarberShopRepository(db)
    user_repo = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo, user_repo)

    with pytest.raises(HTTPException) as exc_info:
        barber_service.get_barber(999)

    assert exc_info.value.status_code == 404
    assert "Barber not found" in exc_info.value.detail


def test_get_barbershop_barbers(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber_repo.create(BarberCreate(name="John", barbershop_id=barbershop.id))
    barber_repo.create(BarberCreate(name="Jane", barbershop_id=barbershop.id))

    barbershop_repo_test = BarberShopRepository(db)
    user_repo_test = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo_test, user_repo_test)

    barbers = barber_service.get_barbershop_barbers(barbershop.id)
    assert len(barbers) == 2


def test_get_barbershop_barbers_invalid_barbershop(db):
    barber_repo = BarberRepository(db)
    barbershop_repo = BarberShopRepository(db)
    user_repo = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo, user_repo)

    with pytest.raises(HTTPException) as exc_info:
        barber_service.get_barbershop_barbers(999)

    assert exc_info.value.status_code == 404
    assert "Barbershop not found" in exc_info.value.detail


def test_get_barbershop_active_barbers(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber_repo.create(
        BarberCreate(name="John", barbershop_id=barbershop.id, is_active=True)
    )
    barber_repo.create(
        BarberCreate(name="Jane", barbershop_id=barbershop.id, is_active=False)
    )

    barbershop_repo_test = BarberShopRepository(db)
    user_repo_test = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo_test, user_repo_test)

    barbers = barber_service.get_barbershop_barbers(barbershop.id, active_only=True)
    assert len(barbers) == 1
    assert barbers[0].name == "John"


def test_update_barber(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber_data = BarberCreate(
        name="John Doe",
        specialty="Haircuts",
        barbershop_id=barbershop.id,
    )
    barber = barber_repo.create(barber_data)

    barbershop_repo_test = BarberShopRepository(db)
    user_repo_test = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo_test, user_repo_test)

    update_data = BarberUpdate(name="John Updated")
    updated = barber_service.update_barber(barber.id, update_data, barbershop.id)

    assert updated.name == "John Updated"


def test_update_barber_not_found(db):
    barber_repo = BarberRepository(db)
    barbershop_repo = BarberShopRepository(db)
    user_repo = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo, user_repo)

    update_data = BarberUpdate(name="Updated")

    with pytest.raises(HTTPException) as exc_info:
        barber_service.update_barber(999, update_data, 1)

    assert exc_info.value.status_code == 404
    assert "Barber not found" in exc_info.value.detail


def test_update_barber_access_denied(db):
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

    barber_repo = BarberRepository(db)
    barber_data = BarberCreate(
        name="John Doe",
        specialty="Haircuts",
        barbershop_id=barbershop1.id,
    )
    barber = barber_repo.create(barber_data)

    barbershop_repo_test = BarberShopRepository(db)
    user_repo_test = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo_test, user_repo_test)

    update_data = BarberUpdate(name="Updated")

    with pytest.raises(HTTPException) as exc_info:
        barber_service.update_barber(barber.id, update_data, barbershop2.id)

    assert exc_info.value.status_code == 403
    assert "Access denied" in exc_info.value.detail


def test_delete_barber(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber_data = BarberCreate(
        name="John Doe",
        specialty="Haircuts",
        barbershop_id=barbershop.id,
    )
    barber = barber_repo.create(barber_data)

    barbershop_repo_test = BarberShopRepository(db)
    user_repo_test = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo_test, user_repo_test)

    result = barber_service.delete_barber(barber.id, barbershop.id)
    assert result is True


def test_delete_barber_not_found(db):
    barber_repo = BarberRepository(db)
    barbershop_repo = BarberShopRepository(db)
    user_repo = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo, user_repo)

    with pytest.raises(HTTPException) as exc_info:
        barber_service.delete_barber(999, 1)

    assert exc_info.value.status_code == 404
    assert "Barber not found" in exc_info.value.detail


def test_delete_barber_access_denied(db):
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

    barber_repo = BarberRepository(db)
    barber_data = BarberCreate(
        name="John Doe",
        specialty="Haircuts",
        barbershop_id=barbershop1.id,
    )
    barber = barber_repo.create(barber_data)

    barbershop_repo_test = BarberShopRepository(db)
    user_repo_test = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo_test, user_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        barber_service.delete_barber(barber.id, barbershop2.id)

    assert exc_info.value.status_code == 403
    assert "Access denied" in exc_info.value.detail


def test_get_barber_by_user(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )
    barber_user = user_repo.create(
        UserCreate(email="barber@example.com", full_name="Barber", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber_data = BarberCreate(
        name="Barber Name",
        specialty="Haircuts",
        barbershop_id=barbershop.id,
        user_id=barber_user.id,
    )
    barber_repo.create(barber_data)

    barbershop_repo_test = BarberShopRepository(db)
    user_repo_test = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo_test, user_repo_test)

    retrieved = barber_service.get_barber_by_user(barber_user.id)
    assert retrieved.name == "Barber Name"


def test_get_barber_by_user_not_found(db):
    barber_repo = BarberRepository(db)
    barbershop_repo = BarberShopRepository(db)
    user_repo = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo, user_repo)

    with pytest.raises(HTTPException) as exc_info:
        barber_service.get_barber_by_user(999)

    assert exc_info.value.status_code == 404
    assert "Barber not found" in exc_info.value.detail
