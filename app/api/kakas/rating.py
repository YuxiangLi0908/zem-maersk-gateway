"""Kaka Sheng (卡卡省) quote request adapter."""

from fastapi import HTTPException
from pydantic import ValidationError

from app.api.kakas.client import kakas_request
from app.data_models.kakas.rating import KakasQuoteRequest


async def get_rating(request, *_args, **_kwargs):
    """Submit ``POST /shipment/quote`` and return the carrier response."""
    raw_payload = (
        request.model_dump(exclude={"carrier"}, exclude_none=True, mode="json")
        if hasattr(request, "model_dump")
        else dict(request)
    )
    raw_payload.pop("carrier", None)
    try:
        payload = KakasQuoteRequest.model_validate(raw_payload).model_dump(
            exclude_none=True, mode="json"
        )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc

    return kakas_request("POST", "/shipment/quote", json=payload)


async def get_rating_result(uuid: str):
    """Fetch completed quote details from ``GET /shipment/getQuotes``."""
    return kakas_request("GET", "/shipment/getQuotes", params={"uuid": uuid})
