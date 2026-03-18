from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.barber import Barber, BarberCreate, BarberUpdate
from app.repositories.barber_repository import BarberRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.repositories.user_repository import UserRepository
from app.services.barber_service import BarberService

router = APIRouter()


@router.post("/", response_model=Barber, status_code=201)
def create_barber(barber_in: BarberCreate, db: Session = Depends(get_db)):
    barber_repo = BarberRepository(db)
    barbershop_repo = BarberShopRepository(db)
    user_repo = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo, user_repo)
    return barber_service.create_barber(barber_in)


@router.get("/{barber_id}", response_model=Barber)
def get_barber(barber_id: int, db: Session = Depends(get_db)):
    barber_repo = BarberRepository(db)
    barbershop_repo = BarberShopRepository(db)
    user_repo = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo, user_repo)
    return barber_service.get_barber(barber_id)


@router.get("/barbershop/{barbershop_id}", response_model=List[Barber])
def get_barbershop_barbers(
    barbershop_id: int,
    active_only: bool = Query(False, description="Only active barbers"),
    db: Session = Depends(get_db),
):
    barber_repo = BarberRepository(db)
    barbershop_repo = BarberShopRepository(db)
    user_repo = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo, user_repo)
    return barber_service.get_barbershop_barbers(barbershop_id, active_only)


@router.get("/user/{user_id}", response_model=Barber)
def get_barber_by_user(user_id: int, db: Session = Depends(get_db)):
    barber_repo = BarberRepository(db)
    barbershop_repo = BarberShopRepository(db)
    user_repo = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo, user_repo)
    return barber_service.get_barber_by_user(user_id)


@router.put("/{barber_id}", response_model=Barber)
def update_barber(
    barber_id: int,
    barber_in: BarberUpdate,
    barbershop_id: int,
    db: Session = Depends(get_db),
):
    barber_repo = BarberRepository(db)
    barbershop_repo = BarberShopRepository(db)
    user_repo = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo, user_repo)
    return barber_service.update_barber(barber_id, barber_in, barbershop_id)


@router.delete("/{barber_id}")
def delete_barber(barber_id: int, barbershop_id: int, db: Session = Depends(get_db)):
    barber_repo = BarberRepository(db)
    barbershop_repo = BarberShopRepository(db)
    user_repo = UserRepository(db)
    barber_service = BarberService(barber_repo, barbershop_repo, user_repo)
    barber_service.delete_barber(barber_id, barbershop_id)
    return {"message": "Barber deleted successfully"}
