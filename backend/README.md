# Krishisetu — Backend (FastAPI)

Scaffold for the Krishisetu project backend using FastAPI + PostgreSQL (async) + SQLAlchemy.

Quick start (development)
1. Copy `.env.example` to `.env` and update values.
2. Create a Python 3.11+ venv, install requirements:
   - python -m venv .venv
   - source .venv/bin/activate
   - pip install -r requirements.txt
3. Start PostgreSQL and ensure DATABASE_URL works.
4. Run Alembic migrations (recommended):
   - alembic init alembic
   - configure alembic.ini and env.py to use app.database engine/session
   - generate and apply migrations
   Alternatively for quick dev only: use SQLAlchemy create_all (not for production).
5. Start app:
   - uvicorn app.main:app --reload

Notes
- BOOKING_CONFIRMATION_HOURS can be set small (0.0333) for quick testing of the scheduler.
- Alembic migrations are required for production correctness — do not rely on create_all in production.
