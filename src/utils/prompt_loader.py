import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"

def load_prompt(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text(encoding="utf-8")

def load_schema(filename: str) -> dict:
    with open(PROMPTS_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)