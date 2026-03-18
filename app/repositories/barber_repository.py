from typing import Optional, List
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.models.barber import Barber as BarberModel
from app.schemas.barber import BarberCreate, BarberUpdate


class IBarberRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[BarberModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_barbershop(self, barbershop_id: int) -> List[BarberModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_active_by_barbershop(self, barbershop_id: int) -> List[BarberModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_user(self, user_id: int) -> Optional[BarberModel]:
        pass  # pragma: no cover

    @abstractmethod
    def create(self, barber: BarberCreate) -> BarberModel:
        pass  # pragma: no cover

    @abstractmethod
    def update(self, id: int, barber: BarberUpdate) -> Optional[BarberModel]:
        pass  # pragma: no cover

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass  # pragma: no cover


class BarberRepository(IBarberRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[BarberModel]:
        return self.db.query(BarberModel).filter(BarberModel.id == id).first()

    def get_by_barbershop(self, barbershop_id: int) -> List[BarberModel]:
        return (
            self.db.query(BarberModel)
            .filter(BarberModel.barbershop_id == barbershop_id)
            .order_by(BarberModel.name)
            .all()
        )

    def get_active_by_barbershop(self, barbershop_id: int) -> List[BarberModel]:
        return (
            self.db.query(BarberModel)
            .filter(
                BarberModel.barbershop_id == barbershop_id,
                BarberModel.is_active == True,
            )
            .order_by(BarberModel.name)
            .all()
        )

    def get_by_user(self, user_id: int) -> Optional[BarberModel]:
        return self.db.query(BarberModel).filter(BarberModel.user_id == user_id).first()

    def create(self, barber: BarberCreate) -> BarberModel:
        db_barber = BarberModel(**barber.model_dump())
        self.db.add(db_barber)
        self.db.commit()
        self.db.refresh(db_barber)
        return db_barber

    def update(self, id: int, barber: BarberUpdate) -> Optional[BarberModel]:
        db_barber = self.get_by_id(id)
        if not db_barber:
            return None
        update_data = barber.model_dump(
            exclude_unset=True, exclude={"barbershop_id", "user_id"}
        )
        for field, value in update_data.items():
            setattr(db_barber, field, value)
        self.db.commit()
        self.db.refresh(db_barber)
        return db_barber

    def delete(self, id: int) -> bool:
        db_barber = self.db.query(BarberModel).filter(BarberModel.id == id).first()
        if not db_barber:
            return False
        self.db.delete(db_barber)
        self.db.commit()
        return True
