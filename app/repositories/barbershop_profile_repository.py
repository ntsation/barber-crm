from typing import Optional
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.barbershop_profile import BarberShopProfile as BarberShopProfileModel
from app.schemas.barbershop_profile import (
    BarberShopProfileCreate,
    BarberShopProfileUpdate,
)


class IBarberShopProfileRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[BarberShopProfileModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_barbershop(self, barbershop_id: int) -> Optional[BarberShopProfileModel]:
        pass  # pragma: no cover

    @abstractmethod
    def create(self, profile: BarberShopProfileCreate) -> BarberShopProfileModel:
        pass  # pragma: no cover

    @abstractmethod
    def update(
        self, id: int, profile: BarberShopProfileUpdate
    ) -> Optional[BarberShopProfileModel]:
        pass  # pragma: no cover

    @abstractmethod
    def soft_delete(self, id: int) -> bool:
        pass  # pragma: no cover

    @abstractmethod
    def restore(self, id: int) -> Optional[BarberShopProfileModel]:
        pass  # pragma: no cover


class BarberShopProfileRepository(IBarberShopProfileRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[BarberShopProfileModel]:
        return (
            self.db.query(BarberShopProfileModel)
            .filter(
                BarberShopProfileModel.id == id,
                BarberShopProfileModel.is_active == True,
            )
            .first()
        )

    def get_by_barbershop(self, barbershop_id: int) -> Optional[BarberShopProfileModel]:
        return (
            self.db.query(BarberShopProfileModel)
            .filter(
                BarberShopProfileModel.barbershop_id == barbershop_id,
                BarberShopProfileModel.is_active == True,
            )
            .first()
        )

    def create(self, profile: BarberShopProfileCreate) -> BarberShopProfileModel:
        db_profile = BarberShopProfileModel(
            description=profile.description,
            services=profile.services,
            logo_url=profile.logo_url,
            banner_url=profile.banner_url,
            barbershop_id=profile.barbershop_id,
        )
        self.db.add(db_profile)
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def update(
        self, id: int, profile: BarberShopProfileUpdate
    ) -> Optional[BarberShopProfileModel]:
        db_profile = self.get_by_id(id)
        if not db_profile:
            return None
        update_data = profile.model_dump(exclude_unset=True, exclude={"barbershop_id"})
        for field, value in update_data.items():
            setattr(db_profile, field, value)
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile

    def soft_delete(self, id: int) -> bool:
        db_profile = (
            self.db.query(BarberShopProfileModel)
            .filter(BarberShopProfileModel.id == id)
            .first()
        )
        if not db_profile:
            return False
        db_profile.is_active = False
        db_profile.deleted_at = func.now()
        self.db.commit()
        return True

    def restore(self, id: int) -> Optional[BarberShopProfileModel]:
        db_profile = (
            self.db.query(BarberShopProfileModel)
            .filter(BarberShopProfileModel.id == id)
            .first()
        )
        if not db_profile:
            return None
        db_profile.is_active = True
        db_profile.deleted_at = None
        self.db.commit()
        self.db.refresh(db_profile)
        return db_profile
