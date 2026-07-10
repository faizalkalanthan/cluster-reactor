from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import sys

import requests
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from frontend.api import BACKEND_BASE_URL
from frontend.api import create_incident
from frontend.api import get_health
from frontend.api import get_readiness
from frontend.api import get_root_status
from frontend.api import get_system_status
from frontend.api import list_incidents
from frontend.ui import inject_global_styles
from frontend.ui import render_incidents_table
from frontend.ui import render_metric_card
from frontend.ui import render_page_header
from frontend.ui import render_severity_legend
from frontend.ui import render_status_banner


st.set_page_config(
    page_title="Cluster Reactor",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_global_styles()


def safe_call(callable_obj, fallback):
    try:
        return callable_obj()
    except requests.RequestException as exc:
        st.session_state["cluster_reactor_last_error"] = str(exc)
        return fallback


def load_dashboard_state() -> tuple[dict[str, object], dict[str, object], dict[str, object], list[dict[str, object]]]:
    root_status = safe_call(get_root_status, {"service": "unavailable", "status": "down", "version": "n/a"})
    health_status = safe_call(get_health, {"status": "down"})
    readiness_status = safe_call(
        get_readiness,
        {"status": "not_ready", "checks": {"database": "unavailable"}, "details": {}},
    )
    incidents = safe_call(list_incidents, [])
    return root_status, health_status, readiness_status, incidents


def render_dashboard() -> None:
    root_status, health_status, readiness_status, incidents = load_dashboard_state()
    render_page_header(
        "Cluster Reactor",
        "An internal reliability operations console for health, incidents, and dependency-aware troubleshooting.",
    )

    is_ready = readiness_status.get("status") == "ready"
    banner_message = (
        "Backend and PostgreSQL are ready to serve incident workflows."
        if is_ready
        else f"Backend is alive but not fully ready. Details: {readiness_status.get('details', {})}"
    )
    render_status_banner(is_ready, banner_message)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Service", str(root_status.get("service", "unknown")))
    with col2:
        render_metric_card("Version", str(root_status.get("version", "n/a")))
    with col3:
        render_metric_card("Health", str(health_status.get("status", "unknown")).upper())
    with col4:
        render_metric_card("Active Incidents", str(len(incidents)))

    left, right = st.columns([1.5, 1])
    with left:
        st.subheader("Recent incidents")
        render_severity_legend()
        render_incidents_table(incidents)
    with right:
        st.subheader("Runtime context")
        system_status = safe_call(get_system_status, {"environment": "unknown"})
        st.json(
            {
                "api_base_url": BACKEND_BASE_URL,
                "environment": system_status.get("environment", "unknown"),
                "readiness": readiness_status,
            }
        )


def render_incident_console() -> None:
    render_page_header(
        "Incident Console",
        "Create synthetic operational events and inspect the current incident timeline.",
    )

    with st.form("create-incident-form"):
        title = st.text_input("Title", placeholder="Database latency spike")
        description = st.text_area("Description", placeholder="What failed, why it matters, and what operators should investigate.")
        col1, col2, col3 = st.columns(3)
        with col1:
            severity = st.selectbox("Severity", ["sev-1", "sev-2", "sev-3", "sev-4"], index=2)
        with col2:
            status = st.selectbox("Status", ["open", "acknowledged", "resolved"], index=0)
        with col3:
            affected_service = st.selectbox("Affected service", ["backend", "postgresql", "frontend", "monitoring"], index=0)
        submitted = st.form_submit_button("Create incident", use_container_width=True)

    if submitted:
        if len(title.strip()) < 3:
            st.error("Incident title must be at least 3 characters long.")
        else:
            try:
                created = create_incident(
                    {
                        "title": title.strip(),
                        "description": description.strip() or None,
                        "severity": severity,
                        "status": status,
                        "affected_service": affected_service,
                    }
                )
                st.success(f"Incident #{created['id']} created for {created['affected_service']}.")
            except requests.RequestException as exc:
                st.error(f"Failed to create incident: {exc}")

    st.subheader("Current incidents")
    incidents = safe_call(list_incidents, [])
    render_incidents_table(incidents)


def render_service_health() -> None:
    render_page_header(
        "Service Health",
        "Inspect liveness, readiness, and backend environment signals the same way an operator would.",
    )
    health_status = safe_call(get_health, {"status": "down"})
    readiness_status = safe_call(get_readiness, {"status": "not_ready", "checks": {"database": "unavailable"}})
    system_status = safe_call(get_system_status, {"service": "unknown", "environment": "unknown", "version": "n/a"})

    col1, col2, col3 = st.columns(3)
    with col1:
        render_metric_card("Liveness", str(health_status.get("status", "unknown")).upper())
    with col2:
        render_metric_card("Readiness", str(readiness_status.get("status", "unknown")).upper())
    with col3:
        render_metric_card("Environment", str(system_status.get("environment", "unknown")).upper())

    st.subheader("Health payloads")
    left, right = st.columns(2)
    with left:
        st.json({"healthz": health_status, "readyz": readiness_status})
    with right:
        st.json(system_status)


with st.sidebar:
    st.markdown("## ⚛️ Cluster Reactor")
    st.caption("Kubernetes-first reliability learning console")
    page = st.radio(
        "Navigate",
        ["Dashboard", "Incident Console", "Service Health"],
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.caption(f"API target: {BACKEND_BASE_URL}")
    if "cluster_reactor_last_error" in st.session_state:
        st.warning(st.session_state["cluster_reactor_last_error"])


if page == "Dashboard":
    render_dashboard()
elif page == "Incident Console":
    render_incident_console()
else:
    render_service_health()