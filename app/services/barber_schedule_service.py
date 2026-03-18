from app.repositories.barber_schedule_repository import IBarberScheduleRepository
from app.repositories.barber_repository import IBarberRepository
from app.schemas.barber_schedule import BarberScheduleCreate, BarberScheduleUpdate
from app.models.barber_schedule import BarberSchedule as BarberScheduleModel
from fastapi import HTTPException
from typing import List


class BarberScheduleService:
    def __init__(
        self,
        schedule_repo: IBarberScheduleRepository,
        barber_repo: IBarberRepository,
    ):
        self.schedule_repo = schedule_repo
        self.barber_repo = barber_repo

    def create_schedule(self, schedule_in: BarberScheduleCreate) -> BarberScheduleModel:
        barber = self.barber_repo.get_by_id(schedule_in.barber_id)
        if not barber:
            raise HTTPException(status_code=404, detail="Barber not found")

        existing = self.schedule_repo.get_by_barber_and_day(
            schedule_in.barber_id, schedule_in.day_of_week
        )
        if existing:
            raise HTTPException(
                status_code=400, detail="Schedule already exists for this day"
            )

        return self.schedule_repo.create(schedule_in)

    def get_schedule(self, schedule_id: int) -> BarberScheduleModel:
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return schedule

    def get_barber_schedules(self, barber_id: int) -> List[BarberScheduleModel]:
        barber = self.barber_repo.get_by_id(barber_id)
        if not barber:
            raise HTTPException(status_code=404, detail="Barber not found")
        return self.schedule_repo.get_by_barber(barber_id)

    def get_barber_available_schedules(
        self, barber_id: int
    ) -> List[BarberScheduleModel]:
        barber = self.barber_repo.get_by_id(barber_id)
        if not barber:
            raise HTTPException(status_code=404, detail="Barber not found")
        return self.schedule_repo.get_available_by_barber(barber_id)

    def update_schedule(
        self,
        schedule_id: int,
        schedule_in: BarberScheduleUpdate,
    ) -> BarberScheduleModel:
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        return self.schedule_repo.update(schedule_id, schedule_in)

    def delete_schedule(self, schedule_id: int) -> bool:
        schedule = self.schedule_repo.get_by_id(schedule_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")

        return self.schedule_repo.delete(schedule_id)
