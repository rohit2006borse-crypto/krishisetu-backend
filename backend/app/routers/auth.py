from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, UserOut
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token

router = APIRouter()


@router.post("/register", response_model=UserOut, summary="Register a new user")
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    if user_in.is_equipment_owner and user_in.role != "FARMER":
        raise HTTPException(status_code=400, detail="Only FARMER role can be equipment owners")

    hashed = hash_password(user_in.password)
    user = User(
        name=user_in.name,
        email=user_in.email,
        phone=user_in.phone,
        password_hash=hashed,
        role=user_in.role,
        is_equipment_owner=user_in.is_equipment_owner,
        location=user_in.location,
    )
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or phone already registered")

    return user


@router.post("/login", summary="Login and get access token")
async def login(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalars().first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.get("/me", response_model=UserOut, summary="Get current authenticated user")
async def me(current_user: User = Depends(lambda: None)):  # replaced below when wiring imports
    return current_user
