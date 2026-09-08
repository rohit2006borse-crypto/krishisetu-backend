from fastapi import APIRouter, Depends, HTTPException
from app.schemas.payment import CreateRazorpayOrderRequest, RazorpayVerifyRequest
from app.config import settings
from app.models.order import Order
from app.models.payment import Payment
from app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import razorpay
import hmac, hashlib

router = APIRouter()


@router.post("/create-order")
async def create_razorpay_order(payload: CreateRazorpayOrderRequest, db: AsyncSession = Depends(get_db)):
    # stripe/razorpay amount in paise
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    # get internal order
    result = await db.execute(select(Order).where(Order.id == payload.order_id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    amount_paise = int(payload.amount * 100)
    data = {"amount": amount_paise, "currency": "INR", "receipt": f"order_{order.id}"}
    razor_order = client.order.create(data)
    order.razorpay_order_id = razor_order.get("id")
    await db.commit()
    return {"razorpay_order": razor_order}


@router.post("/verify")
async def verify_razorpay(payload: RazorpayVerifyRequest, db: AsyncSession = Depends(get_db)):
    # verify signature
    key_secret = settings.RAZORPAY_KEY_SECRET or ""
    message = f"{payload.razorpay_order_id}|{payload.razorpay_payment_id}"
    generated_signature = hmac.new(key_secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    if generated_signature != payload.razorpay_signature:
        raise HTTPException(status_code=400, detail="Invalid signature")
    # update order/payment records
    result = await db.execute(select(Order).where(Order.razorpay_order_id == payload.razorpay_order_id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.razorpay_payment_id = payload.razorpay_payment_id
    order.status = "CONFIRMED"
    payment = Payment(order_id=order.id, provider="RAZORPAY", provider_payment_id=payload.razorpay_payment_id, amount=order.total_amount, status="SUCCESS")
    db.add(payment)
    await db.commit()
    return {"message": "Payment verified and order confirmed"}
