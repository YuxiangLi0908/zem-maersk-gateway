from fastapi import APIRouter

from app.api.common import address, heartbeat, invoice, label, rating, shipment, tracking

api_router = APIRouter()
api_router.include_router(heartbeat.router, tags=["health"])
api_router.include_router(rating.router, tags=["rating"])
api_router.include_router(shipment.router, tags=["shipment"])
api_router.include_router(label.router, tags=["label"])
api_router.include_router(tracking.router, tags=["tracking"])
api_router.include_router(invoice.router, tags=["invoice"])
api_router.include_router(address.router, tags=["smarty_address"])
