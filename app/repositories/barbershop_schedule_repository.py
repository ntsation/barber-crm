from typing import Optional
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.barbershop_schedule import BarberShopSchedule as BarberShopScheduleModel
from app.schemas.barbershop_schedule import (
    BarberShopScheduleCreate,
    BarberShopScheduleUpdate,
)


class IBarberShopScheduleRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[BarberShopScheduleModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_barbershop(
        self, barbershop_id: int
    ) -> Optional[BarberShopScheduleModel]:
        pass  # pragma: no cover

    @abstractmethod
    def create(self, schedule: BarberShopScheduleCreate) -> BarberShopScheduleModel:
        pass  # pragma: no cover

    @abstractmethod
    def update(
        self, id: int, schedule: BarberShopScheduleUpdate
    ) -> Optional[BarberShopScheduleModel]:
        pass  # pragma: no cover

    @abstractmethod
    def soft_delete(self, id: int) -> bool:
        pass  # pragma: no cover

    @abstractmethod
    def restore(self, id: int) -> Optional[BarberShopScheduleModel]:
        pass  # pragma: no cover


class BarberShopScheduleRepository(IBarberShopScheduleRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[BarberShopScheduleModel]:
        return (
            self.db.query(BarberShopScheduleModel)
            .filter(
                BarberShopScheduleModel.id == id,
                BarberShopScheduleModel.is_active == True,
            )
            .first()
        )

    def get_by_barbershop(
        self, barbershop_id: int
    ) -> Optional[BarberShopScheduleModel]:
        return (
            self.db.query(BarberShopScheduleModel)
            .filter(
                BarberShopScheduleModel.barbershop_id == barbershop_id,
                BarberShopScheduleModel.is_active == True,
            )
            .first()
        )

    def create(self, schedule: BarberShopScheduleCreate) -> BarberShopScheduleModel:
        db_schedule = BarberShopScheduleModel(
            monday=schedule.monday.model_dump() if schedule.monday else None,
            tuesday=schedule.tuesday.model_dump() if schedule.tuesday else None,
            wednesday=schedule.wednesday.model_dump() if schedule.wednesday else None,
            thursday=schedule.thursday.model_dump() if schedule.thursday else None,
            friday=schedule.friday.model_dump() if schedule.friday else None,
            saturday=schedule.saturday.model_dump() if schedule.saturday else None,
            sunday=schedule.sunday.model_dump() if schedule.sunday else None,
            barbershop_id=schedule.barbershop_id,
        )
        self.db.add(db_schedule)
        self.db.commit()
        self.db.refresh(db_schedule)
        return db_schedule

    def update(
        self, id: int, schedule: BarberShopScheduleUpdate
    ) -> Optional[BarberShopScheduleModel]:
        db_schedule = self.get_by_id(id)
        if not db_schedule:
            return None
        update_data = schedule.model_dump(exclude_unset=True, exclude={"barbershop_id"})
        for field, value in update_data.items():
            if value is not None:
                setattr(
                    db_schedule,
                    field,
                    value.model_dump() if hasattr(value, "model_dump") else value,
                )
        self.db.commit()
        self.db.refresh(db_schedule)
        return db_schedule

    def soft_delete(self, id: int) -> bool:
        db_schedule = (
            self.db.query(BarberShopScheduleModel)
            .filter(BarberShopScheduleModel.id == id)
            .first()
        )
        if not db_schedule:
            return False
        db_schedule.is_active = False
        db_schedule.deleted_at = func.now()
        self.db.commit()
        return True

    def restore(self, id: int) -> Optional[BarberShopScheduleModel]:
        db_schedule = (
            self.db.query(BarberShopScheduleModel)
            .filter(BarberShopScheduleModel.id == id)
            .first()
        )
        if not db_schedule:
            return None
        db_schedule.is_active = True
        db_schedule.deleted_at = None
        self.db.commit()
        self.db.refresh(db_schedule)
        return db_schedule
