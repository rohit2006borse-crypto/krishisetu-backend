from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.equipment import Equipment
from app.models.order import Order
from app.models.booking import BookingRequest
from app.auth.dependencies import require_role

router = APIRouter()


@router.get("/users")
async def admin_users(db: AsyncSession = Depends(get_db), _=Depends(require_role("ADMIN"))):
    result = await db.execute(select(User))
    return result.scalars().all()


@router.get("/products")
async def admin_products(db: AsyncSession = Depends(get_db), _=Depends(require_role("ADMIN"))):
    result = await db.execute(select(Product))
    return result.scalars().all()


@router.get("/equipment")
async def admin_equipment(db: AsyncSession = Depends(get_db), _=Depends(require_role("ADMIN"))):
    result = await db.execute(select(Equipment))
    return result.scalars().all()


@router.get("/orders")
async def admin_orders(db: AsyncSession = Depends(get_db), _=Depends(require_role("ADMIN"))):
    result = await db.execute(select(Order))
    return result.scalars().all()


@router.get("/bookings")
async def admin_bookings(db: AsyncSession = Depends(get_db), _=Depends(require_role("ADMIN"))):
    result = await db.execute(select(BookingRequest))
    return result.scalars().all()
