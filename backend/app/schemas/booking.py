from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class BookingCreate(BaseModel):
    equipment_id: int
    start_date: datetime
    end_date: datetime


class BookingOut(BaseModel):
    id: int
    equipment_id: int
    farmer_id: int
    start_date: datetime
    end_date: datetime
    status: str
    queue_position: Optional[int]
    confirmation_deadline: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
