import pytest
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User as UserModel


def test_create_user(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="test@example.com", full_name="Test User", password="password123"
    )
    user = user_repo.create(user_data)

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.is_active is True
    assert user.deleted_at is None


def test_get_user_by_email(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="test@example.com", full_name="Test User", password="password123"
    )
    created_user = user_repo.create(user_data)

    user = user_repo.get_by_email("test@example.com")

    assert user is not None
    assert user.email == "test@example.com"


def test_get_user_by_id(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="test@example.com", full_name="Test User", password="password123"
    )
    created_user = user_repo.create(user_data)

    user = user_repo.get_by_id(created_user.id)

    assert user is not None
    assert user.id == created_user.id


def test_get_all_users(db):
    user_repo = UserRepository(db)

    user_repo.create(
        UserCreate(email="user1@example.com", full_name="User 1", password="pass123")
    )
    user_repo.create(
        UserCreate(email="user2@example.com", full_name="User 2", password="pass456")
    )

    users = user_repo.get_all()

    assert len(users) == 2


def test_update_user(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="test@example.com", full_name="Test User", password="password123"
    )
    created_user = user_repo.create(user_data)

    update_data = UserUpdate(full_name="Updated User")
    updated_user = user_repo.update(created_user.id, update_data)

    assert updated_user.full_name == "Updated User"


def test_update_user_email(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="test@example.com", full_name="Test User", password="password123"
    )
    created_user = user_repo.create(user_data)

    update_data = UserUpdate(email="newemail@example.com")
    updated_user = user_repo.update(created_user.id, update_data)

    assert updated_user.email == "newemail@example.com"


def test_soft_delete_user(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="test@example.com", full_name="Test User", password="password123"
    )
    created_user = user_repo.create(user_data)

    result = user_repo.soft_delete(created_user.id)

    assert result is True

    deleted_user = user_repo.get_by_id(created_user.id)
    assert deleted_user is None


def test_restore_user(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="test@example.com", full_name="Test User", password="password123"
    )
    created_user = user_repo.create(user_data)

    user_repo.soft_delete(created_user.id)
    restored_user = user_repo.restore(created_user.id)

    assert restored_user.is_active is True
    assert restored_user.deleted_at is None


def test_get_nonexistent_user(db):
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(999)

    assert user is None


def test_update_nonexistent_user(db):
    user_repo = UserRepository(db)
    update_data = UserUpdate(full_name="Updated User")
    updated_user = user_repo.update(999, update_data)

    assert updated_user is None


def test_soft_delete_nonexistent_user(db):
    user_repo = UserRepository(db)
    result = user_repo.soft_delete(999)

    assert result is False


def test_restore_nonexistent_user(db):
    user_repo = UserRepository(db)
    restored_user = user_repo.restore(999)

    assert restored_user is None
