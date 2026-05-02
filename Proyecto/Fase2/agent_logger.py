from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
LOG_FILE = LOGS_DIR / "agent_actions.jsonl"


def log_agent_action(payload: dict[str, Any]) -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    safe_payload = {
        "timestamp": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        **payload,
    }
    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(safe_payload, ensure_ascii=False) + "\n")
