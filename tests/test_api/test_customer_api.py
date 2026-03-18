import pytest


def test_create_customer(client):
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
        "/api/customers/",
        json={
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "987654321",
            "barbershop_id": barbershop_id,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["barbershop_id"] == barbershop_id


def test_get_all_customers(client):
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
        "/api/customers/",
        json={
            "name": "John",
            "email": "john@example.com",
            "phone": "123",
            "barbershop_id": barbershop_id,
        },
    )
    client.post(
        "/api/customers/",
        json={
            "name": "Jane",
            "email": "jane@example.com",
            "phone": "456",
            "barbershop_id": barbershop_id,
        },
    )

    response = client.get(f"/api/customers/?barbershop_id={barbershop_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_get_customer(client):
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

    create_response = client.post(
        "/api/customers/",
        json={
            "name": "John",
            "email": "john@example.com",
            "phone": "123",
            "barbershop_id": barbershop_id,
        },
    )
    customer_id = create_response.json()["id"]

    response = client.get(f"/api/customers/{customer_id}?barbershop_id={barbershop_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == customer_id


def test_update_customer(client):
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

    create_response = client.post(
        "/api/customers/",
        json={
            "name": "John",
            "email": "john@example.com",
            "phone": "123",
            "barbershop_id": barbershop_id,
        },
    )
    customer_id = create_response.json()["id"]

    response = client.put(
        f"/api/customers/{customer_id}?barbershop_id={barbershop_id}",
        json={"name": "John Updated"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "John Updated"


def test_delete_customer(client):
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

    create_response = client.post(
        "/api/customers/",
        json={
            "name": "John",
            "email": "john@example.com",
            "phone": "123",
            "barbershop_id": barbershop_id,
        },
    )
    customer_id = create_response.json()["id"]

    response = client.delete(
        f"/api/customers/{customer_id}?barbershop_id={barbershop_id}"
    )
    assert response.status_code == 200


def test_restore_customer(client):
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

    create_response = client.post(
        "/api/customers/",
        json={
            "name": "John",
            "email": "john@example.com",
            "phone": "123",
            "barbershop_id": barbershop_id,
        },
    )
    customer_id = create_response.json()["id"]

    client.delete(f"/api/customers/{customer_id}?barbershop_id={barbershop_id}")

    response = client.post(
        f"/api/customers/{customer_id}/restore?barbershop_id={barbershop_id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == customer_id
