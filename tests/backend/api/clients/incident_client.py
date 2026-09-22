from __future__ import annotations

from tests.backend.api.clients.base_client import BaseClient
from tests.backend.api.config.config import ApiTestConfig


class IncidentClient(BaseClient):
    """Client for incident endpoints."""

    def list_incidents(self):
        response = self.get(ApiTestConfig.INCIDENTS_ENDPOINT)
        return response

    def create_incident(self, data: dict):
        response = self.post(ApiTestConfig.INCIDENTS_ENDPOINT, data=data)
        return response