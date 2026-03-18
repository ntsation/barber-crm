from typing import Optional, List
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.service import Service as ServiceModel
from app.schemas.service import ServiceCreate, ServiceUpdate


class IServiceRepository(ABC):
    @abstractmethod
    def get_by_id(self, id: int) -> Optional[ServiceModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_barbershop(self, barbershop_id: int) -> List[ServiceModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_by_barbershop_and_category(
        self, barbershop_id: int, category: str
    ) -> List[ServiceModel]:
        pass  # pragma: no cover

    @abstractmethod
    def get_active_by_barbershop(self, barbershop_id: int) -> List[ServiceModel]:
        pass  # pragma: no cover

    @abstractmethod
    def create(self, service: ServiceCreate) -> ServiceModel:
        pass  # pragma: no cover

    @abstractmethod
    def update(self, id: int, service: ServiceUpdate) -> Optional[ServiceModel]:
        pass  # pragma: no cover

    @abstractmethod
    def delete(self, id: int) -> bool:
        pass  # pragma: no cover


class ServiceRepository(IServiceRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, id: int) -> Optional[ServiceModel]:
        return self.db.query(ServiceModel).filter(ServiceModel.id == id).first()

    def get_by_barbershop(self, barbershop_id: int) -> List[ServiceModel]:
        return (
            self.db.query(ServiceModel)
            .filter(ServiceModel.barbershop_id == barbershop_id)
            .order_by(ServiceModel.name)
            .all()
        )

    def get_by_barbershop_and_category(
        self, barbershop_id: int, category: str
    ) -> List[ServiceModel]:
        return (
            self.db.query(ServiceModel)
            .filter(
                ServiceModel.barbershop_id == barbershop_id,
                ServiceModel.category == category,
            )
            .order_by(ServiceModel.name)
            .all()
        )

    def get_active_by_barbershop(self, barbershop_id: int) -> List[ServiceModel]:
        return (
            self.db.query(ServiceModel)
            .filter(
                ServiceModel.barbershop_id == barbershop_id,
                ServiceModel.is_active == True,
            )
            .order_by(ServiceModel.name)
            .all()
        )

    def create(self, service: ServiceCreate) -> ServiceModel:
        db_service = ServiceModel(**service.model_dump())
        self.db.add(db_service)
        self.db.commit()
        self.db.refresh(db_service)
        return db_service

    def update(self, id: int, service: ServiceUpdate) -> Optional[ServiceModel]:
        db_service = self.get_by_id(id)
        if not db_service:
            return None
        update_data = service.model_dump(exclude_unset=True, exclude={"barbershop_id"})
        for field, value in update_data.items():
            setattr(db_service, field, value)
        self.db.commit()
        self.db.refresh(db_service)
        return db_service

    def delete(self, id: int) -> bool:
        db_service = self.db.query(ServiceModel).filter(ServiceModel.id == id).first()
        if not db_service:
            return False
        self.db.delete(db_service)
        self.db.commit()
        return True
