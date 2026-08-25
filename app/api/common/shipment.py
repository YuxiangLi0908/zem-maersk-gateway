"""Public shipment endpoints routed to a selected carrier."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.common.carriers import Carrier
from app.api.kakas.shipment import create_shipment as create_kakas_shipment
from app.api.kakas.shipment import get_shipment as get_kakas_shipment
from app.api.maersk.shipment import create_shipment as create_maersk_shipment
from app.api.maersk.shipment import shipment_void as void_maersk_shipment
from app.data_models.shipment.request import ShipmentCreateRequest
from app.services.db_session import db_session
from app.services.utils import get_access_token, verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])


def _require_void_supported(carrier: Carrier) -> None:
    if carrier == Carrier.ALL:
        raise HTTPException(status_code=400, detail="取消不支持 carrier=all")
    if carrier != Carrier.MAERSK:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"{carrier.value} 取消接口尚未配置",
        )


def _carrier_from_payload(payload: dict) -> Carrier:
    try:
        return Carrier(payload.get("carrier", Carrier.MAERSK))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Unsupported carrier") from exc


@router.post("/shipment", name="shipment")
async def create_shipment(
    request: dict, db: Session = Depends(db_session.get_db)
):
    carrier = _carrier_from_payload(request)
    if carrier == Carrier.ALL:
        raise HTTPException(status_code=400, detail="下单不支持 carrier=all")
    if carrier == Carrier.KAKAS:
        return await create_kakas_shipment(request)
    if carrier == Carrier.ABF:
        raise HTTPException(status_code=501, detail="abf 下单接口尚未配置")

    try:
        maersk_request = ShipmentCreateRequest.model_validate(
            {**request, "carrier": Carrier.MAERSK}
        )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    return await create_maersk_shipment(
        maersk_request, db, get_access_token()
    )


@router.get("/shipment", name="shipment_info")
async def get_shipment(order_no: str, carrier: Carrier):
    if carrier == Carrier.ALL:
        raise HTTPException(status_code=400, detail="订单信息不支持 carrier=all")
    if carrier != Carrier.KAKAS:
        raise HTTPException(
            status_code=501,
            detail=f"{carrier.value} 订单信息接口尚未配置",
        )
    return await get_kakas_shipment(order_no)


@router.post("/shipment/void", name="shipment_void")
async def shipment_void(
    pro_number: str,
    control_station: str,
    carrier: Carrier = Carrier.MAERSK,
    db: Session = Depends(db_session.get_db),
):
    _require_void_supported(carrier)
    return await void_maersk_shipment(pro_number, control_station, db)
