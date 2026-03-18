from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.barber_schedule import (
    BarberSchedule,
    BarberScheduleCreate,
    BarberScheduleUpdate,
)
from app.repositories.barber_schedule_repository import BarberScheduleRepository
from app.repositories.barber_repository import BarberRepository
from app.services.barber_schedule_service import BarberScheduleService

router = APIRouter()


@router.post("/", response_model=BarberSchedule, status_code=201)
def create_schedule(schedule_in: BarberScheduleCreate, db: Session = Depends(get_db)):
    schedule_repo = BarberScheduleRepository(db)
    barber_repo = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo)
    return schedule_service.create_schedule(schedule_in)


@router.get("/{schedule_id}", response_model=BarberSchedule)
def get_schedule(schedule_id: int, db: Session = Depends(get_db)):
    schedule_repo = BarberScheduleRepository(db)
    barber_repo = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo)
    return schedule_service.get_schedule(schedule_id)


@router.get("/barber/{barber_id}", response_model=List[BarberSchedule])
def get_barber_schedules(
    barber_id: int,
    available_only: bool = Query(False, description="Only available schedules"),
    db: Session = Depends(get_db),
):
    schedule_repo = BarberScheduleRepository(db)
    barber_repo = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo)

    if available_only:
        return schedule_service.get_barber_available_schedules(barber_id)
    return schedule_service.get_barber_schedules(barber_id)


@router.put("/{schedule_id}", response_model=BarberSchedule)
def update_schedule(
    schedule_id: int,
    schedule_in: BarberScheduleUpdate,
    db: Session = Depends(get_db),
):
    schedule_repo = BarberScheduleRepository(db)
    barber_repo = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo)
    return schedule_service.update_schedule(schedule_id, schedule_in)


@router.delete("/{schedule_id}")
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    schedule_repo = BarberScheduleRepository(db)
    barber_repo = BarberRepository(db)
    schedule_service = BarberScheduleService(schedule_repo, barber_repo)
    schedule_service.delete_schedule(schedule_id)
    return {"message": "Schedule deleted successfully"}
