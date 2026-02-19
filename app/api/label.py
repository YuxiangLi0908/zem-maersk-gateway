import requests
from fastapi import APIRouter, Depends, HTTPException, status
from app.services.utils import verify_api_key
from app.data_models.shipment.request import LabelRequest, BOLRequest
from app.services.config import app_config

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/label", name="get_label")
async def get_label(request: LabelRequest):
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

    try:
        return resp.text
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from label service",
        )


@router.post("/bol", name="get_bol")
async def get_bol(request: BOLRequest):
    url = app_config.LABEL_API_URL

    headers = {
        "Content-Type": "text/xml",
    }

    payload = {
        "shawb": request.shawb,
        "szip": request.szip,
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
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

    try:
        return resp.text
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from BOL service",
        )
