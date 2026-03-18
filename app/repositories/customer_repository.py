from typing import List, Optional
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.customer import Customer as CustomerModel
from app.schemas.customer import CustomerCreate, CustomerUpdate


class ICustomerRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[CustomerModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_barbershop(
        self, barbershop_id: int, skip: int = 0, limit: int = 100
    ) -> List[CustomerModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[CustomerModel]:
        pass  # pragma: no cover

    @abstractmethod
    def create(self, customer: CustomerCreate) -> CustomerModel:
        pass  # pragma: no cover

    @abstractmethod
    def update(self, id: int, customer: CustomerUpdate) -> Optional[CustomerModel]:
        pass  # pragma: no cover

    @abstractmethod
    def soft_delete(self, id: int) -> bool:
        pass  # pragma: no cover

    @abstractmethod
    def restore(self, id: int) -> Optional[CustomerModel]:
        pass  # pragma: no cover


class CustomerRepository(ICustomerRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[CustomerModel]:
        return (
            self.db.query(CustomerModel)
            .filter(CustomerModel.id == id, CustomerModel.is_active == True)
            .first()
        )

    def get_by_barbershop(
        self, barbershop_id: int, skip: int = 0, limit: int = 100
    ) -> List[CustomerModel]:
        return (
            self.db.query(CustomerModel)
            .filter(
                CustomerModel.barbershop_id == barbershop_id,
                CustomerModel.is_active == True,
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_email(self, email: str) -> Optional[CustomerModel]:
        return (
            self.db.query(CustomerModel)
            .filter(CustomerModel.email == email, CustomerModel.is_active == True)
            .first()
        )

    def create(self, customer: CustomerCreate) -> CustomerModel:
        db_customer = CustomerModel(
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            barbershop_id=customer.barbershop_id,
        )
        self.db.add(db_customer)
        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer

    def update(self, id: int, customer: CustomerUpdate) -> Optional[CustomerModel]:
        db_customer = self.get_by_id(id)
        if not db_customer:
            return None
        update_data = customer.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_customer, field, value)
        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer

    def soft_delete(self, id: int) -> bool:
        db_customer = (
            self.db.query(CustomerModel).filter(CustomerModel.id == id).first()
        )
        if not db_customer:
            return False
        db_customer.is_active = False
        db_customer.deleted_at = func.now()
        self.db.commit()
        return True

    def restore(self, id: int) -> Optional[CustomerModel]:
        db_customer = (
            self.db.query(CustomerModel).filter(CustomerModel.id == id).first()
        )
        if not db_customer:
            return None
        db_customer.is_active = True
        db_customer.deleted_at = None
        self.db.commit()
        self.db.refresh(db_customer)
        return db_customer
