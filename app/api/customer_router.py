from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.customer import Customer, CustomerCreate, CustomerUpdate
from app.repositories.customer_repository import CustomerRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.services.customer_service import CustomerService

router = APIRouter()


@router.post("/", response_model=Customer)
def create_customer(customer_in: CustomerCreate, db: Session = Depends(get_db)):
    customer_repo = CustomerRepository(db)
    barbershop_repo = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo)
    return customer_service.create_customer(customer_in)


@router.get("/", response_model=List[Customer])
def list_customers(
    barbershop_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    customer_repo = CustomerRepository(db)
    barbershop_repo = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo)
    return customer_service.get_barbershop_customers(
        barbershop_id, skip=skip, limit=limit
    )


@router.get("/{customer_id}", response_model=Customer)
def get_customer(customer_id: int, barbershop_id: int, db: Session = Depends(get_db)):
    customer_repo = CustomerRepository(db)
    barbershop_repo = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo)
    return customer_service.get_customer(customer_id, barbershop_id)


@router.put("/{customer_id}", response_model=Customer)
def update_customer(
    customer_id: int,
    customer_in: CustomerUpdate,
    barbershop_id: int,
    db: Session = Depends(get_db),
):
    customer_repo = CustomerRepository(db)
    barbershop_repo = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo)
    return customer_service.update_customer(customer_id, customer_in, barbershop_id)


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int, barbershop_id: int, db: Session = Depends(get_db)
):
    customer_repo = CustomerRepository(db)
    barbershop_repo = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo)
    customer_service.soft_delete_customer(customer_id, barbershop_id)
    return {"message": "Customer deleted successfully"}


@router.post("/{customer_id}/restore", response_model=Customer)
def restore_customer(
    customer_id: int, barbershop_id: int, db: Session = Depends(get_db)
):
    customer_repo = CustomerRepository(db)
    barbershop_repo = BarberShopRepository(db)
    customer_service = CustomerService(customer_repo, barbershop_repo)
    return customer_service.restore_customer(customer_id, barbershop_id)
