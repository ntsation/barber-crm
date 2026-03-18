import pytest
from app.repositories.barber_repository import BarberRepository, IBarberRepository
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
    barber_data = BarberCreate(
        name="John Doe",
        specialty="Haircuts",
        bio="Experienced barber",
        phone="555-1234",
        barbershop_id=barbershop.id,
    )
    barber = barber_repo.create(barber_data)

    assert barber.id is not None
    assert barber.name == "John Doe"
    assert barber.specialty == "Haircuts"


def test_create_barber_with_user(db):
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
    barber = barber_repo.create(barber_data)

    assert barber.user_id == barber_user.id


def test_get_barber_by_id(db):
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

    retrieved = barber_repo.get_by_id(barber.id)
    assert retrieved is not None
    assert retrieved.name == "John Doe"


def test_get_barber_by_id_not_found(db):
    barber_repo = BarberRepository(db)
    barber = barber_repo.get_by_id(999)
    assert barber is None


def test_get_by_barbershop(db):
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
        BarberCreate(
            name="John Doe",
            specialty="Haircuts",
            barbershop_id=barbershop.id,
        )
    )
    barber_repo.create(
        BarberCreate(
            name="Jane Smith",
            specialty="Beards",
            barbershop_id=barbershop.id,
        )
    )

    barbers = barber_repo.get_by_barbershop(barbershop.id)
    assert len(barbers) == 2


def test_get_active_by_barbershop(db):
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
        BarberCreate(
            name="John Doe",
            specialty="Haircuts",
            barbershop_id=barbershop.id,
            is_active=True,
        )
    )
    barber_repo.create(
        BarberCreate(
            name="Jane Smith",
            specialty="Beards",
            barbershop_id=barbershop.id,
            is_active=False,
        )
    )

    barbers = barber_repo.get_active_by_barbershop(barbershop.id)
    assert len(barbers) == 1
    assert barbers[0].name == "John Doe"
    assert barbers[0].is_active is True


def test_get_by_user(db):
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

    retrieved = barber_repo.get_by_user(barber_user.id)
    assert retrieved is not None
    assert retrieved.name == "Barber Name"


def test_get_by_user_not_found(db):
    barber_repo = BarberRepository(db)
    barber = barber_repo.get_by_user(999)
    assert barber is None


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

    update_data = BarberUpdate(
        name="John Updated",
        specialty="Specialty Updated",
        phone="555-9999",
    )
    updated = barber_repo.update(barber.id, update_data)

    assert updated is not None
    assert updated.name == "John Updated"
    assert updated.specialty == "Specialty Updated"


def test_update_barber_not_found(db):
    barber_repo = BarberRepository(db)
    update_data = BarberUpdate(name="Updated")
    updated = barber_repo.update(999, update_data)
    assert updated is None


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

    result = barber_repo.delete(barber.id)
    assert result is True

    deleted = barber_repo.get_by_id(barber.id)
    assert deleted is None


def test_delete_barber_not_found(db):
    barber_repo = BarberRepository(db)
    result = barber_repo.delete(999)
    assert result is False


def test_repository_implements_interface():
    assert issubclass(BarberRepository, IBarberRepository)
