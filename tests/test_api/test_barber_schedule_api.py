import pytest
from fastapi.testclient import TestClient
from app.repositories.user_repository import UserRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.barber_repository import BarberRepository
from app.repositories.barber_schedule_repository import BarberScheduleRepository
from app.schemas.user import UserCreate
from app.schemas.barbershop import BarberShopCreate
from app.schemas.barber import BarberCreate
from app.schemas.barber_schedule import BarberScheduleCreate


def test_create_schedule(client, db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(BarberCreate(name="John", barbershop_id=barbershop.id))

    schedule_data = {
        "barber_id": barber.id,
        "day_of_week": 1,
        "start_time": "09:00",
        "end_time": "18:00",
    }

    response = client.post("/api/barber-schedules/", json=schedule_data)
    assert response.status_code == 201

    data = response.json()
    assert data["day_of_week"] == 1


def test_create_schedule_invalid_barber(client, db):
    schedule_data = {
        "barber_id": 999,
        "day_of_week": 1,
        "start_time": "09:00",
        "end_time": "18:00",
    }

    response = client.post("/api/barber-schedules/", json=schedule_data)
    assert response.status_code == 404
    assert "Barber not found" in response.json()["detail"]


def test_get_schedule(client, db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(BarberCreate(name="John", barbershop_id=barbershop.id))

    schedule_repo = BarberScheduleRepository(db)
    schedule_data = BarberScheduleCreate(
        barber_id=barber.id,
        day_of_week=1,
        start_time="09:00",
        end_time="18:00",
    )
    schedule = schedule_repo.create(schedule_data)

    response = client.get(f"/api/barber-schedules/{schedule.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == schedule.id


def test_get_schedule_not_found(client, db):
    response = client.get("/api/barber-schedules/999")
    assert response.status_code == 404
    assert "Schedule not found" in response.json()["detail"]


def test_get_barber_schedules(client, db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(BarberCreate(name="John", barbershop_id=barbershop.id))

    schedule_repo = BarberScheduleRepository(db)
    schedule_repo.create(
        BarberScheduleCreate(
            barber_id=barber.id,
            day_of_week=1,
            start_time="09:00",
            end_time="18:00",
        )
    )
    schedule_repo.create(
        BarberScheduleCreate(
            barber_id=barber.id,
            day_of_week=2,
            start_time="09:00",
            end_time="18:00",
        )
    )

    response = client.get(f"/api/barber-schedules/barber/{barber.id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2


def test_get_barber_schedules_available_only(client, db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(BarberCreate(name="John", barbershop_id=barbershop.id))

    schedule_repo = BarberScheduleRepository(db)
    schedule_repo.create(
        BarberScheduleCreate(
            barber_id=barber.id,
            day_of_week=1,
            start_time="09:00",
            end_time="18:00",
            is_available=True,
        )
    )
    schedule_repo.create(
        BarberScheduleCreate(
            barber_id=barber.id,
            day_of_week=2,
            start_time="09:00",
            end_time="18:00",
            is_available=False,
        )
    )

    response = client.get(
        f"/api/barber-schedules/barber/{barber.id}?available_only=true"
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1


def test_get_barber_schedules_invalid_barber(client, db):
    response = client.get("/api/barber-schedules/barber/999")
    assert response.status_code == 404
    assert "Barber not found" in response.json()["detail"]


def test_update_schedule(client, db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(BarberCreate(name="John", barbershop_id=barbershop.id))

    schedule_repo = BarberScheduleRepository(db)
    schedule_data = BarberScheduleCreate(
        barber_id=barber.id,
        day_of_week=1,
        start_time="09:00",
        end_time="18:00",
    )
    schedule = schedule_repo.create(schedule_data)

    update_data = {"start_time": "08:00"}

    response = client.put(
        f"/api/barber-schedules/{schedule.id}",
        json=update_data,
    )
    assert response.status_code == 200

    data = response.json()
    assert data["start_time"] == "08:00"


def test_update_schedule_not_found(client, db):
    update_data = {"start_time": "08:00"}

    response = client.put("/api/barber-schedules/999", json=update_data)
    assert response.status_code == 404
    assert "Schedule not found" in response.json()["detail"]


def test_delete_schedule(client, db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    barber_repo = BarberRepository(db)
    barber = barber_repo.create(BarberCreate(name="John", barbershop_id=barbershop.id))

    schedule_repo = BarberScheduleRepository(db)
    schedule_data = BarberScheduleCreate(
        barber_id=barber.id,
        day_of_week=1,
        start_time="09:00",
        end_time="18:00",
    )
    schedule = schedule_repo.create(schedule_data)

    response = client.delete(f"/api/barber-schedules/{schedule.id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


def test_delete_schedule_not_found(client, db):
    response = client.delete("/api/barber-schedules/999")
    assert response.status_code == 404
    assert "Schedule not found" in response.json()["detail"]
