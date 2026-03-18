from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    barbershop_id = Column(Integer, ForeignKey("barbershops.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    barber_id = Column(Integer, ForeignKey("barbers.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    scheduled_date = Column(DateTime, nullable=False)
    scheduled_time = Column(String(5), nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    notes = Column(Text)
    total_price = Column(Float)

    barbershop = relationship("BarberShop", backref="appointments")
    customer = relationship("Customer", backref="appointments")
    barber = relationship("Barber", backref="appointments")
    service = relationship("Service", backref="appointments")
