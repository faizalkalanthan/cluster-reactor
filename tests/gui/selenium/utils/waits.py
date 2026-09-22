from __future__ import annotations

import time


def wait_for_condition(predicate, timeout_seconds: float = 10.0, poll_interval: float = 0.2) -> None:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if predicate():
            return
        time.sleep(poll_interval)
    raise TimeoutError("Condition was not met in time")