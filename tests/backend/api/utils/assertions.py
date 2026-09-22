from __future__ import annotations

from typing import Any


def assert_field(payload: dict[str, Any], field: str, expected: Any) -> None:
    assert payload[field] == expected