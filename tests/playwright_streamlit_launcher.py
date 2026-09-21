from __future__ import annotations

import json
import os
from pathlib import Path
import sys
from typing import Any

import requests


# This file is a tiny test-only launcher for the Streamlit UI.
#
# Why it exists:
# - Playwright is best when it drives a real browser against a real HTTP app.
# - But for stable tests, we do not want these browser tests to depend on a live
#   backend or database.
# - So we start the Streamlit app normally, but replace the frontend API calls
#   with deterministic fake responses before the app imports and renders.

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import frontend.api as frontend_api


# DEFAULT_PAYLOAD is our "known good" demo state.
#
# Most tests only override one or two keys from this structure.
# Everything else falls back to these defaults so the UI still has complete,
# realistic-looking data to render.
DEFAULT_PAYLOAD = {
    "root_status": {"service": "cluster-reactor-api", "status": "ok", "version": "1.0.0"},
    "health_status": {"status": "ok"},
    "readiness_status": {"status": "ready", "checks": {"database": "available"}},
    "system_status": {"service": "cluster-reactor-api", "environment": "test", "version": "1.0.0"},
    "incidents": [
        {
            "id": 2,
            "title": "API latency spike",
            "description": "Elevated p95 latency on the backend service.",
            "severity": "sev-2",
            "status": "open",
            "affected_service": "backend",
            "created_at": "2026-08-02T10:00:00Z",
        },
        {
            "id": 1,
            "title": "Database failover",
            "description": "Primary database restarted during maintenance.",
            "severity": "sev-1",
            "status": "acknowledged",
            "affected_service": "postgresql",
            "created_at": "2026-08-02T09:45:00Z",
        },
    ],
    "created_incident": {"id": 99, "affected_service": "postgresql"},
}


def _load_payload() -> dict[str, Any]:
    # The parent pytest test passes per-test data through an environment
    # variable. This keeps the launcher simple: each browser test can start the
    # same Streamlit app but with different fake backend responses.
    raw_payload = os.getenv("CR_PLAYWRIGHT_PAYLOAD")
    if not raw_payload:
        return DEFAULT_PAYLOAD
    return json.loads(raw_payload)


def _patch_frontend_api(payload: dict[str, Any]) -> None:
    # Each value uses the test payload first and the default payload second.
    # That pattern makes it easy to override only the part of the UI state a
    # specific test cares about.
    root_status = payload.get("root_status", DEFAULT_PAYLOAD["root_status"])
    health_status = payload.get("health_status", DEFAULT_PAYLOAD["health_status"])
    readiness_status = payload.get("readiness_status", DEFAULT_PAYLOAD["readiness_status"])
    system_status = payload.get("system_status", DEFAULT_PAYLOAD["system_status"])
    incidents = payload.get("incidents", DEFAULT_PAYLOAD["incidents"])
    created_incident = payload.get("created_incident", DEFAULT_PAYLOAD["created_incident"])
    list_error = payload.get("list_error")
    create_error = payload.get("create_error")

    # Monkeypatch the frontend module functions directly.
    #
    # The Streamlit app imports these functions and calls them while rendering.
    # By reassigning them here, the browser test sees predictable data without
    # any real network calls.
    frontend_api.get_root_status = lambda: root_status
    frontend_api.get_health = lambda: health_status
    frontend_api.get_readiness = lambda: readiness_status
    frontend_api.get_system_status = lambda: system_status

    def fake_list_incidents() -> list[dict[str, Any]]:
        # Raise the same broad exception family used by real request failures so
        # the app's error handling path is exercised honestly.
        if list_error:
            raise requests.RequestException(str(list_error))
        return list(incidents)

    def fake_create_incident(payload_data: dict[str, Any]) -> dict[str, Any]:
        # This fake mirrors the shape of the real API enough for the success
        # message in the Streamlit page to render correctly.
        if create_error:
            raise requests.RequestException(str(create_error))
        return {
            "id": created_incident.get("id", 99),
            "affected_service": payload_data.get("affected_service", created_incident.get("affected_service", "backend")),
            "title": payload_data.get("title", "Untitled incident"),
            "severity": payload_data.get("severity", "sev-3"),
            "status": payload_data.get("status", "open"),
        }

    frontend_api.list_incidents = fake_list_incidents
    frontend_api.create_incident = fake_create_incident


# Apply patches before importing the Streamlit app.
#
# This ordering is important: if the app imports first, it could execute with
# the real backend functions before our fake ones are installed.
_patch_frontend_api(_load_payload())

# Importing the app module starts normal Streamlit page setup and rendering.
import frontend.app  # noqa: F401  # pylint: disable=unused-import