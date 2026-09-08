from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, func, Index
from sqlalchemy.orm import relationship
from app.database import Base


class BookingRequest(Base):
    __tablename__ = "booking_requests"

    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id", ondelete="CASCADE"), nullable=False, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), nullable=False, index=True)  # QUEUED, CONFIRMATION_PENDING, CONFIRMED, ACTIVE, COMPLETED, EXPIRED, CANCELLED
    queue_position = Column(Integer, nullable=True)
    confirmation_deadline = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    equipment = relationship("Equipment", lazy="joined")
    farmer = relationship("User", lazy="joined")


Index("ix_booking_equipment_status", BookingRequest.equipment_id, BookingRequest.status)
