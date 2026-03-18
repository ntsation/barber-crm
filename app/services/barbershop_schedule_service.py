from app.repositories.barbershop_schedule_repository import (
    IBarberShopScheduleRepository,
)
from app.repositories.barbershop_repository import IBarberShopRepository
from app.schemas.barbershop_schedule import (
    BarberShopScheduleCreate,
    BarberShopScheduleUpdate,
)
from app.models.barbershop_schedule import BarberShopSchedule as BarberShopScheduleModel
from fastapi import HTTPException


class BarberShopScheduleService:
    def __init__(
        self,
        schedule_repo: IBarberShopScheduleRepository,
        barbershop_repo: IBarberShopRepository,
    ):
        self.schedule_repo = schedule_repo
        self.barbershop_repo = barbershop_repo

    def create_schedule(self, schedule_in: BarberShopScheduleCreate):
        barbershop = self.barbershop_repo.get_by_id(schedule_in.barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        existing_schedule = self.schedule_repo.get_by_barbershop(
            schedule_in.barbershop_id
        )
        if existing_schedule:
            raise HTTPException(
                status_code=400, detail="Schedule already exists for this barbershop"
            )
        return self.schedule_repo.create(schedule_in)

    def get_schedule_by_barbershop(self, barbershop_id: int) -> BarberShopScheduleModel:
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        schedule = self.schedule_repo.get_by_barbershop(barbershop_id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        return schedule

    def update_schedule(
        self, id: int, schedule_in: BarberShopScheduleUpdate, barbershop_id: int
    ):
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        schedule = self.schedule_repo.get_by_id(id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        if schedule.barbershop_id != barbershop_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return self.schedule_repo.update(id, schedule_in)

    def soft_delete_schedule(self, id: int, barbershop_id: int):
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        schedule = self.schedule_repo.get_by_id(id)
        if not schedule:
            raise HTTPException(status_code=404, detail="Schedule not found")
        if schedule.barbershop_id != barbershop_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return self.schedule_repo.soft_delete(id)

    def restore_schedule(self, id: int, barbershop_id: int):
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        schedule = self.schedule_repo.restore(id)
        if not schedule:
            raise HTTPException(
                status_code=404, detail="Schedule not found or already active"
            )
        if schedule.barbershop_id != barbershop_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return schedule
