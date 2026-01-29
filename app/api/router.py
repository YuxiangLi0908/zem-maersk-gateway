from fastapi import APIRouter

from app.api import heartbeat, login, order_tracking

api_router = APIRouter()
api_router.include_router(heartbeat.router, tags=["health"])
