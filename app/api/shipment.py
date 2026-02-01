import requests
from fastapi import APIRouter, Depends, HTTPException, status

from app.data_models.shipment.request import ShipmentCreateRequest
from app.services.config import app_config
from app.services.utils import verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/shipment", name="shipment")
async def create_shipment(request: ShipmentCreateRequest):
	if not app_config.CLIENT_ID:
		raise RuntimeError("MAERSK_CONSUMER_KEY/CLIENT_ID is not set")

	payload = request.model_dump(exclude_none=True, mode="json")

	# Fill in fields that are not provided by the client
	payload.setdefault("tariffCode", app_config.TARIFF_CODE)
	payload.setdefault("locationId", app_config.LOCATION_ID)
	payload.setdefault("thirdParty", app_config.THIRD_PARTY)

	headers = {
		"Consumer-Key": app_config.CLIENT_ID,
		"Content-Type": "application/json",
	}

	try:
		resp = requests.post(
			app_config.SHIPMENT_API_URL,
			headers=headers,
			json=payload,
			timeout=30,
		)
	except requests.exceptions.RequestException as e:
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

		raise HTTPException(status_code=resp.status_code, detail=detail)

	try:
		return resp.json()
	except ValueError:
		raise HTTPException(
			status_code=status.HTTP_502_BAD_GATEWAY,
			detail="Invalid JSON response from shipment service",
		)
