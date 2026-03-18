from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.barbershop_settings import (
    BarberShopSettings,
    BarberShopSettingsCreate,
    BarberShopSettingsUpdate,
)
from app.repositories.barbershop_settings_repository import BarberShopSettingsRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.services.barbershop_settings_service import BarberShopSettingsService

router = APIRouter()


@router.post("/", response_model=BarberShopSettings)
def create_settings(
    settings_in: BarberShopSettingsCreate, db: Session = Depends(get_db)
):
    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo)
    return settings_service.create_settings(settings_in)


@router.get("/barbershop/{barbershop_id}", response_model=BarberShopSettings)
def get_settings_by_barbershop(barbershop_id: int, db: Session = Depends(get_db)):
    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo)
    return settings_service.get_settings_by_barbershop(barbershop_id)


@router.put("/{settings_id}", response_model=BarberShopSettings)
def update_settings(
    settings_id: int,
    settings_in: BarberShopSettingsUpdate,
    barbershop_id: int,
    db: Session = Depends(get_db),
):
    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo)
    return settings_service.update_settings(settings_id, settings_in, barbershop_id)


@router.delete("/{settings_id}")
def delete_settings(
    settings_id: int, barbershop_id: int, db: Session = Depends(get_db)
):
    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo)
    settings_service.soft_delete_settings(settings_id, barbershop_id)
    return {"message": "Settings deleted successfully"}


@router.post("/{settings_id}/restore", response_model=BarberShopSettings)
def restore_settings(
    settings_id: int, barbershop_id: int, db: Session = Depends(get_db)
):
    settings_repo = BarberShopSettingsRepository(db)
    barbershop_repo = BarberShopRepository(db)
    settings_service = BarberShopSettingsService(settings_repo, barbershop_repo)
    return settings_service.restore_settings(settings_id, barbershop_id)
