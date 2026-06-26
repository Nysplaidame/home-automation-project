from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


DEFAULT_BLOCKED_PATHS = (
    "/",
    "/boot",
    "/etc",
    "/var",
    "/usr",
    "/run",
    "/proc",
    "/sys",
)


@dataclass(frozen=True)
class AppConfig:
    bind_host: str = "192.168.10.147"
    bind_port: int = 8088
    database_path: Path = Path("/var/lib/transferportal/jobs.sqlite")
    log_dir: Path = Path("/var/log/transferportal")
    helper_path: Path = Path("/usr/local/lib/transferportal/root-helper")
    portal_base: Path = Path("/srv/transferportal")
    allowed_mount_prefixes: tuple[Path, ...] = (Path("/srv"), Path("/mnt"))
    blocked_paths: tuple[Path, ...] = tuple(Path(p) for p in DEFAULT_BLOCKED_PATHS)
    max_active_jobs: int = 1
    session_secret_file: Path = Path("/etc/transferportal/session.secret")


def _paths(values: list[str] | tuple[str, ...] | None, fallback: tuple[Path, ...]) -> tuple[Path, ...]:
    if not values:
        return fallback
    return tuple(Path(value) for value in values)


def load_config(path: str | Path = "/etc/transferportal/config.yaml") -> AppConfig:
    config_path = Path(path)
    if not config_path.exists():
        return AppConfig()

    raw = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"{config_path} must contain a mapping")

    values: dict[str, Any] = {}
    for key in (
        "bind_host",
        "bind_port",
        "database_path",
        "log_dir",
        "helper_path",
        "portal_base",
        "max_active_jobs",
        "session_secret_file",
    ):
        if key in raw:
            values[key] = raw[key]

    for key in ("database_path", "log_dir", "helper_path", "portal_base", "session_secret_file"):
        if key in values:
            values[key] = Path(values[key])

    values["allowed_mount_prefixes"] = _paths(
        raw.get("allowed_mount_prefixes"),
        AppConfig().allowed_mount_prefixes,
    )
    values["blocked_paths"] = _paths(raw.get("blocked_paths"), AppConfig().blocked_paths)
    return AppConfig(**values)

