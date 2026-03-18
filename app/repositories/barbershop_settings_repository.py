from typing import Optional
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.barbershop_settings import BarberShopSettings as BarberShopSettingsModel
from app.schemas.barbershop_settings import (
    BarberShopSettingsCreate,
    BarberShopSettingsUpdate,
)


class IBarberShopSettingsRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[BarberShopSettingsModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_barbershop(
        self, barbershop_id: int
    ) -> Optional[BarberShopSettingsModel]:
        pass  # pragma: no cover

    @abstractmethod
    def create(self, settings: BarberShopSettingsCreate) -> BarberShopSettingsModel:
        pass  # pragma: no cover

    @abstractmethod
    def update(
        self, id: int, settings: BarberShopSettingsUpdate
    ) -> Optional[BarberShopSettingsModel]:
        pass  # pragma: no cover

    @abstractmethod
    def soft_delete(self, id: int) -> bool:
        pass  # pragma: no cover

    @abstractmethod
    def restore(self, id: int) -> Optional[BarberShopSettingsModel]:
        pass  # pragma: no cover


class BarberShopSettingsRepository(IBarberShopSettingsRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[BarberShopSettingsModel]:
        return (
            self.db.query(BarberShopSettingsModel)
            .filter(
                BarberShopSettingsModel.id == id,
                BarberShopSettingsModel.is_active == True,
            )
            .first()
        )

    def get_by_barbershop(
        self, barbershop_id: int
    ) -> Optional[BarberShopSettingsModel]:
        return (
            self.db.query(BarberShopSettingsModel)
            .filter(
                BarberShopSettingsModel.barbershop_id == barbershop_id,
                BarberShopSettingsModel.is_active == True,
            )
            .first()
        )

    def create(self, settings: BarberShopSettingsCreate) -> BarberShopSettingsModel:
        db_settings = BarberShopSettingsModel(
            accept_online_booking=settings.accept_online_booking,
            require_payment_confirmation=settings.require_payment_confirmation,
            advance_booking_hours=settings.advance_booking_hours,
            max_advance_booking_days=settings.max_advance_booking_days,
            cancellation_hours=settings.cancellation_hours,
            notification_email=settings.notification_email,
            notification_phone=settings.notification_phone,
            default_duration_minutes=settings.default_duration_minutes,
            allow_walk_ins=settings.allow_walk_ins,
            max_walk_ins_per_day=settings.max_walk_ins_per_day,
            barbershop_id=settings.barbershop_id,
        )
        self.db.add(db_settings)
        self.db.commit()
        self.db.refresh(db_settings)
        return db_settings

    def update(
        self, id: int, settings: BarberShopSettingsUpdate
    ) -> Optional[BarberShopSettingsModel]:
        db_settings = self.get_by_id(id)
        if not db_settings:
            return None
        update_data = settings.model_dump(exclude_unset=True, exclude={"barbershop_id"})
        for field, value in update_data.items():
            setattr(db_settings, field, value)
        self.db.commit()
        self.db.refresh(db_settings)
        return db_settings

    def soft_delete(self, id: int) -> bool:
        db_settings = (
            self.db.query(BarberShopSettingsModel)
            .filter(BarberShopSettingsModel.id == id)
            .first()
        )
        if not db_settings:
            return False
        db_settings.is_active = False
        db_settings.deleted_at = func.now()
        self.db.commit()
        return True

    def restore(self, id: int) -> Optional[BarberShopSettingsModel]:
        db_settings = (
            self.db.query(BarberShopSettingsModel)
            .filter(BarberShopSettingsModel.id == id)
            .first()
        )
        if not db_settings:
            return None
        db_settings.is_active = True
        db_settings.deleted_at = None
        self.db.commit()
        self.db.refresh(db_settings)
        return db_settings
