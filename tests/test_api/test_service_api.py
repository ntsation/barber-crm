import pytest
from fastapi.testclient import TestClient
from app.repositories.user_repository import UserRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.service_repository import ServiceRepository
from app.schemas.user import UserCreate
from app.schemas.barbershop import BarberShopCreate
from app.schemas.service import ServiceCreate


def test_create_service(client, db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    service_data = {
        "name": "Haircut",
        "description": "Classic haircut",
        "category": "Hair",
        "price": 25.0,
        "duration_minutes": 30,
        "barbershop_id": barbershop.id,
    }

    response = client.post("/api/services/", json=service_data)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "Haircut"
    assert data["price"] == 25.0
    assert data["id"] is not None


def test_create_service_invalid_barbershop(client, db):
    service_data = {
        "name": "Haircut",
        "description": "Classic haircut",
        "category": "Hair",
        "price": 25.0,
        "duration_minutes": 30,
        "barbershop_id": 999,
    }

    response = client.post("/api/services/", json=service_data)
    assert response.status_code == 404
    assert "Barbershop not found" in response.json()["detail"]


def test_get_service(client, db):
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

    response = client.get(f"/api/services/{service.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == service.id
    assert data["name"] == "Haircut"


def test_get_service_not_found(client, db):
    response = client.get("/api/services/999")
    assert response.status_code == 404
    assert "Service not found" in response.json()["detail"]


def test_get_barbershop_services(client, db):
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

    response = client.get(f"/api/services/barbershop/{barbershop.id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2


def test_get_barbershop_services_with_category(client, db):
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

    response = client.get(f"/api/services/barbershop/{barbershop.id}?category=Hair")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["category"] == "Hair"


def test_get_barbershop_services_active_only(client, db):
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

    response = client.get(f"/api/services/barbershop/{barbershop.id}?active_only=true")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Haircut"
    assert data[0]["is_active"] is True


def test_get_barbershop_services_invalid_barbershop(client, db):
    response = client.get("/api/services/barbershop/999")
    assert response.status_code == 404
    assert "Barbershop not found" in response.json()["detail"]


def test_get_barbershop_services_active_only_invalid_barbershop(client, db):
    response = client.get("/api/services/barbershop/999?active_only=true")
    assert response.status_code == 404
    assert "Barbershop not found" in response.json()["detail"]


def test_get_barbershop_services_category_invalid_barbershop(client, db):
    response = client.get("/api/services/barbershop/999?category=Hair")
    assert response.status_code == 404
    assert "Barbershop not found" in response.json()["detail"]


def test_update_service(client, db):
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

    update_data = {
        "name": "Premium Haircut",
        "price": 35.0,
        "duration_minutes": 45,
    }

    response = client.put(
        f"/api/services/{service.id}?barbershop_id={barbershop.id}",
        json=update_data,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Premium Haircut"
    assert data["price"] == 35.0


def test_update_service_not_found(client, db):
    update_data = {"name": "Updated"}

    response = client.put("/api/services/999?barbershop_id=1", json=update_data)
    assert response.status_code == 404
    assert "Service not found" in response.json()["detail"]


def test_update_service_access_denied(client, db):
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
    service_data = ServiceCreate(
        name="Haircut",
        description="Classic haircut",
        category="Hair",
        price=25.0,
        duration_minutes=30,
        barbershop_id=barbershop1.id,
    )
    service = service_repo.create(service_data)

    update_data = {"name": "Updated"}

    response = client.put(
        f"/api/services/{service.id}?barbershop_id={barbershop2.id}",
        json=update_data,
    )
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_delete_service(client, db):
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

    response = client.delete(
        f"/api/services/{service.id}?barbershop_id={barbershop.id}"
    )
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]

    deleted = service_repo.get_by_id(service.id)
    assert deleted is None


def test_delete_service_not_found(client, db):
    response = client.delete("/api/services/999?barbershop_id=1")
    assert response.status_code == 404
    assert "Service not found" in response.json()["detail"]


def test_delete_service_access_denied(client, db):
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
    service_data = ServiceCreate(
        name="Haircut",
        description="Classic haircut",
        category="Hair",
        price=25.0,
        duration_minutes=30,
        barbershop_id=barbershop1.id,
    )
    service = service_repo.create(service_data)

    response = client.delete(
        f"/api/services/{service.id}?barbershop_id={barbershop2.id}"
    )
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]
