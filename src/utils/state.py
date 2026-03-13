
import json
from pathlib import Path

from models import State

RUNS_DIR = Path(__file__).resolve().parent.parent.parent / "runs"
RUNS_DIR.mkdir(exist_ok=True)

class StateStore:

    def write(self, state: State):
        path = RUNS_DIR / "latest_run.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, indent=2, ensure_ascii=False)