"""Public document endpoints routed to a selected carrier."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.common.carriers import Carrier
from app.api.maersk.label import get_bol as get_maersk_bol
from app.api.maersk.label import get_label as get_maersk_label
from app.data_models.shipment.request import BOLRequest, LabelRequest
from app.services.db_session import db_session
from app.services.utils import verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])


def _require_maersk(carrier: Carrier) -> None:
    if carrier == Carrier.ALL:
        raise HTTPException(status_code=400, detail="单据获取不支持 carrier=all")
    if carrier != Carrier.MAERSK:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"{carrier.value} 单据接口尚未配置",
        )


@router.post("/label", name="get_label")
async def get_label(request: LabelRequest, db: Session = Depends(db_session.get_db)):
    _require_maersk(request.carrier)
    return await get_maersk_label(request, db)


@router.post("/bol", name="get_bol")
async def get_bol(request: BOLRequest, db: Session = Depends(db_session.get_db)):
    _require_maersk(request.carrier)
    return await get_maersk_bol(request, db)

