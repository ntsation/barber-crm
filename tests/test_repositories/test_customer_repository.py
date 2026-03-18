import pytest
from app.repositories.customer_repository import CustomerRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.user_repository import UserRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.schemas.user import UserCreate
from app.schemas.barbershop import BarberShopCreate


def test_create_customer(db):
    user_repo = UserRepository(db)
    user_data = UserCreate(
        email="owner@example.com", full_name="Owner", password="pass123"
    )
    owner = user_repo.create(user_data)

    barbershop_repo = BarberShopRepository(db)
    barbershop_data = BarberShopCreate(
        name="Shop", address="123 St", phone="123456", owner_id=owner.id
    )
    barbershop = barbershop_repo.create(barbershop_data)

    customer_repo = CustomerRepository(db)
    customer_data = CustomerCreate(
        name="John Doe",
        email="john@example.com",
        phone="987654321",
        barbershop_id=barbershop.id,
    )
    customer = customer_repo.create(customer_data)

    assert customer.id is not None
    assert customer.name == "John Doe"
    assert customer.email == "john@example.com"
    assert customer.phone == "987654321"
    assert customer.barbershop_id == barbershop.id


def test_get_customer_by_id(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    customer = customer_repo.create(
        CustomerCreate(
            name="John",
            email="john@example.com",
            phone="123",
            barbershop_id=barbershop.id,
        )
    )

    found_customer = customer_repo.get_by_id(customer.id)

    assert found_customer is not None
    assert found_customer.id == customer.id


def test_get_customers_by_barbershop(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    customer_repo.create(
        CustomerCreate(
            name="John",
            email="john@example.com",
            phone="123",
            barbershop_id=barbershop.id,
        )
    )
    customer_repo.create(
        CustomerCreate(
            name="Jane",
            email="jane@example.com",
            phone="456",
            barbershop_id=barbershop.id,
        )
    )

    customers = customer_repo.get_by_barbershop(barbershop.id)

    assert len(customers) == 2


def test_update_customer(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    customer = customer_repo.create(
        CustomerCreate(
            name="John",
            email="john@example.com",
            phone="123",
            barbershop_id=barbershop.id,
        )
    )

    update_data = CustomerUpdate(name="John Updated")
    updated_customer = customer_repo.update(customer.id, update_data)

    assert updated_customer.name == "John Updated"


def test_update_nonexistent_customer(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    update_data = CustomerUpdate(name="John Updated")
    updated_customer = customer_repo.update(999, update_data)

    assert updated_customer is None


def test_soft_delete_customer(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    customer = customer_repo.create(
        CustomerCreate(
            name="John",
            email="john@example.com",
            phone="123",
            barbershop_id=barbershop.id,
        )
    )

    result = customer_repo.soft_delete(customer.id)

    assert result is True

    deleted_customer = customer_repo.get_by_id(customer.id)
    assert deleted_customer is None


def test_soft_delete_nonexistent_customer(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    result = customer_repo.soft_delete(999)

    assert result is False


def test_restore_customer(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    customer = customer_repo.create(
        CustomerCreate(
            name="John",
            email="john@example.com",
            phone="123",
            barbershop_id=barbershop.id,
        )
    )

    customer_repo.soft_delete(customer.id)
    restored_customer = customer_repo.restore(customer.id)

    assert restored_customer.is_active is True
    assert restored_customer.deleted_at is None


def test_restore_nonexistent_customer(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    restored_customer = customer_repo.restore(999)

    assert restored_customer is None
