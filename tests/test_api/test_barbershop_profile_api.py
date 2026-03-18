import pytest


def test_create_profile(client):
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
        "/api/barbershop-profiles/",
        json={
            "description": "Test description",
            "services": "Test services",
            "logo_url": "http://logo.com",
            "banner_url": "http://banner.com",
            "barbershop_id": barbershop_id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Test description"
    assert data["barbershop_id"] == barbershop_id


def test_get_profile_by_barbershop(client):
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

    profile_response = client.post(
        "/api/barbershop-profiles/",
        json={
            "description": "Test description",
            "services": "Test services",
            "barbershop_id": barbershop_id,
        },
    )
    profile_id = profile_response.json()["id"]

    response = client.get(f"/api/barbershop-profiles/barbershop/{barbershop_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == profile_id


def test_get_profile_by_barbershop_not_found(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    response = client.get(f"/api/barbershop-profiles/barbershop/999")
    assert response.status_code == 404


def test_update_profile(client):
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

    profile_response = client.post(
        "/api/barbershop-profiles/",
        json={
            "description": "Test description",
            "services": "Test services",
            "barbershop_id": barbershop_id,
        },
    )
    profile_id = profile_response.json()["id"]

    response = client.put(
        f"/api/barbershop-profiles/{profile_id}?barbershop_id={barbershop_id}",
        json={"description": "Updated description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description"


def test_update_profile_not_found(client):
    user_response = client.post(
        "/api/users/",
        json={
            "email": "owner@example.com",
            "full_name": "Owner",
            "password": "pass123",
        },
    )
    owner_id = user_response.json()["id"]

    response = client.put(
        f"/api/barbershop-profiles/999?barbershop_id={owner_id}",
        json={"description": "Updated description"},
    )
    assert response.status_code == 404


def test_delete_profile(client):
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

    profile_response = client.post(
        "/api/barbershop-profiles/",
        json={
            "description": "Test description",
            "services": "Test services",
            "barbershop_id": barbershop_id,
        },
    )
    profile_id = profile_response.json()["id"]

    response = client.delete(
        f"/api/barbershop-profiles/{profile_id}?barbershop_id={barbershop_id}"
    )
    assert response.status_code == 200
    assert "deleted successfully" in response.json()["message"]


def test_restore_profile(client):
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

    profile_response = client.post(
        "/api/barbershop-profiles/",
        json={
            "description": "Test description",
            "services": "Test services",
            "barbershop_id": barbershop_id,
        },
    )
    profile_id = profile_response.json()["id"]

    client.delete(
        f"/api/barbershop-profiles/{profile_id}?barbershop_id={barbershop_id}"
    )

    response = client.post(
        f"/api/barbershop-profiles/{profile_id}/restore?barbershop_id={barbershop_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == profile_id
