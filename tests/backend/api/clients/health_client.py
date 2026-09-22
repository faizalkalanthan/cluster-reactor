from __future__ import annotations

from tests.backend.api.clients.base_client import BaseClient
from tests.backend.api.config.config import ApiTestConfig


class HealthClient(BaseClient):
    """Client for health and readiness endpoints."""

    def get_health(self):
        response = self.get(ApiTestConfig.HEALTH_ENDPOINT)
        return response

    def get_readiness(self):
        response = self.get(ApiTestConfig.READINESS_ENDPOINT)
        return response