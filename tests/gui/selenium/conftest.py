from collections.abc import Generator
from pathlib import Path
import os
import socket
import subprocess
import sys
import time

import pytest


pytest.importorskip("selenium")


REPO_ROOT = Path(__file__).resolve().parents[3]
LAUNCHER_FILE = Path(__file__).resolve().parent / "utils" / "streamlit_launcher.py"


def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


def _wait_for_streamlit(base_url: str, timeout_seconds: float = 25.0) -> None:
    import requests

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


@pytest.fixture()
def streamlit_app_factory(tmp_path: Path) -> Generator:
    processes: list[subprocess.Popen[str]] = []

    def _start() -> str:
        port = _find_free_port()
        env = os.environ.copy()
        env["PYTHONPATH"] = str(REPO_ROOT)
        process = subprocess.Popen(
            [
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

    for process in processes:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


@pytest.fixture()
def selenium_remote_url() -> str:
    remote_url = os.getenv("SELENIUM_REMOTE_URL")
    if not remote_url:
        pytest.skip("Set SELENIUM_REMOTE_URL to run Selenium GUI tests.")
    return remote_url