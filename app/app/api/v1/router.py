"""
API v1 — Aggregated Router
"""

from fastapi import APIRouter
from app.api.v1.endpoints import monitors

api_router = APIRouter()

api_router.include_router(monitors.router, prefix="/monitors", tags=["monitors"])
