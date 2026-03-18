from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.barbershop_schedule import (
    BarberShopSchedule,
    BarberShopScheduleCreate,
    BarberShopScheduleUpdate,
)
from app.repositories.barbershop_schedule_repository import BarberShopScheduleRepository
from app.repositories.barbershop_repository import BarberShopRepository
from app.services.barbershop_schedule_service import BarberShopScheduleService

router = APIRouter()


@router.post("/", response_model=BarberShopSchedule)
def create_schedule(
    schedule_in: BarberShopScheduleCreate, db: Session = Depends(get_db)
):
    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo)
    return schedule_service.create_schedule(schedule_in)


@router.get("/barbershop/{barbershop_id}", response_model=BarberShopSchedule)
def get_schedule_by_barbershop(barbershop_id: int, db: Session = Depends(get_db)):
    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo)
    return schedule_service.get_schedule_by_barbershop(barbershop_id)


@router.put("/{schedule_id}", response_model=BarberShopSchedule)
def update_schedule(
    schedule_id: int,
    schedule_in: BarberShopScheduleUpdate,
    barbershop_id: int,
    db: Session = Depends(get_db),
):
    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo)
    return schedule_service.update_schedule(schedule_id, schedule_in, barbershop_id)


@router.delete("/{schedule_id}")
def delete_schedule(
    schedule_id: int, barbershop_id: int, db: Session = Depends(get_db)
):
    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo)
    schedule_service.soft_delete_schedule(schedule_id, barbershop_id)
    return {"message": "Schedule deleted successfully"}


@router.post("/{schedule_id}/restore", response_model=BarberShopSchedule)
def restore_schedule(
    schedule_id: int, barbershop_id: int, db: Session = Depends(get_db)
):
    schedule_repo = BarberShopScheduleRepository(db)
    barbershop_repo = BarberShopRepository(db)
    schedule_service = BarberShopScheduleService(schedule_repo, barbershop_repo)
    return schedule_service.restore_schedule(schedule_id, barbershop_id)
