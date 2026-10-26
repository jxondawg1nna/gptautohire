"""Configuration for the local-first Venture Lab."""
from __future__ import annotations

import os
from pathlib import Path


def load_dotenv(path: Path = Path(".env")) -> None:
    """Load a small .env file without requiring python-dotenv."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def get_config() -> dict[str, object]:
    load_dotenv()
    try:
        cycle_cap = max(1, int(os.getenv("MAX_CYCLES_PER_DAY", "5")))
        timeout = max(5, int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "180")))
    except ValueError as exc:
        raise ValueError("MAX_CYCLES_PER_DAY and OLLAMA_TIMEOUT_SECONDS must be integers") from exc

    allow_external = os.getenv("ALLOW_EXTERNAL_ACTIONS", "false").lower() == "true"
    if allow_external:
        raise ValueError(
            "External actions are not implemented in this scaffold; "
            "set ALLOW_EXTERNAL_ACTIONS=false."
        )
    return {
        "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/"),
        "ollama_model": os.getenv("OLLAMA_MODEL", "qwen3:8b"),
        "ollama_timeout_seconds": timeout,
        "db_path": Path(os.getenv("VENTURE_LAB_DB", "./data/venture_lab.sqlite3")),
        "max_cycles_per_day": cycle_cap,
        "allow_external_actions": False,
    }
