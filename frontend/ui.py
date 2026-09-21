from __future__ import annotations

from collections.abc import Mapping, Sequence

import pandas as pd
import streamlit as st


SEVERITY_COLORS = {
    "sev-1": "#f43f5e",
    "sev-2": "#fb923c",
    "sev-3": "#facc15",
    "sev-4": "#38bdf8",
}


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
            :root {
                --bg: #020817;
                --panel: rgba(15, 23, 42, 0.86);
                --panel-soft: rgba(15, 23, 42, 0.72);
                --border: rgba(148, 163, 184, 0.18);
                --text: #e2e8f0;
                --muted: #94a3b8;
                --accent: #67e8f9;
                --accent-strong: #22d3ee;
                --success: #34d399;
                --warning: #fbbf24;
            }
            html, body, [data-testid="stAppViewContainer"] {
                background: linear-gradient(180deg, #020817 0%, #0f172a 100%);
                color: var(--text);
            }
            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 2rem;
            }
            .stSidebar {
                background: linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(2, 6, 23, 0.96));
                border-right: 1px solid var(--border);
            }
            .cr-card {
                background: linear-gradient(180deg, rgba(30,41,59,0.94), rgba(15,23,42,0.96));
                border: 1px solid rgba(148, 163, 184, 0.16);
                border-radius: 18px;
                padding: 1rem 1.1rem;
                box-shadow: 0 12px 32px rgba(2, 6, 23, 0.25);
            }
            .cr-label {
                color: #94a3b8;
                font-size: 0.82rem;
                margin-bottom: 0.35rem;
                text-transform: uppercase;
                letter-spacing: 0.08em;
            }
            .cr-value {
                color: #f8fafc;
                font-size: 1.7rem;
                font-weight: 700;
            }
            .cr-banner {
                border-radius: 14px;
                padding: 0.85rem 1rem;
                border: 1px solid rgba(148, 163, 184, 0.18);
                margin-bottom: 1rem;
            }
            .cr-banner.ok {
                background: rgba(34, 197, 94, 0.12);
                color: #dcfce7;
            }
            .cr-banner.warn {
                background: rgba(251, 146, 60, 0.14);
                color: #ffedd5;
            }
            .cr-pill {
                display: inline-block;
                padding: 0.25rem 0.65rem;
                border-radius: 999px;
                font-size: 0.8rem;
                font-weight: 600;
                margin-right: 0.35rem;
            }
            .cr-role-tag {
                display: inline-flex;
                align-items: center;
                gap: 0.45rem;
                border-radius: 999px;
                padding: 0.42rem 0.7rem;
                font-size: 0.72rem;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                border: 1px solid rgba(103, 232, 249, 0.28);
                background: rgba(34, 211, 238, 0.12);
                color: #a5f3fc;
            }
            div[data-testid="stVerticalBlock"] > div:not([class*="st-" ]) {
                border: 0;
            }
            .stButton > button {
                border-radius: 12px;
                border: 1px solid rgba(103, 232, 249, 0.28);
                background: linear-gradient(135deg, #67e8f9 0%, #22d3ee 100%);
                color: #082f49;
                font-weight: 700;
                transition: all 0.2s ease;
            }
            .stButton > button:hover {
                filter: brightness(1.04);
                transform: translateY(-1px);
            }
            .stTextInput input, .stTextArea textarea, .stSelectbox div, .stNumberInput input {
                background: rgba(15, 23, 42, 0.9);
                color: #f8fafc;
                border: 1px solid rgba(148, 163, 184, 0.18);
                border-radius: 12px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div style="margin-bottom: 0.8rem;">
            <div style="font-size: 0.74rem; letter-spacing: 0.18em; text-transform: uppercase; color: #67e8f9; margin-bottom: 0.4rem;">Cluster Reactor</div>
            <h1 style="margin: 0; font-size: 2.2rem; line-height: 1.1;">{title}</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption(subtitle)


def render_metric_card(label: str, value: str, help_text: str | None = None) -> None:
    tooltip = f' title="{help_text}"' if help_text else ""
    st.markdown(
        f"""
        <div class="cr-card"{tooltip}>
            <div class="cr-label">{label}</div>
            <div class="cr-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_status_banner(is_healthy: bool, message: str) -> None:
    banner_class = "ok" if is_healthy else "warn"
    st.markdown(
        f'<div class="cr-banner {banner_class}">{message}</div>',
        unsafe_allow_html=True,
    )


def render_incidents_table(incidents: Sequence[Mapping[str, object]]) -> None:
    if not incidents:
        st.info("No incidents recorded yet. Create one from the form to start the operational timeline.")
        return

    frame = pd.DataFrame(list(incidents))
    if "created_at" in frame.columns:
        frame["created_at"] = pd.to_datetime(frame["created_at"]).dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    st.dataframe(frame, hide_index=True)


def render_severity_legend() -> None:
    pills = []
    for severity, color in SEVERITY_COLORS.items():
        pills.append(
            f'<span class="cr-pill" style="background:{color}22;color:{color};border:1px solid {color}55;">{severity.upper()}</span>'
        )
    st.markdown("".join(pills), unsafe_allow_html=True)