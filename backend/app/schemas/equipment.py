from pydantic import BaseModel, Field, condecimal
from typing import Optional
from datetime import datetime


class EquipmentCreate(BaseModel):
    type: str
    name: str
    description: Optional[str] = None
    specifications: Optional[str] = None
    rate: condecimal(gt=0, max_digits=12, decimal_places=2)
    rate_unit: str = Field(..., description="HOUR | DAY")
    location: Optional[str] = None
    image_url: Optional[str] = None


class EquipmentOut(BaseModel):
    id: int
    owner_id: int
    type: str
    name: str
    description: Optional[str]
    specifications: Optional[str]
    rate: condecimal(max_digits=12, decimal_places=2)
    rate_unit: str
    location: Optional[str]
    image_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
