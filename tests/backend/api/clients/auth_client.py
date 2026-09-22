from __future__ import annotations

from tests.backend.api.clients.base_client import BaseClient
from tests.backend.api.config.config import ApiTestConfig


class AuthClient(BaseClient):
    """Client for authentication endpoints."""

    def login(self, email: str, password: str, tenant_slug: str) -> object:
        payload = {
            "email": email,
            "password": password,
            "tenant_slug": tenant_slug,
        }
        response = self.post(ApiTestConfig.LOGIN_ENDPOINT, data=payload)
        return response