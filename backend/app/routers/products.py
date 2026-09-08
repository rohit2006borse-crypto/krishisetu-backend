from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional, List

from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductOut
from app.auth.dependencies import get_current_user, require_role

router = APIRouter()


@router.get("/", response_model=List[ProductOut], summary="List products with filters")
async def list_products(
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    page: int = 1,
    page_size: int = 20,
    db: AsyncSession = Depends(get_db),
):
    q = select(Product)
    if category:
        q = q.where(Product.category == category)
    if search:
        q = q.where(Product.name.ilike(f"%{search}%"))
    if min_price is not None:
        q = q.where(Product.price >= min_price)
    if max_price is not None:
        q = q.where(Product.price <= max_price)
    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    products = result.scalars().all()
    return products


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.post("/", response_model=ProductOut)
async def create_product(payload: ProductCreate, current_user: User = Depends(require_role("VENDOR")), db: AsyncSession = Depends(get_db)):
    product = Product(
        vendor_id=current_user.id,
        name=payload.name,
        category=payload.category,
        price=payload.price,
        stock=payload.stock,
        description=payload.description,
        image_url=payload.image_url,
    )
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductOut)
async def update_product(product_id: int, payload: ProductCreate, current_user: User = Depends(require_role("VENDOR")), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.vendor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to modify this product")
    product.name = payload.name
    product.category = payload.category
    product.price = payload.price
    product.stock = payload.stock
    product.description = payload.description
    product.image_url = payload.image_url
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.delete("/{product_id}")
async def delete_product(product_id: int, current_user: User = Depends(require_role("VENDOR")), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalars().first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.vendor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this product")
    await db.delete(product)
    await db.commit()
    return {"message": "Product deleted"}
