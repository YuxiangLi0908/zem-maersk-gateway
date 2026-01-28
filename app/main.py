from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from typing import List

app = FastAPI(title="Maersk Gateway API", version="1.0.0")


# Pydantic models for request validation
class ShipperConsignee(BaseModel):
    Zipcode: str


class LineItem(BaseModel):
    description: str
    height: str
    length: str
    pieces: str
    weight: str
    width: str


class Rating(BaseModel):
    shipper: ShipperConsignee
    Consignee: ShipperConsignee
    lineItems: List[LineItem]
    locationID: str
    shipDate: str
    tariffHeaderID: str


class RatingRequest(BaseModel):
    rating: Rating


# Configuration
PILOT_API_URL = "https://wsi.pilotdelivers.com/pilotapi/test/v1/Ratings"
API_KEY = "D82DFF02-5FA1-4D03-96E6-8B775767C35E"


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Maersk Gateway API is running", "status": "healthy"}

@app.get("/heartbeat")
async def heartbeat():
    """Health check endpoint"""
    return {"message": "heartbeat", "status": "healthy"}

@app.post("/api/v1/ratings")
async def get_rating(request: RatingRequest):
    """
    Get shipping rate from Pilot API
    
    Args:
        request: RatingRequest containing shipper, consignee, and line items
        
    Returns:
        Rating response from Pilot API
    """
    headers = {
        'api-key': API_KEY,
        'Content-Type': "application/json"
    }
    
    try:
        response = requests.post(
            PILOT_API_URL, 
            headers=headers, 
            json=request.dict()
        )
        response.raise_for_status()
        
        return {
            "status_code": response.status_code,
            "data": response.json()
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calling Pilot API: {str(e)}"
        )
