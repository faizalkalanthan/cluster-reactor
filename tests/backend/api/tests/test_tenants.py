import pytest


pytestmark = [pytest.mark.api]


def test_create_tenant_with_valid_data(tenant_client, valid_tenant_data):
    response = tenant_client.create_tenant(valid_tenant_data)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["name"] == valid_tenant_data["name"]


def test_get_existing_tenant(tenant_client, valid_tenant_data):
    create_response = tenant_client.create_tenant(valid_tenant_data)

    assert create_response.status_code == 201
    tenant_id = create_response.json()["id"]

    response = tenant_client.get_tenant(tenant_id)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == tenant_id


def test_update_existing_tenant(tenant_client, valid_tenant_data, updated_tenant_data):
    create_response = tenant_client.create_tenant(valid_tenant_data)

    assert create_response.status_code == 201
    tenant_id = create_response.json()["id"]

    response = tenant_client.update_tenant(tenant_id, updated_tenant_data)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == updated_tenant_data["name"]
    assert data["domain"] == updated_tenant_data["domain"]


def test_delete_existing_tenant(tenant_client, valid_tenant_data):
    create_response = tenant_client.create_tenant(valid_tenant_data)

    assert create_response.status_code == 201
    tenant_id = create_response.json()["id"]

    delete_response = tenant_client.delete_tenant(tenant_id)
    assert delete_response.status_code == 204

    get_response = tenant_client.get_tenant(tenant_id)
    assert get_response.status_code == 404


def test_list_tenants_returns_created_tenant(tenant_client, valid_tenant_data):
    create_response = tenant_client.create_tenant(valid_tenant_data)
    assert create_response.status_code == 201

    response = tenant_client.list_tenants()

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(item["slug"] == valid_tenant_data["slug"] for item in data)