from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from app.core.config import settings
from app.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup actions go here (e.g. database migrations, initializing Redis client)
    from app.core.logger import logger
    from app.core.redis_client import redis_client
    logger.info("Starting up the FastAPI application...")
    
    if redis_client:
        try:
            redis_client.ping()
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis on startup: {e}")
            
    yield
    # Shutdown actions go here (e.g. closing database connections, closing Redis client)
    logger.info("Shutting down the FastAPI application...")
    if redis_client:
        redis_client.close()

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000", settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the main API router placeholder
app.include_router(api_router)

