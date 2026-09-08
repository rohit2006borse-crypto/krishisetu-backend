from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app.database import AsyncSessionLocal
from app.models.booking import BookingRequest
from app.config import settings

scheduler = AsyncIOScheduler()


async def _process_expired_confirmations():
    async with AsyncSessionLocal() as db:
        async with db.begin():
            # lock confirmation-pending rows that have deadline < now
            now = datetime.utcnow()
            q = select(BookingRequest).where(BookingRequest.status == "CONFIRMATION_PENDING", BookingRequest.confirmation_deadline < now).with_for_update()
            res = await db.execute(q)
            expired = res.scalars().all()
            for b in expired:
                b.status = "EXPIRED"
                b.confirmation_deadline = None
                b.queue_position = None
                db.add(b)
                # find next queued eligible booking for same equipment overlapping the requested window
                q2 = select(BookingRequest).where(BookingRequest.equipment_id == b.equipment_id, BookingRequest.status == "QUEUED").order_by(BookingRequest.queue_position.asc()).with_for_update()
                r2 = await db.execute(q2)
                queued = r2.scalars().all()
                promoted = None
                for qb in queued:
                    # check that there's no confirmed booking overlapping qb
                    q3 = select(BookingRequest).where(BookingRequest.equipment_id == qb.equipment_id, BookingRequest.status == "CONFIRMED").with_for_update()
                    r3 = await db.execute(q3)
                    confirmed = r3.scalars().all()
                    conflict = False
                    for c in confirmed:
                        if qb.start_date < c.end_date and qb.end_date > c.start_date:
                            conflict = True
                            break
                    if not conflict:
                        promoted = qb
                        break
                if promoted:
                    promoted.status = "CONFIRMATION_PENDING"
                    promoted.confirmation_deadline = datetime.utcnow() + timedelta(hours=float(settings.BOOKING_CONFIRMATION_HOURS))
                    # recalc queue positions for remaining queued
                    q4 = select(BookingRequest).where(BookingRequest.equipment_id == b.equipment_id, BookingRequest.status == "QUEUED").order_by(BookingRequest.created_at.asc()).with_for_update()
                    r4 = await db.execute(q4)
                    queued2 = r4.scalars().all()
                    for idx, qb2 in enumerate(queued2, start=1):
                        qb2.queue_position = idx
                        db.add(qb2)
                    db.add(promoted)
        # commit happens at context exit


def init_booking_scheduler(app: FastAPI):
    # schedule interval job every minute (configurable); safe to run repeatedly
    scheduler.add_job(_process_expired_confirmations, IntervalTrigger(seconds=30), id="booking_expiry", replace_existing=True)
    scheduler.start()
    return scheduler
