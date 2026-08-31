"""Kaka Sheng shipment order and order-information adapters."""

from fastapi import HTTPException
from pydantic import ValidationError

from app.api.kakas.client import kakas_request
from app.data_models.kakas.shipment import KakasShipmentCreateRequest


async def create_shipment(request):
    raw_payload = (
        request.model_dump(exclude={"carrier"}, exclude_none=True, mode="json")
        if hasattr(request, "model_dump")
        else dict(request)
    )
    raw_payload.pop("carrier", None)
    try:
        payload = KakasShipmentCreateRequest.model_validate(raw_payload).model_dump(
            exclude_none=True, mode="json"
        )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    return kakas_request("POST", "/shipment/order", json=payload)


async def get_shipment(order_no: str):
    return kakas_request(
        "GET", "/shipment/orderInfo", params={"orderNo": order_no}
    )
