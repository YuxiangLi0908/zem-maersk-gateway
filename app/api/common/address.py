"""Public address validation endpoint (not tied to a carrier)."""

import requests
from fastapi import APIRouter, Depends, HTTPException

from app.services.config import app_config
from app.data_models.address_request import AddressRequest
from app.services.utils import verify_api_key

router = APIRouter(dependencies=[Depends(verify_api_key)])


@router.post("/get_rdi", name="get_rdi")
async def get_rdi(address: AddressRequest):
    url = "https://us-street.api.smarty.com/street-address"
    params = {
        "auth-id": app_config.SMARTY_AUTH_ID,
        "auth-token": app_config.SMARTY_AUTH_TOKEN,
    }
    print(params)
    headers = {
        "Content-Type": "application/json; charset=utf-8",
    }

    try:
        response = requests.post(url, params=params, headers=headers, json=[address.dict()], timeout=30)
        response.raise_for_status()
        response_data = response.json()

        if not response_data or "metadata" not in response_data[0]:
            raise HTTPException(status_code=404, detail="RDI value not found for the given address.")

        return {
            "address": address.dict(),
            "rdi": response_data[0]["metadata"]["rdi"]
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Failed to connect to Smarty API: {str(e)}")
    except KeyError:
        raise HTTPException(status_code=500, detail="Unexpected response format from Smarty API.")
