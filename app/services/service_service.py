from app.repositories.service_repository import IServiceRepository
from app.repositories.barbershop_repository import IBarberShopRepository
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.models.service import Service as ServiceModel
from fastapi import HTTPException
from typing import List


class ServiceService:
    def __init__(
        self,
        service_repo: IServiceRepository,
        barbershop_repo: IBarberShopRepository,
    ):
        self.service_repo = service_repo
        self.barbershop_repo = barbershop_repo

    def create_service(self, service_in: ServiceCreate) -> ServiceModel:
        barbershop = self.barbershop_repo.get_by_id(service_in.barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        return self.service_repo.create(service_in)

    def get_service(self, service_id: int) -> ServiceModel:
        service = self.service_repo.get_by_id(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        return service

    def get_barbershop_services(self, barbershop_id: int) -> List[ServiceModel]:
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        return self.service_repo.get_by_barbershop(barbershop_id)

    def get_barbershop_active_services(self, barbershop_id: int) -> List[ServiceModel]:
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        return self.service_repo.get_active_by_barbershop(barbershop_id)

    def get_barbershop_services_by_category(
        self, barbershop_id: int, category: str
    ) -> List[ServiceModel]:
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        return self.service_repo.get_by_barbershop_and_category(barbershop_id, category)

    def update_service(
        self,
        service_id: int,
        service_in: ServiceUpdate,
        barbershop_id: int,
    ) -> ServiceModel:
        service = self.service_repo.get_by_id(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        if service.barbershop_id != barbershop_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return self.service_repo.update(service_id, service_in)

    def delete_service(self, service_id: int, barbershop_id: int) -> bool:
        service = self.service_repo.get_by_id(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        if service.barbershop_id != barbershop_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return self.service_repo.delete(service_id)
