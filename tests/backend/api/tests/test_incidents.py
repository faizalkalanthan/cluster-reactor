from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.main import app
from app.models.incident import Incident


pytestmark = [pytest.mark.api]


def test_list_incidents_returns_empty_collection(incident_client):
    response = incident_client.list_incidents()

    assert response.status_code == 200
    assert response.json() == []


def test_create_incident_with_valid_data(incident_client, valid_incident_data):
    response = incident_client.create_incident(valid_incident_data)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == valid_incident_data["title"]


def test_list_incidents_returns_newest_first(incident_client, api_session, incident_data):
    older = incident_data["older_incident"]
    newer = incident_data["newer_incident"]

    api_session.add(Incident(**older))
    api_session.add(Incident(**newer))
    api_session.commit()

    response = incident_client.list_incidents()

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == newer["title"]
    assert data[1]["title"] == older["title"]


def test_list_incidents_returns_503_when_database_fails(incident_client):
    broken_session = MagicMock(spec=Session)
    broken_session.scalars.side_effect = OperationalError("SELECT", {}, Exception("connection lost"))

    app.dependency_overrides[get_db_session] = lambda: broken_session
    response = incident_client.list_incidents()
    app.dependency_overrides.pop(get_db_session, None)

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()


def test_create_incident_returns_503_when_database_fails(incident_client, valid_incident_data):
    broken_session = MagicMock(spec=Session)
    broken_session.commit.side_effect = OperationalError("INSERT", {}, Exception("connection lost"))
    broken_session.rollback = MagicMock()

    app.dependency_overrides[get_db_session] = lambda: broken_session
    response = incident_client.create_incident(valid_incident_data)
    app.dependency_overrides.pop(get_db_session, None)

    assert response.status_code == 503
    assert "unavailable" in response.json()["detail"].lower()