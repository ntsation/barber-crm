from app.repositories.barbershop_profile_repository import IBarberShopProfileRepository
from app.repositories.barbershop_repository import IBarberShopRepository
from app.schemas.barbershop_profile import (
    BarberShopProfileCreate,
    BarberShopProfileUpdate,
)
from app.models.barbershop_profile import BarberShopProfile as BarberShopProfileModel
from fastapi import HTTPException


class BarberShopProfileService:
    def __init__(
        self,
        profile_repo: IBarberShopProfileRepository,
        barbershop_repo: IBarberShopRepository,
    ):
        self.profile_repo = profile_repo
        self.barbershop_repo = barbershop_repo

    def create_profile(self, profile_in: BarberShopProfileCreate):
        barbershop = self.barbershop_repo.get_by_id(profile_in.barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        existing_profile = self.profile_repo.get_by_barbershop(profile_in.barbershop_id)
        if existing_profile:
            raise HTTPException(
                status_code=400, detail="Profile already exists for this barbershop"
            )
        return self.profile_repo.create(profile_in)

    def get_profile_by_barbershop(self, barbershop_id: int) -> BarberShopProfileModel:
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        profile = self.profile_repo.get_by_barbershop(barbershop_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        return profile

    def update_profile(
        self, id: int, profile_in: BarberShopProfileUpdate, barbershop_id: int
    ):
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        profile = self.profile_repo.get_by_id(id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        if profile.barbershop_id != barbershop_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return self.profile_repo.update(id, profile_in)

    def soft_delete_profile(self, id: int, barbershop_id: int):
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        profile = self.profile_repo.get_by_id(id)
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        if profile.barbershop_id != barbershop_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return self.profile_repo.soft_delete(id)

    def restore_profile(self, id: int, barbershop_id: int):
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        profile = self.profile_repo.restore(id)
        if not profile:
            raise HTTPException(
                status_code=404, detail="Profile not found or already active"
            )
        if profile.barbershop_id != barbershop_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return profile
