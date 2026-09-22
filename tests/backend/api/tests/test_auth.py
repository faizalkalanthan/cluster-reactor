import pytest


pytestmark = [pytest.mark.api]


def test_login_with_valid_credentials(auth_client, auth_data):
    login_data = auth_data["admin_login"]

    response = auth_client.login(
        email=login_data["email"],
        password=login_data["password"],
        tenant_slug=login_data["tenant_slug"],
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_invalid_password(auth_client, auth_data):
    login_data = auth_data["invalid_login"]

    response = auth_client.login(
        email=login_data["email"],
        password=login_data["password"],
        tenant_slug=login_data["tenant_slug"],
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"