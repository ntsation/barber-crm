from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Barber(Base):
    __tablename__ = "barbers"

    id = Column(Integer, primary_key=True, index=True)
    barbershop_id = Column(Integer, ForeignKey("barbershops.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(100), nullable=False)
    specialty = Column(String(100))
    bio = Column(Text)
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    working_days = Column(JSON)
    working_hours = Column(JSON)

    barbershop = relationship("BarberShop", backref="barbers")
    user = relationship("User", backref="barber_profile")
