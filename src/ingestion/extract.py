import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "json"


def extract_json(filename: str) -> Any:
    """Extrait les données brutes d'un fichier JSON depuis data/json."""
    path = DATA_DIR / filename
    with path.open(encoding="utf-8") as f:
        return json.load(f)
