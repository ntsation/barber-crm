import pytest
from abc import ABC, abstractmethod


def test_user_repository_is_abstract(db):
    from app.repositories.user_repository import IUserRepository

    assert issubclass(IUserRepository, ABC)
    assert hasattr(IUserRepository, "__abstractmethods__")


def test_barbershop_repository_is_abstract(db):
    from app.repositories.barbershop_repository import IBarberShopRepository

    assert issubclass(IBarberShopRepository, ABC)
    assert hasattr(IBarberShopRepository, "__abstractmethods__")


def test_base_class_tablename(db):
    from app.db.base_class import Base

    assert hasattr(Base, "__tablename__")
