from fastapi import APIRouter
from app.api import (
    user_router,
    barbershop_router,
    customer_router,
    barbershop_profile_router,
    barbershop_schedule_router,
    barbershop_settings_router,
    service_router,
    barber_router,
    barber_schedule_router,
    appointment_router,
)

api_router = APIRouter()
api_router.include_router(user_router.router, prefix="/users", tags=["users"])
api_router.include_router(
    barbershop_router.router, prefix="/barbershops", tags=["barbershops"]
)
api_router.include_router(
    customer_router.router, prefix="/customers", tags=["customers"]
)
api_router.include_router(
    barbershop_profile_router.router,
    prefix="/barbershop-profiles",
    tags=["barbershop-profiles"],
)
api_router.include_router(
    barbershop_schedule_router.router,
    prefix="/barbershop-schedules",
    tags=["barbershop-schedules"],
)
api_router.include_router(
    barbershop_settings_router.router,
    prefix="/barbershop-settings",
    tags=["barbershop-settings"],
)
api_router.include_router(service_router.router, prefix="/services", tags=["services"])
api_router.include_router(barber_router.router, prefix="/barbers", tags=["barbers"])
api_router.include_router(
    barber_schedule_router.router, prefix="/barber-schedules", tags=["barber-schedules"]
)
api_router.include_router(
    appointment_router.router, prefix="/appointments", tags=["appointments"]
)
