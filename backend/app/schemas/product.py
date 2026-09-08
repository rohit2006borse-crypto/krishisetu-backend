from pydantic import BaseModel, Field, condecimal
from typing import Optional
from datetime import datetime


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1)
    category: str = Field(..., description="SEEDS | FERTILIZER | PESTICIDE")
    price: condecimal(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(..., ge=0)
    description: Optional[str] = None
    image_url: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    vendor_id: int
    name: str
    category: str
    price: condecimal(gt=0, max_digits=10, decimal_places=2)
    stock: int
    description: Optional[str]
    image_url: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
