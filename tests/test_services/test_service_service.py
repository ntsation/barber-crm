import pytest
from fastapi import HTTPException
from app.services.service_service import ServiceService
from app.repositories.service_repository import ServiceRepository
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
    barbershop_repo_test = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo_test)

    service_data = ServiceCreate(
        name="Haircut",
        description="Classic haircut",
        category="Hair",
        price=25.0,
        duration_minutes=30,
        barbershop_id=barbershop.id,
    )
    service = service_service.create_service(service_data)

    assert service.name == "Haircut"
    assert service.price == 25.0


def test_create_service_invalid_barbershop(db):
    service_repo = ServiceRepository(db)
    barbershop_repo = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo)

    service_data = ServiceCreate(
        name="Haircut",
        description="Classic haircut",
        category="Hair",
        price=25.0,
        duration_minutes=30,
        barbershop_id=999,
    )

    with pytest.raises(HTTPException) as exc_info:
        service_service.create_service(service_data)

    assert exc_info.value.status_code == 404
    assert "Barbershop not found" in exc_info.value.detail


def test_get_service(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    service_repo = ServiceRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo_test)

    service_data = ServiceCreate(
        name="Haircut",
        description="Classic haircut",
        category="Hair",
        price=25.0,
        duration_minutes=30,
        barbershop_id=barbershop.id,
    )
    service = service_repo.create(service_data)

    retrieved = service_service.get_service(service.id)
    assert retrieved.id == service.id
    assert retrieved.name == "Haircut"


def test_get_service_not_found(db):
    service_repo = ServiceRepository(db)
    barbershop_repo = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        service_service.get_service(999)

    assert exc_info.value.status_code == 404
    assert "Service not found" in exc_info.value.detail


def test_get_barbershop_services(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    service_repo = ServiceRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo_test)

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

    services = service_service.get_barbershop_services(barbershop.id)
    assert len(services) == 2


def test_get_barbershop_services_invalid_barbershop(db):
    service_repo = ServiceRepository(db)
    barbershop_repo = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        service_service.get_barbershop_services(999)

    assert exc_info.value.status_code == 404
    assert "Barbershop not found" in exc_info.value.detail


def test_get_barbershop_active_services_invalid_barbershop(db):
    service_repo = ServiceRepository(db)
    barbershop_repo = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        service_service.get_barbershop_active_services(999)

    assert exc_info.value.status_code == 404
    assert "Barbershop not found" in exc_info.value.detail


def test_get_barbershop_services_by_category_invalid_barbershop(db):
    service_repo = ServiceRepository(db)
    barbershop_repo = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        service_service.get_barbershop_services_by_category(999, "Hair")

    assert exc_info.value.status_code == 404
    assert "Barbershop not found" in exc_info.value.detail


def test_get_barbershop_active_services(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    service_repo = ServiceRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo_test)

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

    services = service_service.get_barbershop_active_services(barbershop.id)
    assert len(services) == 1
    assert services[0].name == "Haircut"
    assert services[0].is_active is True


def test_get_barbershop_services_by_category(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    service_repo = ServiceRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo_test)

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

    services = service_service.get_barbershop_services_by_category(
        barbershop.id, "Hair"
    )
    assert len(services) == 2
    assert all(s.category == "Hair" for s in services)


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
    barbershop_repo_test = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo_test)

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
    updated = service_service.update_service(service.id, update_data, barbershop.id)

    assert updated.name == "Premium Haircut"
    assert updated.price == 35.0


def test_update_service_not_found(db):
    service_repo = ServiceRepository(db)
    barbershop_repo = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo)

    update_data = ServiceUpdate(name="Updated")

    with pytest.raises(HTTPException) as exc_info:
        service_service.update_service(999, update_data, 1)

    assert exc_info.value.status_code == 404
    assert "Service not found" in exc_info.value.detail


def test_update_service_access_denied(db):
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

    service_repo = ServiceRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo_test)

    service_data = ServiceCreate(
        name="Haircut",
        description="Classic haircut",
        category="Hair",
        price=25.0,
        duration_minutes=30,
        barbershop_id=barbershop1.id,
    )
    service = service_repo.create(service_data)

    update_data = ServiceUpdate(name="Updated")

    with pytest.raises(HTTPException) as exc_info:
        service_service.update_service(service.id, update_data, barbershop2.id)

    assert exc_info.value.status_code == 403
    assert "Access denied" in exc_info.value.detail


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
    barbershop_repo_test = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo_test)

    service_data = ServiceCreate(
        name="Haircut",
        description="Classic haircut",
        category="Hair",
        price=25.0,
        duration_minutes=30,
        barbershop_id=barbershop.id,
    )
    service = service_repo.create(service_data)

    result = service_service.delete_service(service.id, barbershop.id)
    assert result is True

    deleted = service_repo.get_by_id(service.id)
    assert deleted is None


def test_delete_service_not_found(db):
    service_repo = ServiceRepository(db)
    barbershop_repo = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        service_service.delete_service(999, 1)

    assert exc_info.value.status_code == 404
    assert "Service not found" in exc_info.value.detail


def test_delete_service_access_denied(db):
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

    service_repo = ServiceRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo_test)

    service_data = ServiceCreate(
        name="Haircut",
        description="Classic haircut",
        category="Hair",
        price=25.0,
        duration_minutes=30,
        barbershop_id=barbershop1.id,
    )
    service = service_repo.create(service_data)

    with pytest.raises(HTTPException) as exc_info:
        service_service.delete_service(service.id, barbershop2.id)

    assert exc_info.value.status_code == 403
    assert "Access denied" in exc_info.value.detail
