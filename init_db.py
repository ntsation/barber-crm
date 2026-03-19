"""Database initialization script."""
import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from app.db.base_class import Base
from app.core.config import settings

# Import all models to ensure they are registered with Base
from app.models.user import User
from app.models.barbershop import BarberShop
from app.models.barber import Barber
from app.models.customer import Customer
from app.models.service import Service
from app.models.appointment import Appointment
from app.models.barber_schedule import BarberSchedule
from app.models.barbershop_profile import BarberShopProfile
from app.models.barbershop_schedule import BarberShopSchedule
from app.models.barbershop_settings import BarberShopSettings
from app.models.audit_log import AuditLog


def init_db():
    """Initialize database tables."""
    print(f"Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)
    
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    
    print("Database initialization complete!")
    
    # List created tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nTables created: {', '.join(tables)}")


if __name__ == "__main__":
    init_db()
