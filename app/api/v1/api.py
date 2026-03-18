from fastapi import APIRouter
from app.api.v1 import user_router, barbershop_router

api_router = APIRouter()
api_router.include_router(user_router.router, prefix="/users", tags=["users"])
api_router.include_router(
    barbershop_router.router, prefix="/barbershops", tags=["barbershops"]
)
