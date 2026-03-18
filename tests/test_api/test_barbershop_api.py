import pytest


def test_create_barbershop(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    response = client.post(
        "/api/barbershops/",
        json={
            "name": "Test Barbershop",
            "address": "123 Main St",
            "phone": "123456789",
            "owner_id": owner_id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Barbershop"
    assert data["owner_id"] == owner_id


def test_get_all_barbershops(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    client.post(
        "/api/barbershops/",
        json={
            "name": "Shop 1",
            "address": "1 Main St",
            "phone": "123456789",
            "owner_id": owner_id,
        },
    )
    client.post(
        "/api/barbershops/",
        json={
            "name": "Shop 2",
            "address": "2 Main St",
            "phone": "987654321",
            "owner_id": owner_id,
        },
    )

    response = client.get(f"/api/barbershops/?owner_id={owner_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_barbershop(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    create_response = client.post(
        "/api/barbershops/",
        json={
            "name": "Test Barbershop",
            "address": "123 Main St",
            "phone": "123456789",
            "owner_id": owner_id,
        },
    )
    barbershop_id = create_response.json()["id"]

    response = client.get(f"/api/barbershops/{barbershop_id}?owner_id={owner_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == barbershop_id


def test_get_barbershop_not_found(client):
    response = client.get("/api/barbershops/999?owner_id=1")
    assert response.status_code == 404


def test_get_barbershop_access_denied(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    other_user_response = client.post(
        "/api/users/",
        json={
            "email": "other@example.com",
            "full_name": "Other",
            "password": "pass456",
        },
    )
    other_id = other_user_response.json()["id"]

    create_response = client.post(
        "/api/barbershops/",
        json={
            "name": "Test Barbershop",
            "address": "123 Main St",
            "phone": "123456789",
            "owner_id": owner_id,
        },
    )
    barbershop_id = create_response.json()["id"]

    response = client.get(f"/api/barbershops/{barbershop_id}?owner_id={other_id}")
    assert response.status_code == 403


def test_update_barbershop(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    create_response = client.post(
        "/api/barbershops/",
        json={
            "name": "Test Barbershop",
            "address": "123 Main St",
            "phone": "123456789",
            "owner_id": owner_id,
        },
    )
    barbershop_id = create_response.json()["id"]

    response = client.put(
        f"/api/barbershops/{barbershop_id}?owner_id={owner_id}",
        json={"name": "Updated Barbershop"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Barbershop"


def test_update_barbershop_not_found(client):
    response = client.put(
        "/api/barbershops/999?owner_id=1", json={"name": "Updated Barbershop"}
    )
    assert response.status_code == 404


def test_delete_barbershop(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    create_response = client.post(
        "/api/barbershops/",
        json={
            "name": "Test Barbershop",
            "address": "123 Main St",
            "phone": "123456789",
            "owner_id": owner_id,
        },
    )
    barbershop_id = create_response.json()["id"]

    response = client.delete(f"/api/barbershops/{barbershop_id}?owner_id={owner_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


def test_delete_barbershop_not_found(client):
    response = client.delete("/api/barbershops/999?owner_id=1")
    assert response.status_code == 404


def test_restore_barbershop(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    create_response = client.post(
        "/api/barbershops/",
        json={
            "name": "Test Barbershop",
            "address": "123 Main St",
            "phone": "123456789",
            "owner_id": owner_id,
        },
    )
    barbershop_id = create_response.json()["id"]

    client.delete(f"/api/barbershops/{barbershop_id}?owner_id={owner_id}")

    response = client.post(
        f"/api/barbershops/{barbershop_id}/restore?owner_id={owner_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == barbershop_id


def test_restore_barbershop_not_found(client):
    response = client.post("/api/barbershops/999/restore?owner_id=1")
    assert response.status_code == 404


def test_restore_barbershop_access_denied(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    other_user_response = client.post(
        "/api/users/",
        json={
            "email": "other@example.com",
            "full_name": "Other",
            "password": "pass456",
        },
    )
    other_id = other_user_response.json()["id"]

    create_response = client.post(
        "/api/barbershops/",
        json={
            "name": "Test Barbershop",
            "address": "123 Main St",
            "phone": "123456789",
            "owner_id": owner_id,
        },
    )
    barbershop_id = create_response.json()["id"]

    client.delete(f"/api/barbershops/{barbershop_id}?owner_id={owner_id}")

    response = client.post(
        f"/api/barbershops/{barbershop_id}/restore?owner_id={other_id}"
    )
    assert response.status_code == 403
