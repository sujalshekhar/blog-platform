from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from app.core.config import settings
from app.api import api_router

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup actions go here (e.g. database migrations, initializing Redis client)
    yield
    # Shutdown actions go here (e.g. closing database connections, closing Redis client)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Register the main API router placeholder
app.include_router(api_router)

