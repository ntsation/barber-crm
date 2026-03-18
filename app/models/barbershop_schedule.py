from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class BarberShopSchedule(Base):
    __tablename__ = "barbershop_schedules"

    id = Column(Integer, primary_key=True, index=True)
    barbershop_id = Column(
        Integer, ForeignKey("barbershops.id"), nullable=False, unique=True
    )
    monday = Column(JSON)
    tuesday = Column(JSON)
    wednesday = Column(JSON)
    thursday = Column(JSON)
    friday = Column(JSON)
    saturday = Column(JSON)
    sunday = Column(JSON)

    barbershop = relationship("BarberShop", backref="schedule")
