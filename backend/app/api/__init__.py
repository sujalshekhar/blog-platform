from fastapi import APIRouter
from app.api.health import router as health_router
from app.api.auth import router as auth_router
from app.api.blog import router as blog_router

# Base API Router for v1 endpoints
api_router = APIRouter(prefix="/api/v1")

# Register endpoints
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(blog_router)
