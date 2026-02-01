from fastapi import APIRouter

from app.api import heartbeat, rating, shipment

api_router = APIRouter()
api_router.include_router(heartbeat.router, tags=["health"])
api_router.include_router(rating.router, tags=["rating"])
api_router.include_router(shipment.router, tags=["shipment"])
