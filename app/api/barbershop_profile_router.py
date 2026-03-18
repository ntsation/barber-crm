from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.barbershop_profile import (
    BarberShopProfile,
    BarberShopProfileCreate,
    BarberShopProfileUpdate,
)
from app.repositories.barbershop_profile_repository import BarberShopProfileRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.services.barbershop_profile_service import BarberShopProfileService

router = APIRouter()


@router.post("/", response_model=BarberShopProfile)
def create_profile(profile_in: BarberShopProfileCreate, db: Session = Depends(get_db)):
    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo)
    return profile_service.create_profile(profile_in)


@router.get("/barbershop/{barbershop_id}", response_model=BarberShopProfile)
def get_profile_by_barbershop(barbershop_id: int, db: Session = Depends(get_db)):
    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo)
    return profile_service.get_profile_by_barbershop(barbershop_id)


@router.put("/{profile_id}", response_model=BarberShopProfile)
def update_profile(
    profile_id: int,
    profile_in: BarberShopProfileUpdate,
    barbershop_id: int,
    db: Session = Depends(get_db),
):
    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo)
    return profile_service.update_profile(profile_id, profile_in, barbershop_id)


@router.delete("/{profile_id}")
def delete_profile(profile_id: int, barbershop_id: int, db: Session = Depends(get_db)):
    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo)
    profile_service.soft_delete_profile(profile_id, barbershop_id)
    return {"message": "Profile deleted successfully"}


@router.post("/{profile_id}/restore", response_model=BarberShopProfile)
def restore_profile(profile_id: int, barbershop_id: int, db: Session = Depends(get_db)):
    profile_repo = BarberShopProfileRepository(db)
    barbershop_repo = BarberShopRepository(db)
    profile_service = BarberShopProfileService(profile_repo, barbershop_repo)
    return profile_service.restore_profile(profile_id, barbershop_id)
