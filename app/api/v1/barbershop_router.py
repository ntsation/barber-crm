from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.barbershop import BarberShop, BarberShopCreate, BarberShopUpdate
from app.repositories.barbershop_repository import BarberShopRepository
from app.services.barbershop_service import BarberShopService

router = APIRouter()


@router.post("/", response_model=BarberShop)
def create_barbershop(barbershop_in: BarberShopCreate, db: Session = Depends(get_db)):
    barbershop_repo = BarberShopRepository(db)
    barbershop_service = BarberShopService(barbershop_repo)
    return barbershop_service.create_barbershop(barbershop_in)


@router.get("/", response_model=List[BarberShop])
def list_barbershops(
    owner_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    barbershop_repo = BarberShopRepository(db)
    barbershop_service = BarberShopService(barbershop_repo)
    return barbershop_service.get_owner_barbershops(owner_id, skip=skip, limit=limit)


@router.get("/{barbershop_id}", response_model=BarberShop)
def get_barbershop(barbershop_id: int, owner_id: int, db: Session = Depends(get_db)):
    barbershop_repo = BarberShopRepository(db)
    barbershop_service = BarberShopService(barbershop_repo)
    return barbershop_service.get_barbershop(barbershop_id, owner_id)


@router.put("/{barbershop_id}", response_model=BarberShop)
def update_barbershop(
    barbershop_id: int,
    barbershop_in: BarberShopUpdate,
    owner_id: int,
    db: Session = Depends(get_db),
):
    barbershop_repo = BarberShopRepository(db)
    barbershop_service = BarberShopService(barbershop_repo)
    return barbershop_service.update_barbershop(barbershop_id, barbershop_in, owner_id)


@router.delete("/{barbershop_id}")
def delete_barbershop(barbershop_id: int, owner_id: int, db: Session = Depends(get_db)):
    barbershop_repo = BarberShopRepository(db)
    barbershop_service = BarberShopService(barbershop_repo)
    barbershop_service.soft_delete_barbershop(barbershop_id, owner_id)
    return {"message": "Barbershop deleted successfully"}


@router.post("/{barbershop_id}/restore", response_model=BarberShop)
def restore_barbershop(
    barbershop_id: int, owner_id: int, db: Session = Depends(get_db)
):
    barbershop_repo = BarberShopRepository(db)
    barbershop_service = BarberShopService(barbershop_repo)
    return barbershop_service.restore_barbershop(barbershop_id, owner_id)
