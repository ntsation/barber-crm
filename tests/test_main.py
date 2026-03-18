import pytest


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "Barber CRM API is running" in data["message"]


def test_get_db_dependency(client):
    from app.db.session import get_db

    generator = get_db()
    db = next(generator)
    assert db is not None
    next(generator, None)
