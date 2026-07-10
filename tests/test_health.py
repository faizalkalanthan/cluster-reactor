from fastapi.testclient import TestClient

import app.api.routes.health as health

from app.main import app

client = TestClient(app)


def test_healthz() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readyz() -> None:
    original_check = health.check_database_connection
    health.check_database_connection = lambda: (True, "available")

    response = client.get("/readyz")
    health.check_database_connection = original_check

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
    assert response.json()["checks"]["database"] == "available"


def test_readyz_returns_503_when_database_is_unavailable() -> None:
    original_check = health.check_database_connection
    health.check_database_connection = lambda: (False, "connection refused")

    response = client.get("/readyz")
    health.check_database_connection = original_check

    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert response.json()["checks"]["database"] == "unavailable"