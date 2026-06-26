from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import JobStatus


SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portal_slug TEXT NOT NULL,
    mode TEXT NOT NULL,
    status TEXT NOT NULL,
    options_json TEXT NOT NULL,
    command_json TEXT NOT NULL,
    current_phase TEXT NOT NULL,
    exit_code INTEGER,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at TEXT,
    ended_at TEXT,
    log_path TEXT,
    status_path TEXT,
    pid INTEGER,
    error TEXT
);

CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actor TEXT NOT NULL,
    action TEXT NOT NULL,
    portal_slug TEXT,
    job_id INTEGER,
    detail_json TEXT NOT NULL
);
"""


class JobStore:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self.connect() as conn:
            conn.executescript(SCHEMA)
            columns = {row["name"] for row in conn.execute("PRAGMA table_info(jobs)")}
            if "pid" not in columns:
                conn.execute("ALTER TABLE jobs ADD COLUMN pid INTEGER")
            if "status_path" not in columns:
                conn.execute("ALTER TABLE jobs ADD COLUMN status_path TEXT")

    def active_count(self) -> int:
        return self.active_count_for_portal()

    def active_count_for_portal(self, portal_slug: str | None = None) -> int:
        active = (
            JobStatus.QUEUED.value,
            JobStatus.RUNNING.value,
            JobStatus.VERIFYING.value,
            JobStatus.WAITING_FOR_DELETE_CONFIRMATION.value,
            JobStatus.DELETING_SOURCE.value,
        )
        placeholders = ",".join("?" for _ in active)
        params: tuple[Any, ...]
        where = f"status IN ({placeholders})"
        params = active
        if portal_slug is not None:
            where = f"{where} AND portal_slug = ?"
            params = (*active, portal_slug)
        with self.connect() as conn:
            row = conn.execute(f"SELECT COUNT(*) AS count FROM jobs WHERE {where}", params).fetchone()
        return int(row["count"])

    def create_job(
        self,
        portal_slug: str,
        mode: str,
        status: str,
        options: dict[str, Any],
        command: tuple[str, ...],
        current_phase: str,
        log_path: Path | None,
        status_path: Path | None = None,
    ) -> int:
        with self.connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO jobs (portal_slug, mode, status, options_json, command_json, current_phase, log_path, status_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    portal_slug,
                    mode,
                    status,
                    json.dumps(options, sort_keys=True),
                    json.dumps(list(command)),
                    current_phase,
                    str(log_path) if log_path else None,
                    str(status_path) if status_path else None,
                ),
            )
            return int(cur.lastrowid)

    def list_jobs(self) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return list(conn.execute("SELECT * FROM jobs ORDER BY id DESC LIMIT 100"))

    def get_job(self, job_id: int) -> sqlite3.Row | None:
        with self.connect() as conn:
            return conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()

    def mark_launched(self, job_id: int, pid: int) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE jobs SET status = ?, current_phase = ?, started_at = CURRENT_TIMESTAMP, pid = ? WHERE id = ?",
                (JobStatus.RUNNING.value, "rsync", pid, job_id),
            )

    def list_active_jobs(self) -> list[sqlite3.Row]:
        active = (
            JobStatus.QUEUED.value,
            JobStatus.RUNNING.value,
            JobStatus.VERIFYING.value,
            JobStatus.WAITING_FOR_DELETE_CONFIRMATION.value,
            JobStatus.DELETING_SOURCE.value,
        )
        placeholders = ",".join("?" for _ in active)
        with self.connect() as conn:
            return list(conn.execute(f"SELECT * FROM jobs WHERE status IN ({placeholders})", active))

    def mark_completed(self, job_id: int, exit_code: int = 0) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE jobs SET status = ?, current_phase = ?, exit_code = ?, ended_at = CURRENT_TIMESTAMP WHERE id = ?",
                (JobStatus.COMPLETED.value, "completed", exit_code, job_id),
            )

    def mark_interrupted(self, job_id: int, exit_code: int = -15) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE jobs SET status = ?, current_phase = ?, ended_at = CURRENT_TIMESTAMP, exit_code = ? WHERE id = ?",
                (JobStatus.INTERRUPTED.value, "interrupted", exit_code, job_id),
            )

    def mark_failed(self, job_id: int, error: str, exit_code: int | None = None) -> None:
        with self.connect() as conn:
            conn.execute(
                "UPDATE jobs SET status = ?, current_phase = ?, ended_at = CURRENT_TIMESTAMP, error = ?, exit_code = ? WHERE id = ?",
                (JobStatus.FAILED.value, "failed", error, exit_code, job_id),
            )

    def record_audit(
        self,
        actor: str,
        action: str,
        portal_slug: str | None = None,
        job_id: int | None = None,
        detail: dict[str, Any] | None = None,
    ) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO audit_log (actor, action, portal_slug, job_id, detail_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (actor, action, portal_slug, job_id, json.dumps(detail or {}, sort_keys=True)),
            )
