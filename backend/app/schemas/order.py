from pydantic import BaseModel, condecimal
from typing import List, Optional
from datetime import datetime


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    # we don't accept total_amount from client; computed server-side
    items: List[OrderItemCreate]


class OrderItemOut(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    price_at_purchase: condecimal(max_digits=12, decimal_places=2)

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    farmer_id: int
    status: str
    total_amount: condecimal(max_digits=12, decimal_places=2)
    razorpay_order_id: Optional[str]
    razorpay_payment_id: Optional[str]
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        from_attributes = True
