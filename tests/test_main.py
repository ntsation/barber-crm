import pytest


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "name" in data
    assert "version" in data
    assert "docs" in data
    assert "health" in data


def test_get_db_dependency(client):
    from app.db.session import get_db

    generator = get_db()
    db = next(generator)
    assert db is not None
    next(generator, None)
