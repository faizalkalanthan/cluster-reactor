from __future__ import annotations

from tests.backend.api.clients.base_client import BaseClient
from tests.backend.api.config.config import ApiTestConfig


class TenantClient(BaseClient):
    """Client for tenant management endpoints."""

    def create_tenant(self, data: dict):
        response = self.post(ApiTestConfig.TENANTS_ENDPOINT, data=data)
        return response

    def list_tenants(self):
        response = self.get(ApiTestConfig.TENANTS_ENDPOINT)
        return response

    def get_tenant(self, tenant_id: int):
        response = self.get(f"{ApiTestConfig.TENANTS_ENDPOINT}/{tenant_id}")
        return response

    def update_tenant(self, tenant_id: int, data: dict):
        response = self.put(f"{ApiTestConfig.TENANTS_ENDPOINT}/{tenant_id}", data=data)
        return response

    def delete_tenant(self, tenant_id: int):
        response = self.delete(f"{ApiTestConfig.TENANTS_ENDPOINT}/{tenant_id}")
        return response