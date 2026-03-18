from fastapi import FastAPI
from app.api.api import api_router

app = FastAPI(title="Barber CRM API")

app.include_router(api_router, prefix="/api")


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Barber CRM API is running"}
