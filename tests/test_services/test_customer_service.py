import pytest
from fastapi import HTTPException
from app.services.customer_service import CustomerService
from app.repositories.customer_repository import CustomerRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.user_repository import UserRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.schemas.user import UserCreate
from app.schemas.barbershop import BarberShopCreate


def test_create_customer(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo_test)

    customer_data = CustomerCreate(
        name="John", email="john@example.com", phone="123", barbershop_id=barbershop.id
    )
    customer = customer_service.create_customer(customer_data)

    assert customer.name == "John"


def test_create_customer_invalid_barbershop(db):
    customer_repo = CustomerRepository(db)
    barbershop_repo = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo)

    customer_data = CustomerCreate(
        name="John", email="john@example.com", phone="123", barbershop_id=999
    )

    with pytest.raises(HTTPException) as exc_info:
        customer_service.create_customer(customer_data)

    assert exc_info.value.status_code == 404


def test_create_customer_duplicate_email(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo_test)

    customer_repo.create(
        CustomerCreate(
            name="John",
            email="john@example.com",
            phone="123",
            barbershop_id=barbershop.id,
        )
    )

    customer_data = CustomerCreate(
        name="Jane", email="john@example.com", phone="456", barbershop_id=barbershop.id
    )

    with pytest.raises(HTTPException) as exc_info:
        customer_service.create_customer(customer_data)

    assert exc_info.value.status_code == 400


def test_get_customer(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo_test)

    customer = customer_repo.create(
        CustomerCreate(
            name="John",
            email="john@example.com",
            phone="123",
            barbershop_id=barbershop.id,
        )
    )

    found_customer = customer_service.get_customer(customer.id, barbershop.id)

    assert found_customer.id == customer.id


def test_get_customer_not_found(db):
    customer_repo = CustomerRepository(db)
    barbershop_repo = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        customer_service.get_customer(999, 1)

    assert exc_info.value.status_code == 404


def test_get_customer_access_denied(db):
    user_repo = UserRepository(db)
    owner1 = user_repo.create(
        UserCreate(email="owner1@example.com", full_name="Owner 1", password="pass")
    )
    owner2 = user_repo.create(
        UserCreate(email="owner2@example.com", full_name="Owner 2", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop1 = barbershop_repo.create(
        BarberShopCreate(name="Shop 1", address="123", phone="123", owner_id=owner1.id)
    )
    barbershop2 = barbershop_repo.create(
        BarberShopCreate(name="Shop 2", address="456", phone="456", owner_id=owner2.id)
    )

    customer_repo = CustomerRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo_test)

    customer = customer_repo.create(
        CustomerCreate(
            name="John",
            email="john@example.com",
            phone="123",
            barbershop_id=barbershop1.id,
        )
    )

    with pytest.raises(HTTPException) as exc_info:
        customer_service.get_customer(customer.id, barbershop2.id)

    assert exc_info.value.status_code == 403


def test_get_barbershop_customers(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo_test)

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

    customers = customer_service.get_barbershop_customers(barbershop.id)

    assert len(customers) == 2


def test_get_barbershop_customers_invalid_barbershop(db):
    customer_repo = CustomerRepository(db)
    barbershop_repo = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo)

    with pytest.raises(HTTPException) as exc_info:
        customer_service.get_barbershop_customers(999)

    assert exc_info.value.status_code == 404


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
    barbershop_repo_test = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo_test)

    customer = customer_repo.create(
        CustomerCreate(
            name="John",
            email="john@example.com",
            phone="123",
            barbershop_id=barbershop.id,
        )
    )

    update_data = CustomerUpdate(name="John Updated")
    updated_customer = customer_service.update_customer(
        customer.id, update_data, barbershop.id
    )

    assert updated_customer.name == "John Updated"


def test_update_customer_duplicate_email(db):
    user_repo = UserRepository(db)
    owner = user_repo.create(
        UserCreate(email="owner@example.com", full_name="Owner", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop = barbershop_repo.create(
        BarberShopCreate(name="Shop", address="123", phone="123", owner_id=owner.id)
    )

    customer_repo = CustomerRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo_test)

    customer_repo.create(
        CustomerCreate(
            name="John",
            email="john@example.com",
            phone="123",
            barbershop_id=barbershop.id,
        )
    )
    customer = customer_repo.create(
        CustomerCreate(
            name="Jane",
            email="jane@example.com",
            phone="456",
            barbershop_id=barbershop.id,
        )
    )

    update_data = CustomerUpdate(email="john@example.com")

    with pytest.raises(HTTPException) as exc_info:
        customer_service.update_customer(customer.id, update_data, barbershop.id)

    assert exc_info.value.status_code == 400


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
    barbershop_repo_test = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo_test)

    customer = customer_repo.create(
        CustomerCreate(
            name="John",
            email="john@example.com",
            phone="123",
            barbershop_id=barbershop.id,
        )
    )

    result = customer_service.soft_delete_customer(customer.id, barbershop.id)

    assert result is True


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
    barbershop_repo_test = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo_test)

    customer = customer_repo.create(
        CustomerCreate(
            name="John",
            email="john@example.com",
            phone="123",
            barbershop_id=barbershop.id,
        )
    )

    customer_service.soft_delete_customer(customer.id, barbershop.id)
    restored_customer = customer_service.restore_customer(customer.id, barbershop.id)

    assert restored_customer.is_active is True


def test_restore_customer_access_denied(db):
    user_repo = UserRepository(db)
    owner1 = user_repo.create(
        UserCreate(email="owner1@example.com", full_name="Owner 1", password="pass")
    )
    owner2 = user_repo.create(
        UserCreate(email="owner2@example.com", full_name="Owner 2", password="pass")
    )

    barbershop_repo = BarberShopRepository(db)
    barbershop1 = barbershop_repo.create(
        BarberShopCreate(name="Shop 1", address="123", phone="123", owner_id=owner1.id)
    )
    barbershop2 = barbershop_repo.create(
        BarberShopCreate(name="Shop 2", address="456", phone="456", owner_id=owner2.id)
    )

    customer_repo = CustomerRepository(db)
    barbershop_repo_test = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo_test)

    customer = customer_repo.create(
        CustomerCreate(
            name="John",
            email="john@example.com",
            phone="123",
            barbershop_id=barbershop1.id,
        )
    )

    customer_service.soft_delete_customer(customer.id, barbershop1.id)

    with pytest.raises(HTTPException) as exc_info:
        customer_service.restore_customer(customer.id, barbershop2.id)

    assert exc_info.value.status_code == 403


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
    barbershop_repo_test = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo_test)

    with pytest.raises(HTTPException) as exc_info:
        customer_service.restore_customer(999, barbershop.id)

    assert exc_info.value.status_code == 404
