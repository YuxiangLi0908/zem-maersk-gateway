import requests
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.data_models.db.maersk_logs import MaerskShipmentLog
from app.data_models.shipment.request import ShipmentCreateRequest
from app.services.config import app_config
from app.services.db_session import db_session
from app.services.utils import get_access_token, verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/shipment", name="shipment")
async def create_shipment(
    request: ShipmentCreateRequest,
    db: Session = Depends(db_session.get_db),
    access_token: str = Depends(get_access_token),
):
    if not app_config.CLIENT_ID:
        raise RuntimeError("MAERSK_CONSUMER_KEY/CLIENT_ID is not set")

    payload = request.model_dump(exclude_none=True, mode="json")

    # Fill in fields that are not provided by the client
    payload.setdefault("tariffCode", app_config.TARIFF_CODE)
    payload.setdefault("locationId", app_config.LOCATION_ID)
    payload.setdefault("thirdParty", app_config.THIRD_PARTY)
    payload.setdefault("controlStation", app_config.CONTROL_STATION)
    payload.setdefault("payType", app_config.PAY_TYPE)

    headers = {
        "Consumer-Key": app_config.CLIENT_ID,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }

    try:
        resp = requests.post(
            app_config.SHIPMENT_API_URL,
            headers=headers,
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        # Log request and original response in case of exceptions
        log_entry = MaerskShipmentLog(
            endpoint="/shipment",
            request_data=payload,
            response_data=resp.text if resp else str(e),
        )
        db.add(log_entry)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to shipment service: {str(e)}",
        )

    # If upstream is not success, return same status and message
    if resp.status_code >= 400:
        detail: object
        try:
            detail = resp.json()
        except ValueError:
            detail = resp.text

        # Log request and original response for non-success status codes
        log_entry = MaerskShipmentLog(
            endpoint="/shipment",
            request_data=payload,
            response_data=detail,
        )
        db.add(log_entry)
        db.commit()

        raise HTTPException(status_code=resp.status_code, detail=detail)

    # Log request and response
    log_entry = MaerskShipmentLog(
        endpoint="/shipment",
        request_data=payload,
        response_data=resp.json() if resp.status_code < 400 else detail,
    )
    db.add(log_entry)
    db.commit()

    try:
        return resp.json()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid JSON response from shipment service",
        )


@router.post("/shipment/void", name="shipment_void")
async def shipment_void(
    pro_number: str, control_station: str, db: Session = Depends(db_session.get_db)
):
    if not app_config.MAERSK_API_KEY:
        raise RuntimeError("MAERSK_API_KEY is not set")

    payload = {
        "LocationId": app_config.LOCATION_ID,
        "AddressId": app_config.ADDRESS_ID,
        "ControlStation": control_station,
        "TariffHeaderID": app_config.TARIFF_HEADER_ID,
        "ProNumber": pro_number,
    }

    headers = {
        "api-key": app_config.MAERSK_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(
            f"{app_config.SHIPMENT_VOID_API_URL}/{pro_number}",
            headers=headers,
            json=payload,
            timeout=30,
        )
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to shipment void service: {str(e)}",
        )

    if resp.status_code >= 400:
        detail: object
        try:
            detail = resp.json()
        except ValueError:
            detail = resp.text

        raise HTTPException(status_code=resp.status_code, detail=detail)

    # Log request and response for shipment_void
    log_entry = MaerskShipmentLog(
        endpoint="/shipment/void",
        request_data=payload,
        response_data=resp.json() if resp.status_code < 400 else detail,
    )
    db.add(log_entry)
    db.commit()

    try:
        response_data = resp.json()
        return {
            "cancelled": not response_data.get("IsError", True),
            "originalResponse": response_data,
        }
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid JSON response from shipment void service",
        )
