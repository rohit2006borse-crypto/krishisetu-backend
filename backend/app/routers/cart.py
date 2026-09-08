from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.cart import CartItem
from app.models.product import Product
from app.models.user import User
from app.schemas.cart import CartItemCreate, CartOut, CartItemOut
from app.auth.dependencies import require_role, get_current_user

from typing import List

router = APIRouter()


@router.post("/items", response_model=CartItemOut)
async def add_cart_item(payload: CartItemCreate, current_user: User = Depends(require_role("FARMER")), db: AsyncSession = Depends(get_db)):
    # ensure product exists
    result = await db.execute(select(Product).where(Product.id == payload.product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if payload.quantity > product.stock:
        raise HTTPException(status_code=400, detail="Quantity exceeds available stock")

    # check existing
    result = await db.execute(select(CartItem).where(CartItem.farmer_id == current_user.id, CartItem.product_id == payload.product_id))
    existing = result.scalars().first()
    if existing:
        existing.quantity = existing.quantity + payload.quantity
        if existing.quantity > product.stock:
            raise HTTPException(status_code=400, detail="Quantity exceeds available stock")
        db.add(existing)
        await db.commit()
        await db.refresh(existing)
        return existing

    item = CartItem(farmer_id=current_user.id, product_id=payload.product_id, quantity=payload.quantity)
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/", response_model=CartOut)
async def get_cart(current_user: User = Depends(require_role("FARMER")), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CartItem).where(CartItem.farmer_id == current_user.id))
    items = result.scalars().all()
    total = 0
    for item in items:
        total += float(item.product.price) * item.quantity
    return {"items": items, "total_amount": total}


@router.put("/items/{item_id}", response_model=CartItemOut)
async def update_item(item_id: int, payload: CartItemCreate, current_user: User = Depends(require_role("FARMER")), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CartItem).where(CartItem.id == item_id))
    item = result.scalars().first()
    if not item or item.farmer_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cart item not found")
    # check stock
    result = await db.execute(select(Product).where(Product.id == item.product_id))
    product = result.scalars().first()
    if payload.quantity > product.stock:
        raise HTTPException(status_code=400, detail="Quantity exceeds available stock")
    item.quantity = payload.quantity
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/items/{item_id}")
async def delete_item(item_id: int, current_user: User = Depends(require_role("FARMER")), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CartItem).where(CartItem.id == item_id))
    item = result.scalars().first()
    if not item or item.farmer_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cart item not found")
    await db.delete(item)
    await db.commit()
    return {"message": "Cart item deleted"}


@router.delete("/clear")
async def clear_cart(current_user: User = Depends(require_role("FARMER")), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CartItem).where(CartItem.farmer_id == current_user.id))
    items = result.scalars().all()
    for item in items:
        await db.delete(item)
    await db.commit()
    return {"message": "Cart cleared"}
