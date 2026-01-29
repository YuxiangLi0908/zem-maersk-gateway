import requests
from fastapi import APIRouter, Depends, HTTPException, status

from app.data_models.rating.rating import Rating
from app.data_models.request_model import RatingRequest
from app.services.config import app_config
from app.services.utils import verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/rating", name="rating")
async def get_rating(request: RatingRequest):
    headers = {"api-key": app_config.MAERSK_API_KEY, "Content-Type": "application/json"}
    data = {
        "rating": Rating(
            shipper={"zipcode": request.origin_zip},
            consignee={"zipcode": request.dest_zip},
            lineItems=request.lineItems,
            locationID=app_config.ADDRESS_ID,
            tariffHeaderID=app_config.TARIFF_HEADER_ID,
            shipDate=request.shipDate,
        ).model_dump()
    }

    try:
        resp = requests.post(
            app_config.RATE_API_URL, headers=headers, json=data, timeout=30
        )
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Return same error code and message from the API
        raise HTTPException(status_code=resp.status_code, detail=resp.text or str(e))
    except requests.exceptions.RequestException as e:
        # Network or connection errors
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to rating service: {str(e)}",
        )

    # Parse the response
    try:
        response_data = resp.json()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid JSON response from rating service",
        )

    # Check if the API returned an error in the response body
    if response_data.get("IsError", False):
        error_message = response_data.get(
            "Message", "Unknown error from Maersk rating service"
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error_message
        )

    return response_data
