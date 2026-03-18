from sqlalchemy import Column, Integer, ForeignKey, Boolean, String, Time
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class BarberSchedule(Base):
    __tablename__ = "barber_schedules"

    id = Column(Integer, primary_key=True, index=True)
    barber_id = Column(Integer, ForeignKey("barbers.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(String(5), nullable=False)
    end_time = Column(String(5), nullable=False)
    is_available = Column(Boolean, default=True)

    barber = relationship("Barber", backref="schedules")
