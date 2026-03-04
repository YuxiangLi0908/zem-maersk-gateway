import requests
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.data_models.db.maersk_logs import MaerskLabelLog
from app.data_models.shipment.request import BOLRequest, LabelRequest
from app.services.config import app_config
from app.services.db_session import db_session
from app.services.utils import verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/label", name="get_label")
async def get_label(request: LabelRequest, db: Session = Depends(db_session.get_db)):
    url = f"{app_config.LABEL_API_URL}/HAWBLabel?shawb={request.shawb}&eLabelType={request.eLabelType}&szip={request.szip}"

    try:
        resp = requests.get(url, timeout=30)
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to label service: {str(e)}",
        )

    if resp.status_code >= 400:
        detail: object
        try:
            detail = resp.json()
        except ValueError:
            detail = resp.text

        raise HTTPException(status_code=resp.status_code, detail=detail)

    # Log request and response for label endpoint
    # log_entry = MaerskLabelLog(
    #     endpoint="/label",
    #     request_data=request.dict(),
    #     response_data=resp.json() if resp.status_code < 400 else resp.text,
    # )
    # db.add(log_entry)
    # db.commit()

    try:
        return resp.text
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from label service",
        )


@router.post("/bol", name="get_bol")
async def get_bol(request: BOLRequest, db: Session = Depends(db_session.get_db)):
    url = app_config.LABEL_API_URL

    headers = {
        "Content-Type": "text/xml",
    }

    payload = f"""<?xml version="1.0" encoding="utf-8"?>
        <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema"
        xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
            <soap:Body>
                <HAWBDocument xmlns="http://tempuri.org/">
                    <shawb>{request.shawb}</shawb>
                    <szip>{request.szip}</szip>
                </HAWBDocument>
            </soap:Body>
        </soap:Envelope>
    """

    try:
        resp = requests.post(url, headers=headers, data=payload, timeout=30)
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to BOL service: {str(e)}",
        )

    if resp.status_code >= 400:
        detail: object
        try:
            detail = resp.json()
        except ValueError:
            detail = resp.text

        raise HTTPException(status_code=resp.status_code, detail=detail)

    # Log request and response for bol endpoint
    # log_entry = MaerskLabelLog(
    #     endpoint="/bol",
    #     request_data=request.dict(),
    #     response_data=resp.json() if resp.status_code < 400 else resp.text,
    # )
    # db.add(log_entry)
    # db.commit()

    try:
        return resp.text
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from BOL service",
        )
