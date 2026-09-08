from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.equipment import Equipment
from app.schemas.equipment import EquipmentCreate, EquipmentOut
from app.auth.dependencies import require_role, get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=list[EquipmentOut])
async def list_equipment(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Equipment).where(Equipment.is_active == True))
    items = result.scalars().all()
    return items


@router.get("/{equipment_id}", response_model=EquipmentOut)
async def get_equipment(equipment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Equipment not found")
    return item


@router.post("/", response_model=EquipmentOut)
async def create_equipment(payload: EquipmentCreate, current_user: User = Depends(require_role("FARMER")), db: AsyncSession = Depends(get_db)):
    # only farmers who are equipment owners
    if not current_user.is_equipment_owner:
        raise HTTPException(status_code=403, detail="User is not an equipment owner")
    eq = Equipment(
        owner_id=current_user.id,
        type=payload.type,
        name=payload.name,
        description=payload.description,
        specifications=payload.specifications,
        rate=payload.rate,
        rate_unit=payload.rate_unit,
        location=payload.location,
        image_url=payload.image_url,
    )
    db.add(eq)
    await db.commit()
    await db.refresh(eq)
    return eq


@router.put("/{equipment_id}", response_model=EquipmentOut)
async def update_equipment(equipment_id: int, payload: EquipmentCreate, current_user: User = Depends(require_role("FARMER")), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    eq = result.scalars().first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if eq.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to modify this equipment")
    eq.type = payload.type
    eq.name = payload.name
    eq.description = payload.description
    eq.specifications = payload.specifications
    eq.rate = payload.rate
    eq.rate_unit = payload.rate_unit
    eq.location = payload.location
    eq.image_url = payload.image_url
    db.add(eq)
    await db.commit()
    await db.refresh(eq)
    return eq


@router.delete("/{equipment_id}")
async def delete_equipment(equipment_id: int, current_user: User = Depends(require_role("FARMER")), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Equipment).where(Equipment.id == equipment_id))
    eq = result.scalars().first()
    if not eq:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if eq.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete this equipment")
    await db.delete(eq)
    await db.commit()
    return {"message": "Equipment deleted"}


@router.get("/{equipment_id}/availability")
async def equipment_availability(equipment_id: int, db: AsyncSession = Depends(get_db)):
    from app.models.availability_slot import AvailabilitySlot
    result = await db.execute(select(AvailabilitySlot).where(AvailabilitySlot.equipment_id == equipment_id))
    slots = result.scalars().all()
    return slots
