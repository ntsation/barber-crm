from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base


class BarberShopSettings(Base):
    __tablename__ = "barbershop_settings"

    id = Column(Integer, primary_key=True, index=True)
    barbershop_id = Column(
        Integer, ForeignKey("barbershops.id"), nullable=False, unique=True
    )
    accept_online_booking = Column(Boolean, default=True)
    require_payment_confirmation = Column(Boolean, default=False)
    advance_booking_hours = Column(Integer, default=0)
    max_advance_booking_days = Column(Integer, default=30)
    cancellation_hours = Column(Integer, default=24)
    notification_email = Column(String)
    notification_phone = Column(String)
    default_duration_minutes = Column(Integer, default=60)
    allow_walk_ins = Column(Boolean, default=True)
    max_walk_ins_per_day = Column(Integer, default=5)

    barbershop = relationship("BarberShop", backref="settings")
