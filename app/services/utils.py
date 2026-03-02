import os

import requests
from fastapi import Header, HTTPException, status

from app.services.config import app_config


def verify_api_key(x_api_key: str = Header(...)):
    INTERNAL_API_AUTH_KEY = os.getenv("INTERNAL_API_AUTH_KEY")

    if not INTERNAL_API_AUTH_KEY:
        raise RuntimeError("API_KEY is not set")

    if x_api_key != INTERNAL_API_AUTH_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


def get_access_token():
    resp = requests.post(app_config.ACCESS_TOKEN_URL)
    token = resp.json().get("access_token")
    return token
