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
            locationID=app_config.LOCATION_ID,
            tariffHeaderID=app_config.TARIFF_HEADER_ID,
            shipDate=request.shipDate,
        ).model_dump()
    }
    resp = requests.post(app_config.RATE_API_URL, headers=headers, json=data)
    return resp.json()
