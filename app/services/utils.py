import os

from fastapi import Header, HTTPException, status


def verify_api_key(x_api_key: str = Header(...)):
    INTERNAL_API_AUTH_KEY = os.getenv("INTERNAL_API_AUTH_KEY")

    if not INTERNAL_API_AUTH_KEY:
        raise RuntimeError("API_KEY is not set")

    if x_api_key != INTERNAL_API_AUTH_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )