import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import engine
from app.models import Base
from app.schemas import HealthResponse
from app.routes.webhooks import router as webhooks_router
from app.routes.transactions import router as transactions_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler — creates DB tables on startup."""
    logger.info("Starting up: creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")
    yield
    logger.info("Shutting down...")
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "A service that receives transaction webhooks from external payment "
        "processors, acknowledges them immediately, and processes transactions "
        "reliably in the background."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhooks_router)
app.include_router(transactions_router)


@app.get(
    "/",
    response_model=HealthResponse,
)
async def health_check():
    return HealthResponse(
        status="HEALTHY",
        current_time=datetime.now(timezone.utc),
    )
