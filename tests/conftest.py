from pathlib import Path
import sys


ROOT_PATH = Path(__file__).resolve().parents[1]
BACKEND_PATH = ROOT_PATH / "backend"

for path in (ROOT_PATH, BACKEND_PATH):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))