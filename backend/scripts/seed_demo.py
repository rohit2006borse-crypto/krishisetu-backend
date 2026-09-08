#!/usr/bin/env python
# Simple demo seeding script for Krishisetu backend
# Run: python scripts/seed_demo.py (from backend/ directory; ensure venv active and .env set)

import asyncio
from app.database import AsyncSessionLocal
from app.auth.password import hash_password
from app.models.user import User
from app.models.product import Product
from app.models.equipment import Equipment

async def seed():
    async with AsyncSessionLocal() as session:
        async with session.begin():
            # create admin
            admin = User(
                name='Admin',
                email='admin@example.com',
                phone='9000000000',
                password_hash=hash_password('adminpass'),
                role='ADMIN',
                is_equipment_owner=False,
                location='HQ'
            )
            session.add(admin)

            # vendor
            vendor = User(
                name='Vendor One',
                email='vendor@example.com',
                phone='9000000001',
                password_hash=hash_password('vendorpass'),
                role='VENDOR',
                is_equipment_owner=False,
                location='Village'
            )
            session.add(vendor)

            # farmer + equipment owner
            farmer = User(
                name='Farmer Joe',
                email='farmer@example.com',
                phone='9000000002',
                password_hash=hash_password('farmerpass'),
                role='FARMER',
                is_equipment_owner=True,
                location='Farmville'
            )
            session.add(farmer)

            # products by vendor
            p1 = Product(vendor_id=2, name='Wheat Seeds', category='SEEDS', price=150.00, stock=100, description='High yield seeds')
            p2 = Product(vendor_id=2, name='Urea Fertilizer', category='FERTILIZER', price=500.00, stock=50, description='Nitrogen rich')
            session.add_all([p1, p2])

            # equipment by farmer (owner_id will be 3 if inserted in this order)
            eq = Equipment(owner_id=3, type='TRACTOR', name='Farm Tractor', description='Good condition', specifications='HP:50', rate=1000.00, rate_unit='DAY', location='Farmville')
            session.add(eq)

        await session.commit()
    print('Seeding completed')

if __name__ == '__main__':
    asyncio.run(seed())
