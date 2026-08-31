"""Kaka Sheng shipment invoice adapter."""

from app.api.kakas.client import kakas_request


async def get_invoice(order_no: str):
    """Fetch invoice transactions from ``GET /shipment/invoice``."""
    return kakas_request(
        "GET", "/shipment/invoice", params={"orderNo": order_no}
    )
