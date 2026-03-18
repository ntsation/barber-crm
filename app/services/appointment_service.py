from app.repositories.appointment_repository import IAppointmentRepository
from app.repositories.barbershop_repository import IBarberShopRepository
from app.repositories.customer_repository import ICustomerRepository
from app.repositories.barber_repository import IBarberRepository
from app.repositories.service_repository import IServiceRepository
from app.schemas.appointment import AppointmentCreate, AppointmentUpdate
from app.models.appointment import Appointment as AppointmentModel
from fastapi import HTTPException
from typing import List


class AppointmentService:
    def __init__(
        self,
        appointment_repo: IAppointmentRepository,
        barbershop_repo: IBarberShopRepository,
        customer_repo: ICustomerRepository,
        barber_repo: IBarberRepository,
        service_repo: IServiceRepository,
    ):
        self.appointment_repo = appointment_repo
        self.barbershop_repo = barbershop_repo
        self.customer_repo = customer_repo
        self.barber_repo = barber_repo
        self.service_repo = service_repo

    def create_appointment(self, appointment_in: AppointmentCreate) -> AppointmentModel:
        barbershop = self.barbershop_repo.get_by_id(appointment_in.barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")

        customer = self.customer_repo.get_by_id(appointment_in.customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        barber = self.barber_repo.get_by_id(appointment_in.barber_id)
        if not barber:
            raise HTTPException(status_code=404, detail="Barber not found")

        service = self.service_repo.get_by_id(appointment_in.service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        if barber.barbershop_id != appointment_in.barbershop_id:
            raise HTTPException(
                status_code=400, detail="Barber does not belong to this barbershop"
            )

        if service.barbershop_id != appointment_in.barbershop_id:
            raise HTTPException(
                status_code=400, detail="Service does not belong to this barbershop"
            )

        return self.appointment_repo.create(appointment_in)

    def get_appointment(self, appointment_id: int) -> AppointmentModel:
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        return appointment

    def get_barbershop_appointments(
        self, barbershop_id: int, status: str = None
    ) -> List[AppointmentModel]:
        barbershop = self.barbershop_repo.get_by_id(barbershop_id)
        if not barbershop:
            raise HTTPException(status_code=404, detail="Barbershop not found")

        if status:
            return self.appointment_repo.get_by_barbershop_and_status(
                barbershop_id, status
            )
        return self.appointment_repo.get_by_barbershop(barbershop_id)

    def get_customer_appointments(self, customer_id: int) -> List[AppointmentModel]:
        customer = self.customer_repo.get_by_id(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return self.appointment_repo.get_by_customer(customer_id)

    def get_barber_appointments(self, barber_id: int) -> List[AppointmentModel]:
        barber = self.barber_repo.get_by_id(barber_id)
        if not barber:
            raise HTTPException(status_code=404, detail="Barber not found")
        return self.appointment_repo.get_by_barber(barber_id)

    def update_appointment(
        self, appointment_id: int, appointment_in: AppointmentUpdate
    ) -> AppointmentModel:
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        if appointment_in.status:
            valid_statuses = [
                "pending",
                "confirmed",
                "in_progress",
                "completed",
                "cancelled",
                "no_show",
            ]
            if appointment_in.status not in valid_statuses:
                raise HTTPException(status_code=400, detail="Invalid status")

        return self.appointment_repo.update(appointment_id, appointment_in)

    def delete_appointment(self, appointment_id: int) -> bool:
        appointment = self.appointment_repo.get_by_id(appointment_id)
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")

        return self.appointment_repo.delete(appointment_id)
