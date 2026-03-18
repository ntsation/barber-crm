import pytest


def test_create_schedule(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    barbershop_response = client.post(
        "/api/barbershops/",
        json={"name": "Shop", "address": "123", "phone": "123", "owner_id": owner_id},
    )
    barbershop_id = barbershop_response.json()["id"]

    response = client.post(
        "/api/barbershop-schedules/",
        json={
            "barbershop_id": barbershop_id,
            "monday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "tuesday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "wednesday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "thursday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "friday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "saturday": {"enabled": False},
            "sunday": {"enabled": False},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["monday"]["enabled"] is True
    assert data["saturday"]["enabled"] is False


def test_get_schedule_by_barbershop(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    barbershop_response = client.post(
        "/api/barbershops/",
        json={"name": "Shop", "address": "123", "phone": "123", "owner_id": owner_id},
    )
    barbershop_id = barbershop_response.json()["id"]

    client.post(
        "/api/barbershop-schedules/",
        json={
            "barbershop_id": barbershop_id,
            "monday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "tuesday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "wednesday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "thursday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "friday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "saturday": {"enabled": False},
            "sunday": {"enabled": False},
        },
    )

    response = client.get(f"/api/barbershop-schedules/barbershop/{barbershop_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["saturday"]["enabled"] is False


def test_update_schedule(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    barbershop_response = client.post(
        "/api/barbershops/",
        json={"name": "Shop", "address": "123", "phone": "123", "owner_id": owner_id},
    )
    barbershop_id = barbershop_response.json()["id"]

    schedule_response = client.post(
        "/api/barbershop-schedules/",
        json={
            "barbershop_id": barbershop_id,
            "monday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "tuesday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "wednesday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "thursday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "friday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "saturday": {"enabled": False},
            "sunday": {"enabled": False},
        },
    )
    schedule_id = schedule_response.json()["id"]

    response = client.put(
        f"/api/barbershop-schedules/{schedule_id}?barbershop_id={barbershop_id}",
        json={"monday": {"enabled": False}},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["monday"]["enabled"] is False


def test_delete_schedule(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    barbershop_response = client.post(
        "/api/barbershops/",
        json={"name": "Shop", "address": "123", "phone": "123", "owner_id": owner_id},
    )
    barbershop_id = barbershop_response.json()["id"]

    schedule_response = client.post(
        "/api/barbershop-schedules/",
        json={
            "barbershop_id": barbershop_id,
            "monday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "tuesday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "wednesday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "thursday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "friday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "saturday": {"enabled": False},
            "sunday": {"enabled": False},
        },
    )
    schedule_id = schedule_response.json()["id"]

    response = client.delete(
        f"/api/barbershop-schedules/{schedule_id}?barbershop_id={barbershop_id}"
    )
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


def test_restore_schedule(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    barbershop_response = client.post(
        "/api/barbershops/",
        json={"name": "Shop", "address": "123", "phone": "123", "owner_id": owner_id},
    )
    barbershop_id = barbershop_response.json()["id"]

    schedule_response = client.post(
        "/api/barbershop-schedules/",
        json={
            "barbershop_id": barbershop_id,
            "monday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "tuesday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "wednesday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "thursday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "friday": {"enabled": True, "start_time": "09:00", "end_time": "18:00"},
            "saturday": {"enabled": False},
            "sunday": {"enabled": False},
        },
    )
    schedule_id = schedule_response.json()["id"]

    client.delete(
        f"/api/barbershop-schedules/{schedule_id}?barbershop_id={barbershop_id}"
    )

    response = client.post(
        f"/api/barbershop-schedules/{schedule_id}/restore?barbershop_id={barbershop_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["monday"]["enabled"] is True
    assert data["deleted_at"] is None


def test_create_settings(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    barbershop_response = client.post(
        "/api/barbershops/",
        json={"name": "Shop", "address": "123", "phone": "123", "owner_id": owner_id},
    )
    barbershop_id = barbershop_response.json()["id"]

    response = client.post(
        "/api/barbershop-settings/",
        json={
            "barbershop_id": barbershop_id,
            "accept_online_booking": True,
            "require_payment_confirmation": False,
            "advance_booking_hours": 2,
            "max_advance_booking_days": 30,
            "cancellation_hours": 24,
            "notification_email": "notify@email.com",
            "notification_phone": "11999999999",
            "default_duration_minutes": 60,
            "allow_walk_ins": True,
            "max_walk_ins_per_day": 5,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["accept_online_booking"] is True
    assert data["allow_walk_ins"] is True


def test_get_settings_by_barbershop(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    barbershop_response = client.post(
        "/api/barbershops/",
        json={"name": "Shop", "address": "123", "phone": "123", "owner_id": owner_id},
    )
    barbershop_id = barbershop_response.json()["id"]

    client.post(
        "/api/barbershop-settings/",
        json={
            "barbershop_id": barbershop_id,
            "accept_online_booking": True,
            "require_payment_confirmation": False,
            "advance_booking_hours": 2,
            "max_advance_booking_days": 30,
            "cancellation_hours": 24,
            "notification_email": "notify@email.com",
            "notification_phone": "11999999999",
            "default_duration_minutes": 60,
            "allow_walk_ins": True,
            "max_walk_ins_per_day": 5,
        },
    )

    response = client.get(f"/api/barbershop-settings/barbershop/{barbershop_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["max_advance_booking_days"] == 30


def test_update_settings(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    barbershop_response = client.post(
        "/api/barbershops/",
        json={"name": "Shop", "address": "123", "phone": "123", "owner_id": owner_id},
    )
    barbershop_id = barbershop_response.json()["id"]

    settings_response = client.post(
        "/api/barbershop-settings/",
        json={
            "barbershop_id": barbershop_id,
            "accept_online_booking": True,
            "require_payment_confirmation": False,
            "advance_booking_hours": 2,
            "max_advance_booking_days": 30,
            "cancellation_hours": 24,
            "notification_email": "notify@email.com",
            "notification_phone": "11999999999",
            "default_duration_minutes": 60,
            "allow_walk_ins": True,
            "max_walk_ins_per_day": 5,
        },
    )
    settings_id = settings_response.json()["id"]

    response = client.put(
        f"/api/barbershop-settings/{settings_id}?barbershop_id={barbershop_id}",
        json={"max_advance_booking_days": 60},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["max_advance_booking_days"] == 60


def test_delete_settings(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    barbershop_response = client.post(
        "/api/barbershops/",
        json={"name": "Shop", "address": "123", "phone": "123", "owner_id": owner_id},
    )
    barbershop_id = barbershop_response.json()["id"]

    settings_response = client.post(
        "/api/barbershop-settings/",
        json={
            "barbershop_id": barbershop_id,
            "accept_online_booking": True,
            "require_payment_confirmation": False,
            "advance_booking_hours": 2,
            "max_advance_booking_days": 30,
            "cancellation_hours": 24,
            "notification_email": "notify@email.com",
            "notification_phone": "11999999999",
            "default_duration_minutes": 60,
            "allow_walk_ins": True,
            "max_walk_ins_per_day": 5,
        },
    )
    settings_id = settings_response.json()["id"]

    response = client.delete(
        f"/api/barbershop-settings/{settings_id}?barbershop_id={barbershop_id}"
    )
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


def test_restore_settings(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    barbershop_response = client.post(
        "/api/barbershops/",
        json={"name": "Shop", "address": "123", "phone": "123", "owner_id": owner_id},
    )
    barbershop_id = barbershop_response.json()["id"]

    settings_response = client.post(
        "/api/barbershop-settings/",
        json={
            "barbershop_id": barbershop_id,
            "accept_online_booking": True,
            "require_payment_confirmation": False,
            "advance_booking_hours": 2,
            "max_advance_booking_days": 30,
            "cancellation_hours": 24,
            "notification_email": "notify@email.com",
            "notification_phone": "11999999999",
            "default_duration_minutes": 60,
            "allow_walk_ins": True,
            "max_walk_ins_per_day": 5,
        },
    )
    settings_id = settings_response.json()["id"]

    client.delete(
        f"/api/barbershop-settings/{settings_id}?barbershop_id={barbershop_id}"
    )

    response = client.post(
        f"/api/barbershop-settings/{settings_id}/restore?barbershop_id={barbershop_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is True
    assert data["deleted_at"] is None
