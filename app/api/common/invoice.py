"""Public invoice endpoint routed to a selected carrier."""

from fastapi import APIRouter, Depends, HTTPException

from app.api.common.carriers import Carrier
from app.api.kakas.invoice import get_invoice as get_kakas_invoice
from app.services.utils import verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.get("/invoice", name="invoice")
async def get_invoice(order_no: str, carrier: Carrier):
    if carrier == Carrier.ALL:
        raise HTTPException(status_code=400, detail="订单发票不支持 carrier=all")
    if carrier != Carrier.KAKAS:
        raise HTTPException(
            status_code=501,
            detail=f"{carrier.value} 订单发票接口尚未配置",
        )
    return await get_kakas_invoice(order_no)
