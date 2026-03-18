from typing import List, Optional
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.barbershop import BarberShop as BarberShopModel
from app.schemas.barbershop import BarberShopCreate, BarberShopUpdate


class IBarberShopRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[BarberShopModel]:
        pass

    @abstractmethod
    def get_by_owner(
        self, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[BarberShopModel]:
        pass

    @abstractmethod
    def create(self, barbershop: BarberShopCreate) -> BarberShopModel:
        pass

    @abstractmethod
    def update(
        self, id: int, barbershop: BarberShopUpdate
    ) -> Optional[BarberShopModel]:
        pass

    @abstractmethod
    def soft_delete(self, id: int) -> bool:
        pass

    @abstractmethod
    def restore(self, id: int) -> Optional[BarberShopModel]:
        pass


class BarberShopRepository(IBarberShopRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[BarberShopModel]:
        return (
            self.db.query(BarberShopModel)
            .filter(BarberShopModel.id == id, BarberShopModel.is_active == True)
            .first()
        )

    def get_by_owner(
        self, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[BarberShopModel]:
        return (
            self.db.query(BarberShopModel)
            .filter(
                BarberShopModel.owner_id == owner_id, BarberShopModel.is_active == True
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, barbershop: BarberShopCreate) -> BarberShopModel:
        db_barbershop = BarberShopModel(
            name=barbershop.name,
            address=barbershop.address,
            phone=barbershop.phone,
            owner_id=barbershop.owner_id,
        )
        self.db.add(db_barbershop)
        self.db.commit()
        self.db.refresh(db_barbershop)
        return db_barbershop

    def update(
        self, id: int, barbershop: BarberShopUpdate
    ) -> Optional[BarberShopModel]:
        db_barbershop = self.get_by_id(id)
        if not db_barbershop:
            return None
        update_data = barbershop.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_barbershop, field, value)
        self.db.commit()
        self.db.refresh(db_barbershop)
        return db_barbershop

    def soft_delete(self, id: int) -> bool:
        db_barbershop = (
            self.db.query(BarberShopModel).filter(BarberShopModel.id == id).first()
        )
        if not db_barbershop:
            return False
        db_barbershop.is_active = False
        db_barbershop.deleted_at = func.now()
        self.db.commit()
        return True

    def restore(self, id: int) -> Optional[BarberShopModel]:
        db_barbershop = (
            self.db.query(BarberShopModel).filter(BarberShopModel.id == id).first()
        )
        if not db_barbershop:
            return None
        db_barbershop.is_active = True
        db_barbershop.deleted_at = None
        self.db.commit()
        self.db.refresh(db_barbershop)
        return db_barbershop
