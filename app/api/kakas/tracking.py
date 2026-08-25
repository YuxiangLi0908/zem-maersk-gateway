"""Kaka Sheng shipment tracking adapter."""

from app.api.kakas.client import kakas_request


async def get_tracking(order_no: str):
    """Fetch tracking events from ``GET /shipment/tracking``."""
    return kakas_request(
        "GET", "/shipment/tracking", params={"orderNo": order_no}
    )
