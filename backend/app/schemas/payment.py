from pydantic import BaseModel
from typing import Optional


class CreateRazorpayOrderRequest(BaseModel):
    order_id: int  # internal order id to charge
    amount: float  # amount in INR rupees


class RazorpayVerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
