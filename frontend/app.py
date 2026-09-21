from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
import sys

import requests
import streamlit as st

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from frontend.api import BACKEND_BASE_URL
from frontend.api import create_incident
from frontend.api import create_tenant
from frontend.api import delete_tenant
from frontend.api import get_health
from frontend.api import get_readiness
from frontend.api import get_root_status
from frontend.api import get_system_status
from frontend.api import list_incidents
from frontend.api import list_tenants
from frontend.api import login
from frontend.ui import inject_global_styles
from frontend.ui import render_incidents_table
from frontend.ui import render_metric_card
from frontend.ui import render_page_header
from frontend.ui import render_severity_legend
from frontend.ui import render_status_banner


ROLE_PERMISSIONS = {
    "admin": ["Read incidents", "Write incidents", "Manage tenants", "Manage users"],
    "writer": ["Read incidents", "Write incidents"],
    "reader": ["Read incidents"],
}


st.set_page_config(
    page_title="Cluster Reactor",
    page_icon="⚛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Remove top padding and spacing
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 0rem !important;
            gap: 0rem !important;
        }
        [data-testid="stVerticalBlock"] {
            gap: 0rem !important;
        }
    </style>
""", unsafe_allow_html=True)

inject_global_styles()


def resolve_user_role(email: str) -> str:
    normalized = email.lower()
    if "admin" in normalized:
        return "admin"
    if "writer" in normalized:
        return "writer"
    return "reader"


def safe_call(callable_obj, fallback):
    try:
        return callable_obj()
    except requests.RequestException as exc:
        st.session_state["cluster_reactor_last_error"] = str(exc)
        return fallback


def render_role_summary() -> None:
    role = st.session_state.get("user_role", "reader")
    permissions = ROLE_PERMISSIONS.get(role, ROLE_PERMISSIONS["reader"])
    st.markdown(
        f"""
        <div style="margin-top: 0.5rem; margin-bottom: 0.75rem; padding: 0.9rem 1rem; border: 1px solid rgba(103, 232, 249, 0.18); border-radius: 14px; background: rgba(15,23,42,0.9);">
            <div style="font-size: 0.68rem; letter-spacing: 0.15em; text-transform: uppercase; color: #67e8f9;">Session</div>
            <div style="display:flex; align-items:center; justify-content:space-between; margin-top: 0.45rem;">
                <div>
                    <div style="font-size: 1.08rem; font-weight: 700; color: #f8fafc;">{role.title()}</div>
                    <div style="font-size: 0.75rem; color: #94a3b8;">{st.session_state.get('tenant_slug', 'clusterreactor')}</div>
                </div>
                <span style="display:inline-flex; align-items:center; gap:0.35rem; border-radius:999px; padding:0.38rem 0.7rem; font-size:0.68rem; letter-spacing:0.12em; background: rgba(34,211,238,0.12); color: #a5f3fc; border: 1px solid rgba(34,211,238,0.2); text-transform: uppercase;">{role}</span>
            </div>
            <div style="margin-top: 0.8rem; display:flex; flex-wrap:wrap; gap:0.45rem;">
                {''.join(f'<span style="display:inline-flex; padding:0.3rem 0.6rem; border-radius:999px; background: rgba(148,163,184,0.08); color: #e2e8f0; font-size: 0.7rem; border:1px solid rgba(148,163,184,0.12);">{p}</span>' for p in permissions)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def normalize_login_username(raw_username: str) -> str:
    username = (raw_username or "").strip().lower()
    if not username:
        return ""
    if "@" in username:
        username = username.split("@", 1)[0]
    return username


def load_dashboard_state() -> tuple[Mapping[str, object], Mapping[str, object], Mapping[str, object], Sequence[Mapping[str, object]]]:
    root_status = safe_call(get_root_status, {"service": "unavailable", "status": "down", "version": "n/a"})
    health_status = safe_call(get_health, {"status": "down"})
    readiness_status = safe_call(
        get_readiness,
        {"status": "not_ready", "checks": {"database": "unavailable"}, "details": {}},
    )
    incidents = safe_call(list_incidents, [])
    return root_status, health_status, readiness_status, incidents


def render_login_page() -> None:
    st.markdown(
        """
        <style>
            html, body, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"], section.main, section.main > div.block-container {
                margin: 0 !important;
                padding: 0 !important;
                min-height: 100vh !important;
                width: 100vw !important;
                overflow: hidden !important;
                background: #020817 !important;
            }
            [data-testid="stVerticalBlock"] {
                gap: 0 !important;
                padding: 0 !important;
            }
            header, [data-testid="stToolbar"], [data-testid="stDecoration"], #MainMenu {
                display: none !important;
            }
            .stApp {
                background: #020817 !important;
            }
            .login-shell {
                position: fixed;
                inset: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 0;
                margin: 0;
                background: radial-gradient(circle at top, rgba(14,165,233,0.16), transparent 32%), #020817;
            }
            .login-card {
                width: min(100%, 460px);
                background: rgba(15, 23, 42, 0.9);
                border: 1px solid rgba(148,163,184,0.2);
                border-radius: 24px;
                margin: 0;
                box-shadow: 0 18px 42px rgba(8, 47, 73, 0.35);
                overflow: hidden;
            }
            div[data-testid="stForm"] {
                max-width: 360px;
                margin: 0 auto;
            }
            div[data-testid="stForm"] > form {
                padding-top: 0.1rem;
            }
            div[data-testid="stTextInput"],
            div[data-testid="stPassword"] {
                max-width: 360px;
                margin: 0 auto 0.25rem;
            }
            div[data-testid="stTextInput"] input,
            div[data-testid="stPassword"] input {
                max-width: 360px;
            }
            div[data-testid="stCheckbox"] {
                margin: 0.45rem 0 0.2rem;
            }
            div[data-testid="stFormSubmitButton"] {
                margin-top: 0.85rem;
            }
            div[data-testid="stFormSubmitButton"] button {
                width: 100%;
            }
            .tenant-brand {
                width: 52px;
                height: 52px;
                margin: 0.55cm auto 1.1rem;
                border-radius: 16px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: linear-gradient(135deg, rgba(34,211,238,0.22), rgba(59,130,246,0.28));
                color: #67e8f9;
                font-size: 1.5rem;
                font-weight: 800;
            }
            .login-title {
                text-align: center;
                margin: 0 0 0.85rem;
                color: #f8fafc;
                font-size: 2rem;
                line-height: 1.05;
                font-weight: 750;
            }
            .login-subtitle {
                text-align: center;
                color: #94a3b8;
                margin: 0 0 1.55rem;
                font-size: 0.90rem;
            }
            .login-hint {
                margin-top: 17rem;
                padding: 0.55rem 0.9rem;
                border-radius: 10px;
                border: 1px solid rgba(148,163,184,0.14);
                background: rgba(15,23,42,0.7);
                color: #cbd5e1;
                font-size: 0.78rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="login-shell"><div class="login-card">', unsafe_allow_html=True)
    st.markdown('<div class="tenant-brand">CR</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-title">Cluster Reactor</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Login to your tenant workspace</div>', unsafe_allow_html=True)

    with st.form("tenant_login_form"):
        tenant_slug = "clusterreactor"
        raw_username = st.text_input("Username", placeholder="admin")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        remember = st.checkbox("Keep me signed in")
        submitted = st.form_submit_button("Sign in", use_container_width=True)

    if submitted:
        username = normalize_login_username(raw_username)
        if not username:
            st.error("Please enter a username.")
        else:
            try:
                email = f"{username}@clusterreactor.local"
                result = login(tenant_slug=tenant_slug, email=email, password=password)
                st.session_state["access_token"] = result["access_token"]
                st.session_state["tenant_slug"] = tenant_slug
                st.session_state["user_role"] = resolve_user_role(username)
                st.success("Login successful")
                st.rerun()
            except requests.HTTPError as exc:
                detail = ""
                try:
                    payload = exc.response.json()
                    if isinstance(payload, dict):
                        detail = payload.get("detail", "")
                except ValueError:
                    detail = ""
                if detail:
                    st.error(f"Login failed: {detail}")
                else:
                    st.error(f"Login failed: {exc}")
            except requests.RequestException as exc:
                st.error(f"Login failed: {exc}")

    st.markdown(
        """
        <div class="login-hint">
            Demo users: admin / writer / reader<br>
            Passwords: Admin123!, Writer123!, Reader123!
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div></div>", unsafe_allow_html=True)


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


def render_tenants_admin() -> None:
    render_page_header("Tenant Administration", "Create and manage tenant organizations with scoped access.")
    token = st.session_state.get("access_token")
    if not token:
        st.warning("Please log in first.")
        return

    tenants = safe_call(lambda: list_tenants(token), [])

    st.markdown(
        """
        <div style="margin: 1rem 0 1.5rem; padding: 0.9rem 1rem; border-radius: 16px; border: 1px solid rgba(103, 232, 249, 0.18); background: rgba(8, 47, 73, 0.16); color: #dbeafe;">
            <strong style="color: #67e8f9;">Access model</strong><br>
            Admins can manage tenants and users. Writers can create and update incidents. Readers can view incidents only.
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("tenant-create-form"):
        name = st.text_input("Tenant name")
        slug = st.text_input("Slug")
        domain = st.text_input("Domain (optional)")
        is_active = st.checkbox("Active", value=True)
        submitted = st.form_submit_button("Create tenant", use_container_width=True)

    if submitted and name.strip() and slug.strip():
        try:
            create_tenant(
                token,
                {"name": name.strip(), "slug": slug.strip(), "domain": domain.strip() or None, "is_active": is_active},
            )
            st.success("Tenant created")
            st.rerun()
        except requests.RequestException as exc:
            st.error(f"Failed to create tenant: {exc}")

    if tenants:
        st.subheader("Existing tenants")
        for tenant in tenants:
            status_label = "Active" if tenant.get("is_active") else "Inactive"
            with st.container():
                st.markdown(
                    f"""
                    <div style="margin-top: 0.8rem; padding: 1rem 1.1rem; border-radius: 16px; background: rgba(15,23,42,0.9); border: 1px solid rgba(148,163,184,0.15);">
                        <div style="display:flex; align-items:center; justify-content:space-between; gap: 1rem; flex-wrap:wrap;">
                            <div>
                                <div style="font-size: 1.06rem; font-weight:700; color: #f8fafc;">{tenant.get('name')}</div>
                                <div style="font-size: 0.76rem; color: #94a3b8;">{tenant.get('slug')} • {tenant.get('domain') or 'no domain'}</div>
                            </div>
                            <span style="display:inline-flex; padding:0.32rem 0.7rem; border-radius:999px; font-size:0.7rem; text-transform: uppercase; letter-spacing:0.08em; background: rgba(34,197,94,0.14); color:#bbf7d0; border: 1px solid rgba(34,197,94,0.25);">{status_label}</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                col_a, col_b = st.columns([3, 1])
                with col_a:
                    st.caption("Permissions: Admin • Writer • Reader")
                with col_b:
                    if st.button("Delete", key=f"delete-tenant-{tenant['id']}"):
                        try:
                            delete_tenant(token, int(tenant["id"]))
                            st.success("Tenant deleted")
                            st.rerun()
                        except requests.RequestException as exc:
                            st.error(f"Could not delete tenant: {exc}")


def render_user_management() -> None:
    render_page_header("User Management", "Assign roles and control tenant memberships for each user.")
    role = st.session_state.get("user_role", "reader")
    if role != "admin":
        st.warning("Only administrators can manage users.")
        return

    st.markdown(
        """
        <div style="margin: 1rem 0 1.5rem; padding: 0.9rem 1rem; border-radius: 16px; border: 1px solid rgba(103, 232, 249, 0.18); background: rgba(8, 47, 73, 0.16); color: #dbeafe;">
            <strong style="color: #67e8f9;">Role controls</strong><br>
            Admins can manage tenants and users. Writers can create and update incidents. Readers can only view incidents.
        </div>
        """,
        unsafe_allow_html=True,
    )

    users = [
        {"name": "Cluster Reactor Admin", "email": "admin@clusterreactor.local", "role": "admin"},
        {"name": "Cluster Reactor Writer", "email": "writer@clusterreactor.local", "role": "writer"},
        {"name": "Cluster Reactor Reader", "email": "reader@clusterreactor.local", "role": "reader"},
    ]

    for user in users:
        col_a, col_b, col_c = st.columns([2, 2, 1.2])
        with col_a:
            st.write(f"**{user['name']}**")
            st.caption(user["email"])
        with col_b:
            st.selectbox(
                "Role",
                ["reader", "writer", "admin"],
                index=["reader", "writer", "admin"].index(user["role"]),
                key=f"role-select-{user['email']}",
                label_visibility="collapsed",
            )
        with col_c:
            st.button("Save", key=f"save-role-{user['email']}")


if "access_token" not in st.session_state:
    render_login_page()
else:
    with st.sidebar:
        st.markdown("## ⚛️ Cluster Reactor")
        render_role_summary()
        st.caption(f"Workspace: {st.session_state.get('tenant_slug', 'clusterreactor')}")
        page = st.radio(
            "Navigate",
            ["Dashboard", "Incident Console", "Service Health", "Tenant Administration", "User Management"],
            label_visibility="collapsed",
        )
        st.markdown("---")
        st.caption(f"API target: {BACKEND_BASE_URL}")
        if st.button("Log out"):
            st.session_state.pop("access_token", None)
            st.session_state.pop("tenant_slug", None)
            st.session_state.pop("user_role", None)
            st.rerun()
        if "cluster_reactor_last_error" in st.session_state:
            st.warning(st.session_state["cluster_reactor_last_error"])

    if page == "Dashboard":
        render_dashboard()
    elif page == "Incident Console":
        render_incident_console()
    elif page == "Tenant Administration":
        render_tenants_admin()
    elif page == "User Management":
        render_user_management()
    else:
        render_service_health()