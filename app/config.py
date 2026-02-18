import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./transactions.db"
    )
    APP_NAME: str = "Transaction Webhook Service"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
