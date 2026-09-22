from __future__ import annotations


NEW_INCIDENT_PAYLOAD = {
    "title": "Database latency spike",
    "description": "Synthetic incident for API coverage.",
    "severity": "sev-2",
    "status": "open",
    "affected_service": "postgresql",
}


RECENT_INCIDENTS = [
    {
        "title": "Older incident",
        "severity": "sev-3",
        "status": "open",
        "affected_service": "backend",
    },
    {
        "title": "Newer incident",
        "severity": "sev-1",
        "status": "acknowledged",
        "affected_service": "database",
    },
]