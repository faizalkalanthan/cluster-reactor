from __future__ import annotations

from typing import Any

from fastapi.testclient import TestClient


class BaseClient:
    """Simple wrapper around FastAPI TestClient.

    The methods below are not test cases.
    They are helper methods used by test cases.
    """

    def __init__(self, client: TestClient, token: str | None = None) -> None:
        self.client = client
        self.token = token

    def set_token(self, token: str) -> None:
        self.token = token

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def get(self, endpoint: str, params: dict[str, Any] | None = None):
        response = self.client.get(endpoint, params=params, headers=self._headers())
        return response

    def post(self, endpoint: str, data: dict[str, Any]):
        response = self.client.post(endpoint, json=data, headers=self._headers())
        return response

    def put(self, endpoint: str, data: dict[str, Any]):
        response = self.client.put(endpoint, json=data, headers=self._headers())
        return response

    def patch(self, endpoint: str, data: dict[str, Any]):
        response = self.client.patch(endpoint, json=data, headers=self._headers())
        return response

    def delete(self, endpoint: str):
        response = self.client.delete(endpoint, headers=self._headers())
        return response