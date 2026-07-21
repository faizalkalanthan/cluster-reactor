from collections.abc import Generator
from unittest.mock import MagicMock
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db_session
from app.main import app
from app.models import Incident


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)


def override_get_db_session() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db_session] = override_get_db_session
client = TestClient(app)


def setup_function() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_list_incidents_returns_empty_collection() -> None:
    response = client.get("/api/v1/incidents")

    assert response.status_code == 200
    assert response.json() == []


def test_create_incident_persists_and_returns_payload() -> None:
    response = client.post(
        "/api/v1/incidents",
        json={
            "title": "Database latency spike",
            "description": "Synthetic incident for Phase 1 API coverage.",
            "severity": "sev-2",
            "status": "open",
            "affected_service": "postgresql",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["title"] == "Database latency spike"
    assert payload["severity"] == "sev-2"
    assert payload["affected_service"] == "postgresql"
    assert payload["id"] > 0


def test_list_incidents_returns_newest_first() -> None:
    session = TestingSessionLocal()
    try:
        session.add_all(
            [
                Incident(title="Older incident", severity="sev-3", status="open", affected_service="backend"),
                Incident(title="Newer incident", severity="sev-1", status="acknowledged", affected_service="database"),
            ]
        )
        session.commit()
    finally:
        session.close()

    response = client.get("/api/v1/incidents")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert payload[0]["title"] == "Newer incident"
    assert payload[1]["title"] == "Older incident"


def test_list_incidents_returns_503_on_db_failure() -> None:
    """Route must return 503 when a SQLAlchemy error occurs during SELECT."""
    broken_session = MagicMock(spec=Session)
    broken_session.scalars.side_effect = OperationalError("SELECT", {}, Exception("connection lost"))

    app.dependency_overrides[get_db_session] = lambda: broken_session
    response = client.get("/api/v1/incidents")
    app.dependency_overrides[get_db_session] = override_get_db_session

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


def test_create_incident_returns_503_on_db_failure() -> None:
    """Route must return 503 and not expose raw traceback when commit fails."""
    broken_session = MagicMock(spec=Session)
    broken_session.commit.side_effect = OperationalError("INSERT", {}, Exception("connection lost"))

    app.dependency_overrides[get_db_session] = lambda: broken_session
    response = client.post(
        "/api/v1/incidents",
        json={
            "title": "DB failure test incident",
            "severity": "sev-3",
            "status": "open",
            "affected_service": "backend",
        },
    )
    app.dependency_overrides[get_db_session] = override_get_db_session

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()