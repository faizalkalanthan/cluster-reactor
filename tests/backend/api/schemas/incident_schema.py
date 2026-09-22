from __future__ import annotations


def build_incident_payload(
    title: str = "Database latency spike",
    description: str = "Synthetic incident for API automation.",
    severity: str = "sev-2",
    status: str = "open",
    affected_service: str = "postgresql",
) -> dict:
    return {
        "title": title,
        "description": description,
        "severity": severity,
        "status": status,
        "affected_service": affected_service,
    }