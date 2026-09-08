from typing import List
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    BOOKING_CONFIRMATION_HOURS: float = 24.0
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    RAZORPAY_KEY_ID: str | None = None
    RAZORPAY_KEY_SECRET: str | None = None
    ENV: str = "development"

    @validator("CORS_ORIGINS", pre=True)
    def _split_origins(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
