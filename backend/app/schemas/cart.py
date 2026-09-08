from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class CartItemOut(BaseModel):
    id: int
    farmer_id: int
    product_id: int
    quantity: int
    created_at: datetime

    class Config:
        from_attributes = True


class CartOut(BaseModel):
    items: List[CartItemOut]
    total_amount: float
