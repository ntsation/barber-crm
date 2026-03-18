from typing import Optional, List
from abc import ABC, abstractmethod
from datetime import date as date_type
from sqlalchemy import func, and_
from sqlalchemy.orm import Session
from app.models.appointment import Appointment as AppointmentModel
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate


class IAppointmentRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[AppointmentModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_barbershop(self, barbershop_id: int) -> List[AppointmentModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_customer(self, customer_id: int) -> List[AppointmentModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_barber(self, barber_id: int) -> List[AppointmentModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_barbershop_and_status(
        self, barbershop_id: int, status: str
    ) -> List[AppointmentModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_date(self, date: str, barbershop_id: int) -> List[AppointmentModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_barber_and_date(
        self, barber_id: int, date: date_type
    ) -> List[AppointmentModel]:
        pass  # pragma: no cover

    @abstractmethod
    def has_conflicting_appointment(
        self,
        barber_id: int,
        date: date_type,
        start_time: str,
        end_time: str,
        exclude_id: Optional[int] = None,
    ) -> bool:
        pass  # pragma: no cover

    @abstractmethod
    def create(self, appointment: AppointmentCreate) -> AppointmentModel:
        pass  # pragma: no cover

    @abstractmethod
    def update(
        self, id: int, appointment: AppointmentUpdate
    ) -> Optional[AppointmentModel]:
        pass  # pragma: no cover

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass  # pragma: no cover


class AppointmentRepository(IAppointmentRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[AppointmentModel]:
        return self.db.query(AppointmentModel).filter(AppointmentModel.id == id).first()

    def get_by_barbershop(self, barbershop_id: int) -> List[AppointmentModel]:
        return (
            self.db.query(AppointmentModel)
            .filter(AppointmentModel.barbershop_id == barbershop_id)
            .order_by(AppointmentModel.scheduled_date, AppointmentModel.scheduled_time)
            .all()
        )

    def get_by_customer(self, customer_id: int) -> List[AppointmentModel]:
        return (
            self.db.query(AppointmentModel)
            .filter(AppointmentModel.customer_id == customer_id)
            .order_by(AppointmentModel.scheduled_date.desc())
            .all()
        )

    def get_by_barber(self, barber_id: int) -> List[AppointmentModel]:
        return (
            self.db.query(AppointmentModel)
            .filter(AppointmentModel.barber_id == barber_id)
            .order_by(AppointmentModel.scheduled_date, AppointmentModel.scheduled_time)
            .all()
        )

    def get_by_barbershop_and_status(
        self, barbershop_id: int, status: str
    ) -> List[AppointmentModel]:
        return (
            self.db.query(AppointmentModel)
            .filter(
                AppointmentModel.barbershop_id == barbershop_id,
                AppointmentModel.status == status,
            )
            .order_by(AppointmentModel.scheduled_date, AppointmentModel.scheduled_time)
            .all()
        )

    def get_by_date(self, date: str, barbershop_id: int) -> List[AppointmentModel]:
        return (
            self.db.query(AppointmentModel)
            .filter(
                AppointmentModel.barbershop_id == barbershop_id,
                func.date(AppointmentModel.scheduled_date) == date,
            )
            .order_by(AppointmentModel.scheduled_time)
            .all()
        )

    def get_by_barber_and_date(
        self, barber_id: int, date: date_type
    ) -> List[AppointmentModel]:
        return (
            self.db.query(AppointmentModel)
            .filter(
                AppointmentModel.barber_id == barber_id,
                func.date(AppointmentModel.scheduled_date) == date,
                AppointmentModel.status.notin_(["cancelled", "no_show"]),
            )
            .order_by(AppointmentModel.scheduled_time)
            .all()
        )

    def has_conflicting_appointment(
        self,
        barber_id: int,
        date: date_type,
        start_time: str,
        end_time: str,
        exclude_id: Optional[int] = None,
    ) -> bool:
        from datetime import datetime, timedelta

        # Get all appointments for this barber on this date
        appointments = self.db.query(AppointmentModel).filter(
            AppointmentModel.barber_id == barber_id,
            func.date(AppointmentModel.scheduled_date) == date,
            AppointmentModel.status.notin_(["cancelled", "no_show"]),
        )

        if exclude_id:
            appointments = appointments.filter(AppointmentModel.id != exclude_id)

        appointments = appointments.all()

        # Check for conflicts in Python
        for appt in appointments:
            appt_start = appt.scheduled_time
            # Assume default 30 min duration if not specified
            appt_duration = getattr(appt, 'duration_minutes', 30) or 30
            appt_end = self._add_minutes_to_time(appt_start, appt_duration)

            # Check if there's an overlap
            if appt_start < end_time and appt_end > start_time:
                return True

        return False

    def _add_minutes_to_time(self, time_str: str, minutes: int) -> str:
        from datetime import datetime, timedelta
        time_obj = datetime.strptime(time_str, "%H:%M")
        new_time = time_obj + timedelta(minutes=minutes)
        return new_time.strftime("%H:%M")

    def create(self, appointment: AppointmentCreate) -> AppointmentModel:
        db_appointment = AppointmentModel(**appointment.model_dump())
        self.db.add(db_appointment)
        self.db.commit()
        self.db.refresh(db_appointment)
        return db_appointment

    def update(
        self, id: int, appointment: AppointmentUpdate
    ) -> Optional[AppointmentModel]:
        db_appointment = self.get_by_id(id)
        if not db_appointment:
            return None
        update_data = appointment.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_appointment, field, value)
        self.db.commit()
        self.db.refresh(db_appointment)
        return db_appointment

    def delete(self, id: int) -> bool:
        db_appointment = (
            self.db.query(AppointmentModel).filter(AppointmentModel.id == id).first()
        )
        if not db_appointment:
            return False
        self.db.delete(db_appointment)
        self.db.commit()
        return True
