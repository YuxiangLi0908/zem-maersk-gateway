"""Shared HTTP client behavior for the Kaka Sheng carrier API."""

from typing import Any

import requests
from fastapi import HTTPException, status

from app.services.config import app_config


def kakas_request(
    method: str,
    path: str,
    *,
    params: dict[str, Any] | None = None,
    json: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if not app_config.KAKAS_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="KAKAS_API_KEY is not configured",
        )

    try:
        response = requests.request(
            method,
            f"{app_config.KAKAS_API_BASE_URL}{path}",
            headers={
                "API-KEY": app_config.KAKAS_API_KEY,
                "Content-Type": "application/json",
            },
            params=params,
            json=json,
            timeout=30,
        )
    except requests.exceptions.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Failed to connect to Kaka Sheng service: {exc}",
        ) from exc

    try:
        response_data = response.json()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid JSON response from Kaka Sheng service",
        ) from exc

    if response.status_code >= 400:
        raise HTTPException(status_code=response.status_code, detail=response_data)
    return response_data
