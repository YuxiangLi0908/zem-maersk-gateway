"""Public tracking endpoint routed to a selected carrier."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.common.carriers import Carrier
from app.api.kakas.tracking import get_tracking as get_kakas_tracking
from app.api.maersk.tracking import get_tracking_details as get_maersk_tracking
from app.data_models.tracking.request import TrackingRequest
from app.services.utils import verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/tracking", name="tracking")
async def get_tracking_details(request: TrackingRequest):
    if request.carrier == Carrier.ALL:
        raise HTTPException(status_code=400, detail="追踪不支持 carrier=all")
    if request.carrier != Carrier.MAERSK:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"{request.carrier.value} 追踪接口尚未配置",
        )
    return await get_maersk_tracking(request)


@router.get("/tracking", name="tracking_by_order")
async def get_tracking(order_no: str, carrier: Carrier):
    if carrier == Carrier.ALL:
        raise HTTPException(status_code=400, detail="订单轨迹不支持 carrier=all")
    if carrier != Carrier.KAKAS:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"{carrier.value} 按订单号查询轨迹的接口尚未配置",
        )
    return await get_kakas_tracking(order_no)
