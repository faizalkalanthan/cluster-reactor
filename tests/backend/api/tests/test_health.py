import pytest

import app.api.routes.health as health


pytestmark = [pytest.mark.api]


def test_health_endpoint_returns_ok(health_client):
    response = health_client.get_health()

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readiness_endpoint_returns_ready(health_client):
    original_check = health.check_database_connection
    health.check_database_connection = lambda: (True, "available")

    response = health_client.get_readiness()
    health.check_database_connection = original_check

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["checks"]["database"] == "available"


def test_readiness_endpoint_returns_503_when_database_is_down(health_client):
    original_check = health.check_database_connection
    health.check_database_connection = lambda: (False, "connection refused")

    response = health_client.get_readiness()
    health.check_database_connection = original_check

    assert response.status_code == 503
    data = response.json()
    assert data["status"] == "not_ready"
    assert data["checks"]["database"] == "unavailable"