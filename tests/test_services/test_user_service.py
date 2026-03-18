import pytest
from fastapi import HTTPException
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


def test_register_user(db):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    user_data = UserCreate(
        email="test@example.com", full_name="Test User", password="password123"
    )

    user = user_service.register_user(user_data)

    assert user.email == "test@example.com"
    assert user.full_name == "Test User"


def test_register_user_duplicate_email(db):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    user_data = UserCreate(
        email="test@example.com", full_name="Test User", password="password123"
    )

    user_service.register_user(user_data)

    with pytest.raises(HTTPException) as exc_info:
        user_service.register_user(user_data)

    assert exc_info.value.status_code == 400
    assert "already exists" in exc_info.value.detail


def test_get_user(db):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    user_data = UserCreate(
        email="test@example.com", full_name="Test User", password="password123"
    )
    created_user = user_repo.create(user_data)

    user = user_service.get_user(created_user.id)

    assert user.email == "test@example.com"


def test_get_user_not_found(db):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)

    with pytest.raises(HTTPException) as exc_info:
        user_service.get_user(999)

    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail


def test_get_all_users(db):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)

    user_repo.create(
        UserCreate(email="user1@example.com", full_name="User 1", password="pass123")
    )
    user_repo.create(
        UserCreate(email="user2@example.com", full_name="User 2", password="pass456")
    )

    users = user_service.get_all_users()

    assert len(users) == 2


def test_update_user(db):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    user_data = UserCreate(
        email="test@example.com", full_name="Test User", password="password123"
    )
    created_user = user_repo.create(user_data)

    update_data = UserUpdate(full_name="Updated User")
    updated_user = user_service.update_user(created_user.id, update_data)

    assert updated_user.full_name == "Updated User"


def test_update_user_duplicate_email(db):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)

    user_repo.create(
        UserCreate(email="user1@example.com", full_name="User 1", password="pass123")
    )
    user_data = UserCreate(
        email="user2@example.com", full_name="User 2", password="pass456"
    )
    created_user = user_repo.create(user_data)

    update_data = UserUpdate(email="user1@example.com")

    with pytest.raises(HTTPException) as exc_info:
        user_service.update_user(created_user.id, update_data)

    assert exc_info.value.status_code == 400


def test_update_user_not_found(db):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    update_data = UserUpdate(full_name="Updated User")

    with pytest.raises(HTTPException) as exc_info:
        user_service.update_user(999, update_data)

    assert exc_info.value.status_code == 404


def test_soft_delete_user(db):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    user_data = UserCreate(
        email="test@example.com", full_name="Test User", password="password123"
    )
    created_user = user_repo.create(user_data)

    result = user_service.soft_delete_user(created_user.id)

    assert result is True


def test_soft_delete_user_not_found(db):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)

    with pytest.raises(HTTPException) as exc_info:
        user_service.soft_delete_user(999)

    assert exc_info.value.status_code == 404


def test_restore_user(db):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)
    user_data = UserCreate(
        email="test@example.com", full_name="Test User", password="password123"
    )
    created_user = user_repo.create(user_data)

    user_service.soft_delete_user(created_user.id)
    restored_user = user_service.restore_user(created_user.id)

    assert restored_user.is_active is True


def test_restore_user_not_found(db):
    user_repo = UserRepository(db)
    user_service = UserService(user_repo)

    with pytest.raises(HTTPException) as exc_info:
        user_service.restore_user(999)

    assert exc_info.value.status_code == 404
