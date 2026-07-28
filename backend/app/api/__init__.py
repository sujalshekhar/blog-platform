from fastapi import APIRouter
from app.api.health import router as health_router

# Base API Router for v1 endpoints
api_router = APIRouter(prefix="/api/v1")

# Register endpoints
api_router.include_router(health_router)

