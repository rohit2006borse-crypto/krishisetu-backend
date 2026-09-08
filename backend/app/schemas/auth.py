from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    phone: str = Field(..., min_length=6)
    password: str = Field(..., min_length=6)
    role: str = Field(..., description="FARMER | VENDOR | ADMIN")
    location: str | None = None
    is_equipment_owner: bool = False


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    role: str
    is_equipment_owner: bool
    location: str | None
    created_at: datetime | None

    class Config:
        from_attributes = True
