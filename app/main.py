import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.api.router import api_router

app = FastAPI(title="Maersk Gateway API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    GZipMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
app.include_router(api_router)

# Configuration
PILOT_API_URL = "https://wsi.pilotdelivers.com/pilotapi/test/v1/Ratings"
API_KEY = "D82DFF02-5FA1-4D03-96E6-8B775767C35E"


@app.post("/api/v1/ratings")
async def get_rating(request: RatingRequest):
    """
    Get shipping rate from Pilot API

    Args:
        request: RatingRequest containing shipper, consignee, and line items

    Returns:
        Rating response from Pilot API
    """
    headers = {"api-key": API_KEY, "Content-Type": "application/json"}

    try:
        response = requests.post(PILOT_API_URL, headers=headers, json=request.dict())
        response.raise_for_status()

        return {"status_code": response.status_code, "data": response.json()}
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500, detail=f"Error calling Pilot API: {str(e)}"
        )
