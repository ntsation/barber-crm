from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class BarberShopProfile(Base):
    __tablename__ = "barbershop_profiles"

    id = Column(Integer, primary_key=True, index=True)
    barbershop_id = Column(
        Integer, ForeignKey("barbershops.id"), nullable=False, unique=True
    )
    description = Column(Text)
    services = Column(Text)
    logo_url = Column(String)
    banner_url = Column(String)

    barbershop = relationship("BarberShop", backref="profile")
