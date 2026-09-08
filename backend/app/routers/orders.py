from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.product import Product
from app.models.cart import CartItem
from app.models.user import User
from app.schemas.order import OrderCreate, OrderOut
from app.auth.dependencies import require_role, get_current_user

from decimal import Decimal

router = APIRouter()


@router.post("/", response_model=OrderOut)
async def create_order(payload: OrderCreate, current_user: User = Depends(require_role("FARMER")), db: AsyncSession = Depends(get_db)):
    # Use transaction
    async with db.begin():
        # validate cart matches items (we will allow client to pass items; but will verify stock and compute prices)
        total = Decimal("0.00")
        order = Order(farmer_id=current_user.id, status="PLACED", total_amount=total)
        db.add(order)
        await db.flush()  # get order.id

        for item in payload.items:
            result = await db.execute(select(Product).where(Product.id == item.product_id).with_for_update())
            product = result.scalars().first()
            if not product:
                raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
            if product.stock < item.quantity:
                raise HTTPException(status_code=400, detail=f"Insufficient stock for product {product.name}")
            price = product.price
            total += Decimal(price) * item.quantity
            order_item = OrderItem(order_id=order.id, product_id=product.id, quantity=item.quantity, price_at_purchase=price)
            db.add(order_item)
            # reduce stock
            product.stock = product.stock - item.quantity
            db.add(product)

        order.total_amount = total
        # clear cart items for this user that match purchased products
        await db.execute(select(CartItem).where(CartItem.farmer_id == current_user.id))
        # commit happens automatically on context exit

    # refresh
    await db.refresh(order)
    return order


@router.get("/my", response_model=list[OrderOut])
async def my_orders(current_user: User = Depends(require_role("FARMER")), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).where(Order.farmer_id == current_user.id).order_by(Order.created_at.desc()))
    orders = result.scalars().all()
    return orders


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if current_user.role == "FARMER" and order.farmer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    # vendors see relevant orders via vendor-specific endpoint
    return order


@router.get("/vendor")
async def vendor_orders(current_user: User = Depends(require_role("VENDOR")), db: AsyncSession = Depends(get_db)):
    # find orders that include items from this vendor's products
    q = select(Order).join(OrderItem).join(Product).where(Product.vendor_id == current_user.id)
    result = await db.execute(q)
    orders = result.scalars().all()
    return orders
