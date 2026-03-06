from xml.etree import ElementTree

import requests
from fastapi import APIRouter, Depends, HTTPException

from app.data_models.tracking.request import TrackingRequest
from app.services.config import app_config
from app.services.utils import verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/tracking", name="tracking")
async def get_tracking_details(request: TrackingRequest):
    url = "https://wsi.pilotdelivers.com/test/pilotpartnertracking.asmx"
    headers = {
        "Content-Type": "text/xml",
    }

    payload = f"""<?xml version=\"1.0\" encoding=\"utf-8\"?>
        <soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">
        <soap:Body>
            <PilotAPIDetailTrackingHD xmlns=\"https://www.pilotssl.com\">
            <tr>
                <Validation>
                <UserID>{app_config.MAERSK_USER_ID}</UserID>
                <Password>{app_config.MAERSK_PASSWORD}</Password>
                </Validation>
                <APIVersion>3.0</APIVersion>
                <TrackingNumber>{request.pro_number}</TrackingNumber>
            </tr>
            </PilotAPIDetailTrackingHD>
        </soap:Body>
        </soap:Envelope>
    """

    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=503, detail=f"Failed to connect to tracking service: {str(e)}"
        )

    try:
        root = ElementTree.fromstring(response.text)
        namespace = "{http://schemas.xmlsoap.org/soap/envelope/}"
        body = root.find(f"{namespace}Body")
        tracking_details = body.find(".//TrackingEventHistory")

        events = []
        for event in tracking_details.findall("TrackingEventDetail"):
            event_data = {
                "EventCode": event.find("EventCode").text,
                "EventCodeDesc": event.find("EventCodeDesc").text,
                "EventType": event.find("EventType").text,
                "EventDateTime": event.find("EventDateTime").text,
                "EventLocation": {
                    "City": event.find("EventLocation/City").text,
                    "StateProvince": event.find("EventLocation/StateProvince").text,
                    "PostalCode": event.find("EventLocation/PostalCode").text,
                    "CountryCode": event.find("EventLocation/CountryCode").text,
                },
            }
            events.append(event_data)

        return {"TrackingEvents": events}

    except ElementTree.ParseError as e:
        raise HTTPException(
            status_code=502, detail=f"Failed to parse tracking response: {str(e)}"
        )
