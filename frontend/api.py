from __future__ import annotations

import os
from collections.abc import Mapping
from typing import Any

import requests


BACKEND_BASE_URL = os.getenv("CLUSTER_REACTOR_API_URL", "http://127.0.0.1:8000")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("CLUSTER_REACTOR_API_TIMEOUT", "5"))


def _request(method: str, path: str, payload: Mapping[str, Any] | None = None) -> dict[str, Any]:
    url = f"{BACKEND_BASE_URL.rstrip('/')}{path}"
    response = requests.request(
        method=method,
        url=url,
        json=dict(payload) if payload is not None else None,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def get_root_status() -> dict[str, Any]:
    return _request("GET", "/")


def get_health() -> dict[str, Any]:
    return _request("GET", "/healthz")


def get_readiness() -> dict[str, Any]:
    return _request("GET", "/readyz")


def get_system_status() -> dict[str, Any]:
    return _request("GET", "/api/v1/system/status")


def list_incidents() -> list[dict[str, Any]]:
    response = _request("GET", "/api/v1/incidents")
    if not isinstance(response, list):
        raise TypeError("Expected a list of incidents from the backend API")
    return response


def create_incident(payload: Mapping[str, Any]) -> dict[str, Any]:
    return _request("POST", "/api/v1/incidents", payload=payload)