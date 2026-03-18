from app.repositories.barber_repository import IBarberRepository
from app.repositories.barbershop_repository import IBarberShopRepository
from app.repositories.user_repository import IUserRepository
from app.schemas.barber import BarberCreate, BarberUpdate
from app.models.barber import Barber as BarberModel
from fastapi import HTTPException
from typing import List


class BarberService:
    def __init__(
        self,
        barber_repo: IBarberRepository,
        barbershop_repo: IBarberShopRepository,
        user_repo: IUserRepository,
    ):
        self.barber_repo = barber_repo
        self.barbershop_repo = barbershop_repo
        self.user_repo = user_repo

    def create_barber(self, barber_in: BarberCreate) -> BarberModel:
        barbershop = self.barbershop_repo.get_by_id(barber_in.barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")

        if barber_in.user_id:
            user = self.user_repo.get_by_id(barber_in.user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

        return self.barber_repo.create(barber_in)

    def get_barber(self, barber_id: int) -> BarberModel:
        barber = self.barber_repo.get_by_id(barber_id)
        if not barber:
            raise HTTPException(status_code=404, detail="Barber not found")
        return barber

    def get_barbershop_barbers(
        self, barbershop_id: int, active_only: bool = False
    ) -> List[BarberModel]:
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")

        if active_only:
            return self.barber_repo.get_active_by_barbershop(barbershop_id)
        return self.barber_repo.get_by_barbershop(barbershop_id)

    def get_barber_by_user(self, user_id: int) -> BarberModel:
        barber = self.barber_repo.get_by_user(user_id)
        if not barber:
            raise HTTPException(status_code=404, detail="Barber not found")
        return barber

    def update_barber(
        self,
        barber_id: int,
        barber_in: BarberUpdate,
        barbershop_id: int,
    ) -> BarberModel:
        barber = self.barber_repo.get_by_id(barber_id)
        if not barber:
            raise HTTPException(status_code=404, detail="Barber not found")
        if barber.barbershop_id != barbershop_id:
            raise HTTPException(status_code=403, detail="Access denied")

        return self.barber_repo.update(barber_id, barber_in)

    def delete_barber(self, barber_id: int, barbershop_id: int) -> bool:
        barber = self.barber_repo.get_by_id(barber_id)
        if not barber:
            raise HTTPException(status_code=404, detail="Barber not found")
        if barber.barbershop_id != barbershop_id:
            raise HTTPException(status_code=403, detail="Access denied")

        return self.barber_repo.delete(barber_id)
