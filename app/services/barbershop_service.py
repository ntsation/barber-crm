from app.repositories.barbershop_repository import IBarberShopRepository
from app.schemas.barbershop import BarberShopCreate, BarberShopUpdate
from app.models.barbershop import BarberShop as BarberShopModel
from fastapi import HTTPException


class BarberShopService:
    def __init__(self, barbershop_repo: IBarberShopRepository):
        self.barbershop_repo = barbershop_repo

    def create_barbershop(self, barbershop_in: BarberShopCreate):
        return self.barbershop_repo.create(barbershop_in)

    def get_barbershop(self, id: int, owner_id: int) -> BarberShopModel:
        barbershop = self.barbershop_repo.get_by_id(id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")
        if barbershop.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return barbershop

    def get_owner_barbershops(self, owner_id: int, skip: int = 0, limit: int = 100):
        return self.barbershop_repo.get_by_owner(owner_id, skip=skip, limit=limit)

    def update_barbershop(
        self, id: int, barbershop_in: BarberShopUpdate, owner_id: int
    ):
        barbershop = self.get_barbershop(id, owner_id)
        return self.barbershop_repo.update(id, barbershop_in)

    def soft_delete_barbershop(self, id: int, owner_id: int):
        barbershop = self.get_barbershop(id, owner_id)
        return self.barbershop_repo.soft_delete(id)

    def restore_barbershop(self, id: int, owner_id: int):
        barbershop = self.barbershop_repo.restore(id)
        if not barbershop:
            raise HTTPException(
                status_code=404, detail="Barbershop not found or already active"
            )
        if barbershop.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return barbershop
