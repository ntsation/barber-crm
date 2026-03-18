from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Barber CRM"
    DATABASE_URL: str = "postgresql://user:password@db:5432/barberdb"

    class Config:
        case_sensitive = True

settings = Settings()
