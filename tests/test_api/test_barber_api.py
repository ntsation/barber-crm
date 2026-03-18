import pytest
from fastapi.testclient import TestClient
from app.repositories.user_repository import UserRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.barber_repository import BarberRepository
from app.schemas.user import UserCreate
from app.schemas.barbershop import BarberShopCreate
from app.schemas.barber import BarberCreate


def test_create_barber(client, db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_data = {
        "name": "John Doe",
        "specialty": "Haircuts",
        "barbershop_id": barbershop.id,
    }

    response = client.post("/api/barbers/", json=barber_data)
    assert response.status_code == 201

    data = response.json()
    assert data["name"] == "John Doe"


def test_create_barber_invalid_barbershop(client, db):
    barber_data = {
        "name": "John Doe",
        "specialty": "Haircuts",
        "barbershop_id": 999,
    }

    response = client.post("/api/barbers/", json=barber_data)
    assert response.status_code == 404
    assert "Barbershop not found" in response.json()["detail"]


def test_get_barber(client, db):
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

    response = client.get(f"/api/barbers/{barber.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == barber.id


def test_get_barber_not_found(client, db):
    response = client.get("/api/barbers/999")
    assert response.status_code == 404
    assert "Barber not found" in response.json()["detail"]


def test_get_barbershop_barbers(client, db):
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

    response = client.get(f"/api/barbers/barbershop/{barbershop.id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2


def test_get_barbershop_barbers_active_only(client, db):
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

    response = client.get(f"/api/barbers/barbershop/{barbershop.id}?active_only=true")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1


def test_get_barbershop_barbers_invalid_barbershop(client, db):
    response = client.get("/api/barbers/barbershop/999")
    assert response.status_code == 404
    assert "Barbershop not found" in response.json()["detail"]


def test_get_barber_by_user(client, db):
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

    response = client.get(f"/api/barbers/user/{barber_user.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == barber.id
    assert data["name"] == "Barber Name"


def test_update_barber(client, db):
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

    update_data = {"name": "John Updated"}

    response = client.put(
        f"/api/barbers/{barber.id}?barbershop_id={barbershop.id}",
        json=update_data,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "John Updated"


def test_update_barber_not_found(client, db):
    update_data = {"name": "Updated"}

    response = client.put("/api/barbers/999?barbershop_id=1", json=update_data)
    assert response.status_code == 404
    assert "Barber not found" in response.json()["detail"]


def test_update_barber_access_denied(client, db):
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

    update_data = {"name": "Updated"}

    response = client.put(
        f"/api/barbers/{barber.id}?barbershop_id={barbershop2.id}",
        json=update_data,
    )
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_delete_barber(client, db):
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

    response = client.delete(f"/api/barbers/{barber.id}?barbershop_id={barbershop.id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


def test_delete_barber_not_found(client, db):
    response = client.delete("/api/barbers/999?barbershop_id=1")
    assert response.status_code == 404
    assert "Barber not found" in response.json()["detail"]


def test_delete_barber_access_denied(client, db):
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

    response = client.delete(f"/api/barbers/{barber.id}?barbershop_id={barbershop2.id}")
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]
