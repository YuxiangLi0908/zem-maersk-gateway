from fastapi import APIRouter

from app.api import heartbeat, rating

api_router = APIRouter()
api_router.include_router(heartbeat.router, tags=["health"])
api_router.include_router(rating.router, tags=["rating"])
