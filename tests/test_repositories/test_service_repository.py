import pytest
from app.repositories.service_repository import ServiceRepository, IServiceRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.user_repository import UserRepository
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.schemas.user import UserCreate
from app.schemas.barbershop import BarberShopCreate


def test_create_service(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    service_repo = ServiceRepository(db)
    service_data = ServiceCreate(
        name="Haircut",
        description="Classic haircut",
        category="Hair",
        price=25.0,
        duration_minutes=30,
        barbershop_id=barbershop.id,
    )
    service = service_repo.create(service_data)

    assert service.id is not None
    assert service.name == "Haircut"
    assert service.price == 25.0
    assert service.duration_minutes == 30


def test_get_service_by_id(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    service_repo = ServiceRepository(db)
    service_data = ServiceCreate(
        name="Haircut",
        description="Classic haircut",
        category="Hair",
        price=25.0,
        duration_minutes=30,
        barbershop_id=barbershop.id,
    )
    service = service_repo.create(service_data)

    retrieved = service_repo.get_by_id(service.id)
    assert retrieved is not None
    assert retrieved.name == "Haircut"
    assert retrieved.price == 25.0


def test_get_service_by_id_not_found(db):
    service_repo = ServiceRepository(db)
    service = service_repo.get_by_id(999)
    assert service is None


def test_get_by_barbershop(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    service_repo = ServiceRepository(db)
    service_repo.create(
        ServiceCreate(
            name="Haircut",
            description="Classic haircut",
            category="Hair",
            price=25.0,
            duration_minutes=30,
            barbershop_id=barbershop.id,
        )
    )
    service_repo.create(
        ServiceCreate(
            name="Beard Trim",
            description="Beard trim",
            category="Beard",
            price=15.0,
            duration_minutes=20,
            barbershop_id=barbershop.id,
        )
    )

    services = service_repo.get_by_barbershop(barbershop.id)
    assert len(services) == 2
    assert services[0].name == "Beard Trim"
    assert services[1].name == "Haircut"


def test_get_by_barbershop_and_category(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    service_repo = ServiceRepository(db)
    service_repo.create(
        ServiceCreate(
            name="Haircut",
            description="Classic haircut",
            category="Hair",
            price=25.0,
            duration_minutes=30,
            barbershop_id=barbershop.id,
        )
    )
    service_repo.create(
        ServiceCreate(
            name="Beard Trim",
            description="Beard trim",
            category="Beard",
            price=15.0,
            duration_minutes=20,
            barbershop_id=barbershop.id,
        )
    )
    service_repo.create(
        ServiceCreate(
            name="Buzz Cut",
            description="Buzz cut",
            category="Hair",
            price=20.0,
            duration_minutes=15,
            barbershop_id=barbershop.id,
        )
    )

    services = service_repo.get_by_barbershop_and_category(barbershop.id, "Hair")
    assert len(services) == 2
    assert all(s.category == "Hair" for s in services)


def test_get_active_by_barbershop(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    service_repo = ServiceRepository(db)
    service_repo.create(
        ServiceCreate(
            name="Haircut",
            description="Classic haircut",
            category="Hair",
            price=25.0,
            duration_minutes=30,
            barbershop_id=barbershop.id,
            is_active=True,
        )
    )
    service_repo.create(
        ServiceCreate(
            name="Beard Trim",
            description="Beard trim",
            category="Beard",
            price=15.0,
            duration_minutes=20,
            barbershop_id=barbershop.id,
            is_active=False,
        )
    )

    services = service_repo.get_active_by_barbershop(barbershop.id)
    assert len(services) == 1
    assert services[0].name == "Haircut"
    assert services[0].is_active is True


def test_update_service(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    service_repo = ServiceRepository(db)
    service_data = ServiceCreate(
        name="Haircut",
        description="Classic haircut",
        category="Hair",
        price=25.0,
        duration_minutes=30,
        barbershop_id=barbershop.id,
    )
    service = service_repo.create(service_data)

    update_data = ServiceUpdate(
        name="Premium Haircut",
        price=35.0,
        duration_minutes=45,
    )
    updated = service_repo.update(service.id, update_data)

    assert updated is not None
    assert updated.name == "Premium Haircut"
    assert updated.price == 35.0
    assert updated.duration_minutes == 45


def test_update_service_not_found(db):
    service_repo = ServiceRepository(db)
    update_data = ServiceUpdate(name="Updated")
    updated = service_repo.update(999, update_data)
    assert updated is None


def test_delete_service(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    service_repo = ServiceRepository(db)
    service_data = ServiceCreate(
        name="Haircut",
        description="Classic haircut",
        category="Hair",
        price=25.0,
        duration_minutes=30,
        barbershop_id=barbershop.id,
    )
    service = service_repo.create(service_data)

    result = service_repo.delete(service.id)
    assert result is True

    deleted = service_repo.get_by_id(service.id)
    assert deleted is None


def test_delete_service_not_found(db):
    service_repo = ServiceRepository(db)
    result = service_repo.delete(999)
    assert result is False


def test_repository_implements_interface():
    assert issubclass(ServiceRepository, IServiceRepository)
