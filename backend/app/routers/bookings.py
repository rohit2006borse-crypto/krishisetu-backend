from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.booking import BookingRequest
from app.models.equipment import Equipment
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingOut
from app.auth.dependencies import require_role, get_current_user
from datetime import datetime, timedelta
from app.config import settings

router = APIRouter()


def dates_overlap(start_a, end_a, start_b, end_b) -> bool:
    return start_a < end_b and end_a > start_b


@router.post("/", response_model=BookingOut)
async def create_booking(payload: BookingCreate, current_user: User = Depends(require_role("FARMER")), db: AsyncSession = Depends(get_db)):
    # validate dates
    if payload.start_date >= payload.end_date:
        raise HTTPException(status_code=400, detail="start_date must be before end_date")
    if payload.start_date < datetime.utcnow():
        raise HTTPException(status_code=400, detail="start_date cannot be in the past")

    # Check equipment exists
    result = await db.execute(select(Equipment).where(Equipment.id == payload.equipment_id))
    equipment = result.scalars().first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")

    # FCFS logic in transaction with row-level locking
    async with db.begin():
        # Lock existing bookings for this equipment to compute queue safely
        q = select(BookingRequest).where(
            BookingRequest.equipment_id == payload.equipment_id,
            BookingRequest.status.in_("QUEUED", "CONFIRMATION_PENDING", "CONFIRMED")
        ).with_for_update(of=BookingRequest)
        res = await db.execute(q)
        existing_bookings = res.scalars().all()

        # Determine if any CONFIRMED booking overlaps requested window
        for b in existing_bookings:
            if b.status == "CONFIRMED" and dates_overlap(b.start_date, b.end_date, payload.start_date, payload.end_date):
                # slot is taken
                # add as QUEUED with position at end
                max_pos = max([eb.queue_position or 0 for eb in existing_bookings if eb.queue_position is not None] + [0])
                br = BookingRequest(
                    equipment_id=payload.equipment_id,
                    farmer_id=current_user.id,
                    start_date=payload.start_date,
                    end_date=payload.end_date,
                    status="QUEUED",
                    queue_position=max_pos + 1,
                )
                db.add(br)
                await db.flush()
                await db.refresh(br)
                return br

        # No overlapping CONFIRMED. Check if there is any CONFIRMATION_PENDING or QUEUED that conflicts
        # If no conflicting pending/queued requests for the exact requested period, create CONFIRMATION_PENDING
        # We'll define "conflict" as overlapping periods
        conflicting = [b for b in existing_bookings if dates_overlap(b.start_date, b.end_date, payload.start_date, payload.end_date)]
        if not conflicting:
            deadline = datetime.utcnow() + timedelta(hours=float(settings.BOOKING_CONFIRMATION_HOURS))
            br = BookingRequest(
                equipment_id=payload.equipment_id,
                farmer_id=current_user.id,
                start_date=payload.start_date,
                end_date=payload.end_date,
                status="CONFIRMATION_PENDING",
                queue_position=1,
                confirmation_deadline=deadline,
            )
            db.add(br)
            await db.flush()
            await db.refresh(br)
            return br

        # There are conflicting pending/queued requests. Determine queue position (append to end)
        max_pos = max([b.queue_position or 0 for b in existing_bookings] + [0])
        br = BookingRequest(
            equipment_id=payload.equipment_id,
            farmer_id=current_user.id,
            start_date=payload.start_date,
            end_date=payload.end_date,
            status="QUEUED",
            queue_position=max_pos + 1,
        )
        db.add(br)
        await db.flush()
        await db.refresh(br)
        return br


@router.get("/my", response_model=list[BookingOut])
async def my_bookings(current_user: User = Depends(require_role("FARMER")), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BookingRequest).where(BookingRequest.farmer_id == current_user.id).order_by(BookingRequest.created_at.desc()))
    bookings = result.scalars().all()
    return bookings


@router.get("/{booking_id}", response_model=BookingOut)
async def get_booking(booking_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BookingRequest).where(BookingRequest.id == booking_id))
    booking = result.scalars().first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if current_user.role == "FARMER" and booking.farmer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return booking


@router.post("/{booking_id}/confirm")
async def confirm_booking(booking_id: int, current_user: User = Depends(require_role("FARMER")), db: AsyncSession = Depends(get_db)):
    async with db.begin():
        res = await db.execute(select(BookingRequest).where(BookingRequest.id == booking_id).with_for_update())
        booking = res.scalars().first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        if booking.farmer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not your booking")
        if booking.status not in ("CONFIRMATION_PENDING", "QUEUED"):
            raise HTTPException(status_code=400, detail="Booking cannot be confirmed in current status")
        # If QUEUED, only allow confirm if its queue_position == 1 and there is no other confirmed overlap
        if booking.status == "QUEUED":
            if booking.queue_position != 1:
                raise HTTPException(status_code=400, detail="Not your turn to confirm")
            # promote to CONFIRMATION_PENDING first (but allow direct confirmation if no conflicts)
        # check overlap with existing CONFIRMED bookings
        q = select(BookingRequest).where(
            BookingRequest.equipment_id == booking.equipment_id,
            BookingRequest.status == "CONFIRMED"
        ).with_for_update(of=BookingRequest)
        r2 = await db.execute(q)
        confirmed = r2.scalars().all()
        for c in confirmed:
            if dates_overlap(c.start_date, c.end_date, booking.start_date, booking.end_date):
                raise HTTPException(status_code=409, detail="Equipment is already booked for requested dates")
        # mark this booking CONFIRMED
        booking.status = "CONFIRMED"
        booking.confirmation_deadline = None
        # shift other queued bookings' positions (if any) — we keep them as-is relative to their queue positions
        db.add(booking)
    await db.refresh(booking)
    return {"message": "Booking confirmed", "booking": booking}


@router.post("/{booking_id}/cancel")
async def cancel_booking(booking_id: int, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    async with db.begin():
        res = await db.execute(select(BookingRequest).where(BookingRequest.id == booking_id).with_for_update())
        booking = res.scalars().first()
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        # Only farmer who created or equipment owner or admin can cancel
        from app.auth.dependencies import require_role
        current = current_user
        is_owner = False
        eq_res = await db.execute(select(Equipment).where(Equipment.id == booking.equipment_id))
        equipment = eq_res.scalars().first()
        if current.role == "ADMIN" or booking.farmer_id == current.id or (equipment and equipment.owner_id == current.id):
            # allowed
            prev_status = booking.status
            booking.status = "CANCELLED"
            booking.queue_position = None
            booking.confirmation_deadline = None
            db.add(booking)
            # If it was CONFIRMATION_PENDING or CONFIRMED, we should promote next queued booking if any
            if prev_status in ("CONFIRMATION_PENDING", "CONFIRMED"):
                # find next queued booking overlapping the same requested window
                q = select(BookingRequest).where(
                    BookingRequest.equipment_id == booking.equipment_id,
                    BookingRequest.status == "QUEUED"
                ).order_by(BookingRequest.queue_position.asc()).with_for_update()
                r = await db.execute(q)
                nexts = r.scalars().all()
                promoted = None
                for n in nexts:
                    # ensure no confirmed booking now overlaps n
                    q2 = select(BookingRequest).where(
                        BookingRequest.equipment_id == booking.equipment_id,
                        BookingRequest.status == "CONFIRMED"
                    ).with_for_update(of=BookingRequest)
                    r2 = await db.execute(q2)
                    confirmed_now = r2.scalars().all()
                    conflict = False
                    for c in confirmed_now:
                        if dates_overlap(c.start_date, c.end_date, n.start_date, n.end_date):
                            conflict = True
                            break
                    if not conflict:
                        promoted = n
                        break
                if promoted:
                    promoted.status = "CONFIRMATION_PENDING"
                    promoted.confirmation_deadline = datetime.utcnow() + timedelta(hours=float(settings.BOOKING_CONFIRMATION_HOURS))
                    # adjust queue positions of remaining queued bookings
                    # recompute positions
                    q3 = select(BookingRequest).where(
                        BookingRequest.equipment_id == booking.equipment_id,
                        BookingRequest.status == "QUEUED"
                    ).order_by(BookingRequest.created_at.asc()).with_for_update()
                    r3 = await db.execute(q3)
                    queued = r3.scalars().all()
                    for idx, qb in enumerate(queued, start=1):
                        qb.queue_position = idx
                        db.add(qb)
                    db.add(promoted)
        else:
            raise HTTPException(status_code=403, detail="Not authorized to cancel this booking")
    return {"message": "Booking cancelled"}
