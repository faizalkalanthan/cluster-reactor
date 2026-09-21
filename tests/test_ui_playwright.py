from __future__ import annotations

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from collections.abc import Generator

import pytest
import requests
from playwright.sync_api import Page
from playwright.sync_api import expect


# This test file uses Python Playwright together with pytest.
#
# Beginner mental model:
# - `page` is a real browser tab provided by Playwright.
# - each test starts a tiny Streamlit server on a free port.
# - Playwright opens that page and interacts with it like a user would.
# - `expect(...)` is Playwright's built-in assertion style for waiting on UI.

LAUNCHER_FILE = Path(__file__).resolve().parent / "playwright_streamlit_launcher.py"


def _find_free_port() -> int:
    # Ask the OS for any available local port.
    # This avoids hard-coding one port and makes repeated test runs safer.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


def _wait_for_streamlit(base_url: str, timeout_seconds: float = 25.0) -> None:
    # Streamlit needs a moment to boot.
    # Rather than sleeping a fixed number of seconds, we poll the built-in
    # health endpoint until the app is truly ready.
    deadline = time.time() + timeout_seconds
    health_url = f"{base_url}/_stcore/health"
    while time.time() < deadline:
        try:
            response = requests.get(health_url, timeout=1)
            if response.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(0.3)
    raise RuntimeError(f"Streamlit app did not become ready: {health_url}")


@pytest.fixture
def streamlit_app_factory(tmp_path: Path) -> Generator:
    # A pytest fixture is reusable setup code.
    #
    # This fixture returns a function instead of a single value. That pattern is
    # often called a "factory fixture" and is common in interviews because it
    # allows each test to create slightly different test data on demand.
    processes: list[subprocess.Popen[str]] = []

    def _start(payload: dict[str, object] | None = None) -> str:
        # Each test instance gets its own Streamlit process and its own port.
        # That keeps tests isolated from one another.
        port = _find_free_port()
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1])
        env["CR_PLAYWRIGHT_PAYLOAD"] = json.dumps(payload or {})
        process = subprocess.Popen(
            [
                # Use the currently active Python interpreter so the subprocess
                # uses the same virtual environment as pytest.
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(LAUNCHER_FILE),
                "--server.headless",
                "true",
                "--server.port",
                str(port),
                "--browser.gatherUsageStats",
                "false",
            ],
            stdout=(tmp_path / f"streamlit-{port}.stdout.log").open("w", encoding="utf-8"),
            stderr=subprocess.STDOUT,
            text=True,
            env=env,
        )
        processes.append(process)
        base_url = f"http://127.0.0.1:{port}"
        _wait_for_streamlit(base_url)
        return base_url

    yield _start

    # Fixture teardown: always clean up child processes.
    # This is the pytest equivalent of reliable setup/teardown hygiene.
    for process in processes:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def _open_dashboard(page: Page, base_url: str) -> None:
    # Small helper functions like this are useful in Playwright suites because
    # they remove repeated navigation/wait boilerplate from each test.
    page.goto(base_url)
    expect(page.get_by_text("Cluster Reactor").first).to_be_visible()


@pytest.mark.ui
@pytest.mark.e2e
def test_dashboard_happy_path_renders_summary_cards(page: Page, streamlit_app_factory) -> None:
    # Happy path = everything is healthy and the page should render its core UI.
    base_url = streamlit_app_factory()
    _open_dashboard(page, base_url)

    # `expect(...)` waits until the UI matches the condition or times out.
    # This is better than raw `assert` for browser state because the DOM updates
    # asynchronously.
    expect(page.get_by_text("Recent incidents")).to_be_visible()
    expect(page.get_by_text("cluster-reactor-api")).to_be_visible()
    expect(page.get_by_text("1.0.0")).to_be_visible()
    expect(page.get_by_text("OK")).to_be_visible()
    expect(page.get_by_text("2").first).to_be_visible()
    expect(page.get_by_text("API latency spike")).to_be_visible()


@pytest.mark.ui
@pytest.mark.e2e
@pytest.mark.parametrize(
    ("payload", "expected_text"),
    [
        pytest.param({}, "Backend and PostgreSQL are ready to serve incident workflows.", id="ready-state"),
        pytest.param(
            {"readiness_status": {"status": "not_ready", "checks": {"database": "unavailable"}, "details": {"database": "connection refused"}}},
            "Backend is alive but not fully ready.",
            id="not-ready-state",
        ),
    ],
)
def test_dashboard_banner_covers_readiness_variants(page: Page, streamlit_app_factory, payload: dict[str, object], expected_text: str) -> None:
    # Parametrization lets one test body cover multiple scenarios cleanly.
    # This is one of the most common pytest interview topics.
    base_url = streamlit_app_factory(payload)
    _open_dashboard(page, base_url)

    expect(page.get_by_text(expected_text)).to_be_visible()


@pytest.mark.ui
@pytest.mark.e2e
def test_dashboard_handles_fetch_failures_gracefully(page: Page, streamlit_app_factory) -> None:
    # Negative-path test: verify the UI degrades gracefully when the backend
    # call fails instead of crashing silently.
    base_url = streamlit_app_factory({"list_error": "backend unavailable", "incidents": []})
    _open_dashboard(page, base_url)

    expect(page.get_by_text("backend unavailable")).to_be_visible()
    expect(page.get_by_text("No incidents recorded yet")).to_be_visible()


@pytest.mark.ui
@pytest.mark.e2e
@pytest.mark.parametrize(
    ("page_name", "headline"),
    [
        pytest.param("Incident Console", "Current incidents", id="incident-console"),
        pytest.param("Service Health", "Health payloads", id="service-health"),
    ],
)
def test_sidebar_navigation_switches_views(page: Page, streamlit_app_factory, page_name: str, headline: str) -> None:
    base_url = streamlit_app_factory()
    _open_dashboard(page, base_url)

    # Playwright locators describe elements the way a user would perceive them:
    # by label text, button name, visible text, etc. That tends to produce more
    # maintainable tests than brittle CSS selectors.
    page.get_by_label("Navigate").select_option(label=page_name)
    expect(page.get_by_text(headline)).to_be_visible()


@pytest.mark.ui
@pytest.mark.e2e
def test_incident_console_validates_short_title(page: Page, streamlit_app_factory) -> None:
    # Form-validation test: we intentionally submit bad input and assert the
    # validation error the user should see.
    base_url = streamlit_app_factory({"incidents": []})
    _open_dashboard(page, base_url)

    page.get_by_label("Navigate").select_option(label="Incident Console")
    page.get_by_label("Title").fill("DB")
    page.get_by_label("Description").fill("Transient database issue")
    page.get_by_role("button", name="Create incident").click()

    expect(page.get_by_text("Incident title must be at least 3 characters long.")).to_be_visible()


@pytest.mark.ui
@pytest.mark.e2e
def test_incident_console_submits_form_successfully(page: Page, streamlit_app_factory) -> None:
    # This covers a complete user flow:
    # navigate -> fill form -> submit -> assert success feedback.
    base_url = streamlit_app_factory({"incidents": []})
    _open_dashboard(page, base_url)

    page.get_by_label("Navigate").select_option(label="Incident Console")
    page.get_by_label("Title").fill("Database latency spike")
    page.get_by_label("Description").fill("Investigate connection pool saturation")
    page.get_by_label("Severity").select_option(label="sev-1")
    page.get_by_label("Status").select_option(label="acknowledged")
    page.get_by_label("Affected service").select_option(label="postgresql")
    page.get_by_role("button", name="Create incident").click()

    expect(page.get_by_text("Incident #99 created for postgresql.")).to_be_visible()


@pytest.mark.ui
@pytest.mark.e2e
def test_incident_console_surfaces_backend_errors(page: Page, streamlit_app_factory) -> None:
    # Another negative-path test: the request is accepted by the form, but the
    # backend operation fails and the user should get a clear error message.
    base_url = streamlit_app_factory({"incidents": [], "create_error": "timeout"})
    _open_dashboard(page, base_url)

    page.get_by_label("Navigate").select_option(label="Incident Console")
    page.get_by_label("Title").fill("Backend timeout")
    page.get_by_role("button", name="Create incident").click()

    expect(page.get_by_text("Failed to create incident: timeout")).to_be_visible()


@pytest.mark.ui
@pytest.mark.e2e
def test_service_health_page_renders_runtime_context(page: Page, streamlit_app_factory) -> None:
    # This test checks a second page to prove the navigation and runtime context
    # cards render correctly under a different dataset.
    base_url = streamlit_app_factory(
        {
            "health_status": {"status": "ok"},
            "readiness_status": {"status": "ready", "checks": {"database": "available"}},
            "system_status": {"service": "cluster-reactor-api", "environment": "staging", "version": "2.1.0"},
        }
    )
    _open_dashboard(page, base_url)

    page.get_by_label("Navigate").select_option(label="Service Health")

    expect(page.get_by_text("Service Health")).to_be_visible()
    expect(page.get_by_text("Liveness")).to_be_visible()
    expect(page.get_by_text("Readiness")).to_be_visible()
    expect(page.get_by_text("Environment")).to_be_visible()
    expect(page.get_by_text("STAGING")).to_be_visible()
