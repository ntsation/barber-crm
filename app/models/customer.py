from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, index=True)
    phone = Column(String, nullable=False)
    barbershop_id = Column(Integer, ForeignKey("barbershops.id"), nullable=False)

    barbershop = relationship("BarberShop", backref="customers")
