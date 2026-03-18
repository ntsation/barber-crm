import pytest


def test_create_user(client):
    response = client.post(
        "/api/users/",
        json={
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data
    assert "password" not in data


def test_create_user_duplicate_email(client):
    client.post(
        "/api/users/",
        json={
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "password123",
        },
    )

    response = client.post(
        "/api/users/",
        json={
            "email": "test@example.com",
            "full_name": "Another User",
            "password": "password456",
        },
    )
    assert response.status_code == 400


def test_get_all_users(client):
    client.post(
        "/api/users/",
        json={
            "email": "user1@example.com",
            "full_name": "User 1",
            "password": "pass123",
        },
    )
    client.post(
        "/api/users/",
        json={
            "email": "user2@example.com",
            "full_name": "User 2",
            "password": "pass456",
        },
    )

    response = client.get("/api/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_user(client):
    create_response = client.post(
        "/api/users/",
        json={
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "password123",
        },
    )
    user_id = create_response.json()["id"]

    response = client.get(f"/api/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["email"] == "test@example.com"


def test_get_user_not_found(client):
    response = client.get("/api/users/999")
    assert response.status_code == 404


def test_update_user(client):
    create_response = client.post(
        "/api/users/",
        json={
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "password123",
        },
    )
    user_id = create_response.json()["id"]

    response = client.put(f"/api/users/{user_id}", json={"full_name": "Updated User"})
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated User"


def test_update_user_email_duplicate(client):
    client.post(
        "/api/users/",
        json={
            "email": "user1@example.com",
            "full_name": "User 1",
            "password": "pass123",
        },
    )
    create_response = client.post(
        "/api/users/",
        json={
            "email": "user2@example.com",
            "full_name": "User 2",
            "password": "pass456",
        },
    )
    user_id = create_response.json()["id"]

    response = client.put(f"/api/users/{user_id}", json={"email": "user1@example.com"})
    assert response.status_code == 400


def test_update_user_not_found(client):
    response = client.put("/api/users/999", json={"full_name": "Updated User"})
    assert response.status_code == 404


def test_delete_user(client):
    create_response = client.post(
        "/api/users/",
        json={
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "password123",
        },
    )
    user_id = create_response.json()["id"]

    response = client.delete(f"/api/users/{user_id}")
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


def test_delete_user_not_found(client):
    response = client.delete("/api/users/999")
    assert response.status_code == 404


def test_restore_user(client):
    create_response = client.post(
        "/api/users/",
        json={
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "password123",
        },
    )
    user_id = create_response.json()["id"]

    client.delete(f"/api/users/{user_id}")

    response = client.post(f"/api/users/{user_id}/restore")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id


def test_restore_user_not_found(client):
    response = client.post("/api/users/999/restore")
    assert response.status_code == 404
