from app.repositories.barbershop_settings_repository import (
    IBarberShopSettingsRepository,
)
from app.repositories.barbershop_repository import IBarberShopRepository
from app.schemas.barbershop_settings import (
    BarberShopSettingsCreate,
    BarberShopSettingsUpdate,
)
from app.models.barbershop_settings import BarberShopSettings as BarberShopSettingsModel
from fastapi import HTTPException


class BarberShopSettingsService:
    def __init__(
        self,
        settings_repo: IBarberShopSettingsRepository,
        barbershop_repo: IBarberShopRepository,
    ):
        self.settings_repo = settings_repo
        self.barbershop_repo = barbershop_repo

    def create_settings(self, settings_in: BarberShopSettingsCreate):
        barbershop = self.barbershop_repo.get_by_id(settings_in.barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        existing_settings = self.settings_repo.get_by_barbershop(
            settings_in.barbershop_id
        )
        if existing_settings:
            raise HTTPException(
                status_code=400, detail="Settings already exists for this barbershop"
            )
        return self.settings_repo.create(settings_in)

    def get_settings_by_barbershop(self, barbershop_id: int) -> BarberShopSettingsModel:
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        settings = self.settings_repo.get_by_barbershop(barbershop_id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        return settings

    def update_settings(
        self, id: int, settings_in: BarberShopSettingsUpdate, barbershop_id: int
    ):
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        settings = self.settings_repo.get_by_id(id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        if settings.barbershop_id != barbershop_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return self.settings_repo.update(id, settings_in)

    def soft_delete_settings(self, id: int, barbershop_id: int):
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        settings = self.settings_repo.get_by_id(id)
        if not settings:
            raise HTTPException(status_code=404, detail="Settings not found")
        if settings.barbershop_id != barbershop_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return self.settings_repo.soft_delete(id)

    def restore_settings(self, id: int, barbershop_id: int):
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        settings = self.settings_repo.restore(id)
        if not settings:
            raise HTTPException(
                status_code=404, detail="Settings not found or already active"
            )
        if settings.barbershop_id != barbershop_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return settings
