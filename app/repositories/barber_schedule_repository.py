from typing import Optional, List
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.models.barber_schedule import BarberSchedule as BarberScheduleModel
from app.schemas.barber_schedule import BarberScheduleCreate, BarberScheduleUpdate


class IBarberScheduleRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[BarberScheduleModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_barber(self, barber_id: int) -> List[BarberScheduleModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_barber_and_day(
        self, barber_id: int, day_of_week: int
    ) -> Optional[BarberScheduleModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_available_by_barber(self, barber_id: int) -> List[BarberScheduleModel]:
        pass  # pragma: no cover

    @abstractmethod
    def create(self, schedule: BarberScheduleCreate) -> BarberScheduleModel:
        pass  # pragma: no cover

    @abstractmethod
    def update(
        self, id: int, schedule: BarberScheduleUpdate
    ) -> Optional[BarberScheduleModel]:
        pass  # pragma: no cover

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass  # pragma: no cover


class BarberScheduleRepository(IBarberScheduleRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[BarberScheduleModel]:
        return (
            self.db.query(BarberScheduleModel)
            .filter(BarberScheduleModel.id == id)
            .first()
        )

    def get_by_barber(self, barber_id: int) -> List[BarberScheduleModel]:
        return (
            self.db.query(BarberScheduleModel)
            .filter(BarberScheduleModel.barber_id == barber_id)
            .order_by(BarberScheduleModel.day_of_week)
            .all()
        )

    def get_by_barber_and_day(
        self, barber_id: int, day_of_week: int
    ) -> Optional[BarberScheduleModel]:
        return (
            self.db.query(BarberScheduleModel)
            .filter(
                BarberScheduleModel.barber_id == barber_id,
                BarberScheduleModel.day_of_week == day_of_week,
            )
            .first()
        )

    def get_available_by_barber(self, barber_id: int) -> List[BarberScheduleModel]:
        return (
            self.db.query(BarberScheduleModel)
            .filter(
                BarberScheduleModel.barber_id == barber_id,
                BarberScheduleModel.is_available == True,
            )
            .order_by(BarberScheduleModel.day_of_week)
            .all()
        )

    def create(self, schedule: BarberScheduleCreate) -> BarberScheduleModel:
        db_schedule = BarberScheduleModel(**schedule.model_dump())
        self.db.add(db_schedule)
        self.db.commit()
        self.db.refresh(db_schedule)
        return db_schedule

    def update(
        self, id: int, schedule: BarberScheduleUpdate
    ) -> Optional[BarberScheduleModel]:
        db_schedule = self.get_by_id(id)
        if not db_schedule:
            return None
        update_data = schedule.model_dump(exclude_unset=True, exclude={"barber_id"})
        for field, value in update_data.items():
            setattr(db_schedule, field, value)
        self.db.commit()
        self.db.refresh(db_schedule)
        return db_schedule

    def delete(self, id: int) -> bool:
        db_schedule = (
            self.db.query(BarberScheduleModel)
            .filter(BarberScheduleModel.id == id)
            .first()
        )
        if not db_schedule:
            return False
        self.db.delete(db_schedule)
        self.db.commit()
        return True
