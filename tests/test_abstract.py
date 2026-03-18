import pytest
from unittest.mock import MagicMock


def test_abstract_user_repository_methods(db):
    from app.repositories.user_repository import IUserRepository

    class MockUserRepository(IUserRepository):
        def get_by_email(self, email: str):
            return None

        def get_by_id(self, id: int):
            return None

        def get_all(self, skip: int = 0, limit: int = 100):
            return []

        def create(self, user):
            return None

        def update(self, id: int, user):
            return None

        def soft_delete(self, id: int):
            return False

        def restore(self, id: int):
            return None

    mock_repo = MockUserRepository()
    assert mock_repo.get_by_email("test") is None
    assert mock_repo.get_by_id(1) is None
    assert mock_repo.get_all() == []
    assert mock_repo.create(None) is None
    assert mock_repo.update(1, None) is None
    assert mock_repo.soft_delete(1) is False
    assert mock_repo.restore(1) is None


def test_abstract_barbershop_repository_methods(db):
    from app.repositories.barbershop_repository import IBarberShopRepository

    class MockBarberShopRepository(IBarberShopRepository):
        def get_by_id(self, id: int):
            return None

        def get_by_owner(self, owner_id: int, skip: int = 0, limit: int = 100):
            return []

        def create(self, barbershop):
            return None

        def update(self, id: int, barbershop):
            return None

        def soft_delete(self, id: int):
            return False

        def restore(self, id: int):
            return None

    mock_repo = MockBarberShopRepository()
    assert mock_repo.get_by_id(1) is None
    assert mock_repo.get_by_owner(1) == []
    assert mock_repo.create(None) is None
    assert mock_repo.update(1, None) is None
    assert mock_repo.soft_delete(1) is False
    assert mock_repo.restore(1) is None
