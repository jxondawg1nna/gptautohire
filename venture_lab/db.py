"""SQLite persistence for runs, experiments, events and reviewable proposals."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Store:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        return con

    def _init_schema(self) -> None:
        with self.connect() as con:
            con.executescript("""
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    status TEXT NOT NULL,
                    summary TEXT NOT NULL DEFAULT ''
                );
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER,
                    created_at TEXT NOT NULL,
                    role TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    FOREIGN KEY(run_id) REFERENCES runs(id)
                );
                CREATE TABLE IF NOT EXISTS experiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    run_id INTEGER,
                    hypothesis TEXT NOT NULL,
                    metric TEXT NOT NULL DEFAULT '',
                    result TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'proposed',
                    FOREIGN KEY(run_id) REFERENCES runs(id)
                );
                CREATE TABLE IF NOT EXISTS proposals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    run_id INTEGER,
                    title TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    validation_plan TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending_review',
                    FOREIGN KEY(run_id) REFERENCES runs(id)
                );
            """)

    def create_run(self, goal: str) -> int:
        with self.connect() as con:
            cur = con.execute(
                "INSERT INTO runs(created_at, goal, status) VALUES (?, ?, ?)",
                (utc_now(), goal, "running"),
            )
            return int(cur.lastrowid)

    def finish_run(self, run_id: int, status: str, summary: str) -> None:
        with self.connect() as con:
            con.execute(
                "UPDATE runs SET status=?, summary=? WHERE id=?",
                (status, summary, run_id),
            )

    def event(self, run_id: int | None, role: str, event_type: str, content: Any) -> None:
        serialised = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
        with self.connect() as con:
            con.execute(
                "INSERT INTO events(run_id, created_at, role, event_type, content) VALUES (?, ?, ?, ?, ?)",
                (run_id, utc_now(), role, event_type, serialised),
            )

    def add_proposal(self, run_id: int, proposal: dict[str, str]) -> int:
        with self.connect() as con:
            cur = con.execute(
                """INSERT INTO proposals(created_at, run_id, title, rationale, change_type, validation_plan)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (utc_now(), run_id, proposal["title"], proposal["rationale"],
                 proposal["change_type"], proposal["validation_plan"]),
            )
            return int(cur.lastrowid)

    def runs(self, limit: int = 10) -> list[dict[str, Any]]:
        with self.connect() as con:
            rows = con.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
            return [dict(row) for row in rows]

    def proposals(self, limit: int = 20) -> list[dict[str, Any]]:
        with self.connect() as con:
            rows = con.execute("SELECT * FROM proposals ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
            return [dict(row) for row in rows]

    def count_runs_today(self) -> int:
        today = datetime.now(timezone.utc).date().isoformat()
        with self.connect() as con:
            row = con.execute(
                "SELECT COUNT(*) AS n FROM runs WHERE substr(created_at, 1, 10)=?",
                (today,),
            ).fetchone()
            return int(row["n"])
