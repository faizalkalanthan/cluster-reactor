from __future__ import annotations

import json
from pathlib import Path


def load_json_file(file_path: Path) -> dict:
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)