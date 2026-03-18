from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.service import Service, ServiceCreate, ServiceUpdate
from app.repositories.service_repository import ServiceRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.services.service_service import ServiceService

router = APIRouter()


@router.post("/", response_model=Service, status_code=201)
def create_service(service_in: ServiceCreate, db: Session = Depends(get_db)):
    service_repo = ServiceRepository(db)
    barbershop_repo = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo)
    return service_service.create_service(service_in)


@router.get("/{service_id}", response_model=Service)
def get_service(service_id: int, db: Session = Depends(get_db)):
    service_repo = ServiceRepository(db)
    barbershop_repo = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo)
    return service_service.get_service(service_id)


@router.get("/barbershop/{barbershop_id}", response_model=List[Service])
def get_barbershop_services(
    barbershop_id: int,
    category: str = Query(None, description="Filter by category"),
    active_only: bool = Query(False, description="Only active services"),
    db: Session = Depends(get_db),
):
    service_repo = ServiceRepository(db)
    barbershop_repo = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo)

    if category:
        return service_service.get_barbershop_services_by_category(
            barbershop_id, category
        )
    elif active_only:
        return service_service.get_barbershop_active_services(barbershop_id)
    else:
        return service_service.get_barbershop_services(barbershop_id)


@router.put("/{service_id}", response_model=Service)
def update_service(
    service_id: int,
    service_in: ServiceUpdate,
    barbershop_id: int,
    db: Session = Depends(get_db),
):
    service_repo = ServiceRepository(db)
    barbershop_repo = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo)
    return service_service.update_service(service_id, service_in, barbershop_id)


@router.delete("/{service_id}")
def delete_service(service_id: int, barbershop_id: int, db: Session = Depends(get_db)):
    service_repo = ServiceRepository(db)
    barbershop_repo = BarberShopRepository(db)
    service_service = ServiceService(service_repo, barbershop_repo)
    service_service.delete_service(service_id, barbershop_id)
    return {"message": "Service deleted successfully"}
