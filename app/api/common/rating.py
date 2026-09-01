"""Public rating endpoint and multi-carrier orchestration."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.abf.rating import get_rating as get_abf_rating
from app.api.common.carriers import Carrier, DIRECT_CARRIERS
from app.api.kakas.rating import get_rating as get_kakas_rating
from app.api.kakas.rating import get_rating_result as get_kakas_rating_result
from app.api.maersk.rating import get_rating as get_maersk_rating
from app.data_models.request_model import RatingRequest
from app.services.db_session import db_session
from app.services.utils import verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])

RATING_HANDLERS = {
    Carrier.MAERSK: get_maersk_rating,
    Carrier.KAKAS: get_kakas_rating,
    Carrier.ABF: get_abf_rating,
}


def _carrier_from_payload(payload: dict) -> Carrier:
    try:
        return Carrier(payload.get("carrier", Carrier.MAERSK))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Unsupported carrier") from exc


def _kakas_freight_classes(payload: dict) -> list[str]:
    carrier_payloads = payload.get("carrierPayloads")
    kakas_payload = (
        carrier_payloads.get(Carrier.KAKAS.value, {})
        if isinstance(carrier_payloads, dict)
        else {}
    )
    commodity_list = kakas_payload.get("commodityList", [])
    if not isinstance(commodity_list, list):
        return []

    freight_classes = []
    for commodity in commodity_list:
        if not isinstance(commodity, dict):
            continue
        freight_class = str(commodity.get("freightClass") or "").strip()
        if freight_class and freight_class not in freight_classes:
            freight_classes.append(freight_class)
    return freight_classes


async def _get_one_rating(carrier: Carrier, payload: dict, db: Session):
    carrier_payloads = payload.get("carrierPayloads")
    if isinstance(carrier_payloads, dict) and carrier.value in carrier_payloads:
        selected_payload = carrier_payloads[carrier.value]
        if not isinstance(selected_payload, dict):
            raise HTTPException(
                status_code=422,
                detail=f"carrierPayloads.{carrier.value} must be an object",
            )
        payload = {**selected_payload, "carrier": carrier.value}

    if carrier == Carrier.MAERSK:
        try:
            request = RatingRequest.model_validate({**payload, "carrier": carrier})
        except ValidationError as exc:
            raise HTTPException(status_code=422, detail=exc.errors()) from exc
        return await get_maersk_rating(request, db)
    return await RATING_HANDLERS[carrier](payload, db)


@router.post("/rating", name="rating")
async def get_rating(request: dict, db: Session = Depends(db_session.get_db)):
    """Get one carrier quote, or collect every carrier result with ``carrier=all``.

    Multi-carrier callers may provide ``carrierPayloads`` so each adapter receives
    its own native request schema while the public API remains a single request.
    """
    carrier_selector = _carrier_from_payload(request)
    if carrier_selector != Carrier.ALL:
        return await _get_one_rating(carrier_selector, request, db)

    results = {}
    for carrier in DIRECT_CARRIERS:
        try:
            results[carrier.value] = {
                "status": "success",
                "data": await _get_one_rating(carrier, request, db),
            }
        except HTTPException as exc:
            results[carrier.value] = {
                "status": "not_configured" if exc.status_code == 501 else "failed",
                "error": exc.detail,
            }
        except Exception:
            results[carrier.value] = {
                "status": "failed",
                "error": f"{carrier.value} rating service failed unexpectedly",
            }

    response = {"carrier": Carrier.ALL, "results": results}
    freight_classes = _kakas_freight_classes(request)
    if freight_classes:
        response["freightClass"] = freight_classes[0]
        response["freightClasses"] = freight_classes
    return response


@router.get("/rating", name="rating_result")
async def get_rating_result(uuid: str, carrier: Carrier):
    """Fetch an asynchronous carrier quote by its request UUID."""
    if carrier == Carrier.ALL:
        raise HTTPException(status_code=400, detail="获取报价不支持 carrier=all")
    if carrier != Carrier.KAKAS:
        raise HTTPException(
            status_code=501,
            detail=f"{carrier.value} 暂不需要通过 UUID 获取报价",
        )
    return await get_kakas_rating_result(uuid)
