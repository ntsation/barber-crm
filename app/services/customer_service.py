from app.repositories.customer_repository import ICustomerRepository
from app.repositories.barbershop_repository import IBarberShopRepository
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.models.customer import Customer as CustomerModel
from fastapi import HTTPException


class CustomerService:
    def __init__(
        self, customer_repo: ICustomerRepository, barbershop_repo: IBarberShopRepository
    ):
        self.customer_repo = customer_repo
        self.barbershop_repo = barbershop_repo

    def create_customer(self, customer_in: CustomerCreate):
        barbershop = self.barbershop_repo.get_by_id(customer_in.barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        if customer_in.email:
            existing_customer = self.customer_repo.get_by_email(customer_in.email)
            if existing_customer:
                raise HTTPException(
                    status_code=400, detail="Customer email already registered"
                )
        return self.customer_repo.create(customer_in)

    def get_customer(self, id: int, barbershop_id: int) -> CustomerModel:
        customer = self.customer_repo.get_by_id(id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        if customer.barbershop_id != barbershop_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return customer

    def get_barbershop_customers(
        self, barbershop_id: int, skip: int = 0, limit: int = 100
    ):
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        return self.customer_repo.get_by_barbershop(
            barbershop_id, skip=skip, limit=limit
        )

    def update_customer(self, id: int, customer_in: CustomerUpdate, barbershop_id: int):
        customer = self.get_customer(id, barbershop_id)
        if customer_in.email and customer_in.email != customer.email:
            existing_customer = self.customer_repo.get_by_email(customer_in.email)
            if existing_customer:
                raise HTTPException(
                    status_code=400, detail="Customer email already registered"
                )
        return self.customer_repo.update(id, customer_in)

    def soft_delete_customer(self, id: int, barbershop_id: int):
        customer = self.get_customer(id, barbershop_id)
        return self.customer_repo.soft_delete(id)

    def restore_customer(self, id: int, barbershop_id: int):
        customer = self.customer_repo.restore(id)
        if not customer:
            raise HTTPException(
                status_code=404, detail="Customer not found or already active"
            )
        if customer.barbershop_id != barbershop_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return customer
