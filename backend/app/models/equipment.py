from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from app.database import Base


class Equipment(Base):
    __tablename__ = "equipment"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # TRACTOR, ROTAVATOR, ...
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    specifications = Column(Text, nullable=True)
    rate = Column(Numeric(12, 2), nullable=False)
    rate_unit = Column(String(10), nullable=False)  # HOUR, DAY
    location = Column(String(255), nullable=True)
    image_url = Column(String(1024), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", lazy="joined")
