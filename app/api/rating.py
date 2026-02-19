import requests
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError

from app.data_models.rating.line_item import LineItem
from app.data_models.rating.rating import Rating
from app.data_models.request_model import RatingRequest
from app.services.config import app_config
from app.services.utils import verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/rating", name="rating")
async def get_rating(request: RatingRequest):
    headers = {"api-key": app_config.MAERSK_API_KEY, "Content-Type": "application/json"}

    # Validate each line item
    try:
        validated_line_items = [
            LineItem(**item) if isinstance(item, dict) else item
            for item in request.lineItems
        ]
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid line item data: {e.errors()}",
        )

    data = {
        "rating": Rating(
            shipper={"zipcode": request.origin_zip},
            consignee={"zipcode": request.dest_zip},
            lineItems=validated_line_items,
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
        raise HTTPException(status_code=resp.status_code, detail=resp.text or str(e))
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to rating service: {str(e)}",
        )

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

    # Filter quotes for services BR and 72
    filtered_quotes = []
    for quote in response_data["dsQuote"]["Quote"]:
        if quote.get("Service") in ["BR", "72"]:
            quote_id = quote.get("Quote_Id")

            # Find corresponding breakdowns for this quote
            breakdowns = [
                breakdown
                for breakdown in response_data["dsQuote"]["Breakdown"]
                if breakdown.get("Quote_Id") == quote_id
            ]

            # Add breakdowns to the quote
            quote["Breakdowns"] = breakdowns
            filtered_quotes.append(quote)

    result = {
        "rating": response_data["dsQuote"]["Rating"][0],
        "shipper": response_data["dsQuote"]["Shipper"][0],
        "consignee": response_data["dsQuote"]["Consignee"][0],
        "lineitems": response_data["dsQuote"]["LineItems"],
        "quotes": filtered_quotes,
    }
    return result
