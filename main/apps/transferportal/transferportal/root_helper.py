from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

from .path_safety import MountInfo, PathValidationError, validate_data_path, validate_no_overlap
from .portals import validate_slug
from .settings import load_config

SYSTEMD_SYSTEM_DIR = Path(os.environ.get("TRANSFERPORTAL_SYSTEMD_DIR", "/etc/systemd/system"))


class HelperInputError(ValueError):
    """Raised for invalid helper input."""


def run(command: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=check)


def load_mounts() -> list[MountInfo]:
    result = run(["findmnt", "--json", "--output", "SOURCE,TARGET,FSTYPE,OPTIONS"], check=True)
    payload = json.loads(result.stdout)
    mounts: list[MountInfo] = []

    def walk(rows: list[dict[str, Any]]) -> None:
        for row in rows:
            target = row.get("target")
            if target:
                mounts.append(
                    MountInfo(
                        target=Path(target),
                        source=str(row.get("source", "")),
                        fstype=str(row.get("fstype", "")),
                        options=str(row.get("options", "")),
                    )
                )
            children = row.get("children") or []
            if children:
                walk(children)

    walk(payload.get("filesystems", []))
    return mounts


def action_list_mounts(params: dict[str, Any]) -> dict[str, Any]:
    _unused(params)
    return {
        "mounts": [
            {
                "target": str(mount.target),
                "source": mount.source,
                "fstype": mount.fstype,
                "options": mount.options,
            }
            for mount in load_mounts()
        ]
    }


def action_preflight(params: dict[str, Any]) -> dict[str, Any]:
    config = load_config(params.get("config_path", "/etc/transferportal/config.yaml"))
    source = Path(_required(params, "source_path"))
    destination = Path(_required(params, "destination_path"))
    mounts = load_mounts()
    safe_source = validate_data_path(source, mounts, config.allowed_mount_prefixes, config.blocked_paths)
    safe_destination = validate_data_path(destination, mounts, config.allowed_mount_prefixes, config.blocked_paths)
    validate_no_overlap(safe_source, safe_destination)
    return {"source_path": str(safe_source), "destination_path": str(safe_destination)}


def action_browse_path(params: dict[str, Any]) -> dict[str, Any]:
    config = load_config(params.get("config_path", "/etc/transferportal/config.yaml"))
    requested = str(params.get("path") or "").strip()
    mounts = load_mounts()
    if not requested:
        roots = [
            mount.target
            for mount in mounts
            if _is_allowed_mount_root(mount.target, config.allowed_mount_prefixes)
            and str(mount.target) != "/"
            and not _is_relative_to(mount.target, config.portal_base)
            and not _is_blocked_path(mount.target, config.blocked_paths)
            and mount.target.is_dir()
        ]
        unique_roots = sorted({str(path): path for path in roots}.values(), key=lambda item: str(item))
        return {
            "path": "",
            "parent": None,
            "entries": [_browse_entry(path) for path in unique_roots],
        }

    current = Path(str(validate_data_path(Path(requested), mounts, config.allowed_mount_prefixes, config.blocked_paths)))
    if not current.is_dir():
        raise HelperInputError(f"{current} is not a directory")

    parent_value = None
    try:
        safe_parent = Path(str(validate_data_path(current.parent, mounts, config.allowed_mount_prefixes, config.blocked_paths)))
        if safe_parent != current:
            parent_value = str(safe_parent)
    except PathValidationError:
        parent_value = None

    entries = []
    try:
        with os.scandir(current) as rows:
            for row in rows:
                try:
                    if row.is_dir(follow_symlinks=False):
                        entries.append({"name": row.name, "path": str(current / row.name)})
                except OSError:
                    continue
    except PermissionError as exc:
        raise HelperInputError(f"permission denied while listing {current}") from exc
    entries.sort(key=lambda item: item["name"].lower())
    return {"path": str(current), "parent": parent_value, "entries": entries}


def action_create_portal(params: dict[str, Any]) -> dict[str, Any]:
    config = load_config(params.get("config_path", "/etc/transferportal/config.yaml"))
    slug = validate_slug(str(_required(params, "slug")))
    source = Path(_required(params, "source_path"))
    destination = Path(_required(params, "destination_path"))
    action_preflight({"source_path": str(source), "destination_path": str(destination), "config_path": str(params.get("config_path", "/etc/transferportal/config.yaml"))})

    portal_root = config.portal_base / slug
    source_mount = portal_root / "source"
    destination_mount = portal_root / "destination"
    source_mount.mkdir(parents=True, exist_ok=True)
    destination_mount.mkdir(parents=True, exist_ok=True)

    units = {
        _mount_unit_name(source_mount): _mount_unit(source, source_mount),
        _mount_unit_name(destination_mount): _mount_unit(destination, destination_mount),
    }
    for name, content in units.items():
        unit_path = SYSTEMD_SYSTEM_DIR / name
        unit_path.write_text(content, encoding="utf-8")
    run(["systemctl", "daemon-reload"])
    for name in units:
        run(["systemctl", "enable", "--now", name])
    return {"portal_root": str(portal_root), "units": sorted(units)}


def action_remove_portal(params: dict[str, Any]) -> dict[str, Any]:
    config = load_config(params.get("config_path", "/etc/transferportal/config.yaml"))
    slug = validate_slug(str(_required(params, "slug")))
    portal_root = config.portal_base / slug
    mount_points = [portal_root / "source", portal_root / "destination"]
    units = [_mount_unit_name(path) for path in mount_points]
    removed_symlinks: list[str] = []
    removed_unit_files: list[str] = []
    removed_directories: list[str] = []

    for name in reversed(units):
        run(["systemctl", "stop", name], check=False)
    for name in reversed(units):
        run(["systemctl", "disable", name], check=False)

    for name in units:
        for symlink in _systemd_unit_symlinks(name):
            symlink.unlink()
            removed_symlinks.append(str(symlink))
        unit_path = SYSTEMD_SYSTEM_DIR / name
        if unit_path.exists() or unit_path.is_symlink():
            unit_path.unlink()
            removed_unit_files.append(str(unit_path))

    run(["systemctl", "daemon-reload"], check=False)
    for name in units:
        run(["systemctl", "reset-failed", name], check=False)
    run(["systemctl", "daemon-reload"], check=False)

    leftovers = _portal_removal_leftovers(units, mount_points)
    if leftovers:
        detail = "; ".join(f"{key}: {', '.join(values)}" for key, values in leftovers.items())
        raise HelperInputError(f"portal removal left dependencies behind ({detail})")

    for path in reversed([portal_root, *mount_points]):
        try:
            path.rmdir()
            removed_directories.append(str(path))
        except FileNotFoundError:
            continue
        except OSError:
            pass

    return {
        "removed_units": units,
        "removed_unit_files": removed_unit_files,
        "removed_symlinks": removed_symlinks,
        "removed_directories": removed_directories,
    }


def action_mount_portal(params: dict[str, Any]) -> dict[str, Any]:
    config = load_config(params.get("config_path", "/etc/transferportal/config.yaml"))
    slug = validate_slug(str(_required(params, "slug")))
    portal_root = config.portal_base / slug
    units = [
        _mount_unit_name(portal_root / "source"),
        _mount_unit_name(portal_root / "destination"),
    ]
    for name in units:
        run(["systemctl", "start", name])
    return {"mounted_units": units}


def action_unmount_portal(params: dict[str, Any]) -> dict[str, Any]:
    config = load_config(params.get("config_path", "/etc/transferportal/config.yaml"))
    slug = validate_slug(str(_required(params, "slug")))
    portal_root = config.portal_base / slug
    units = [
        _mount_unit_name(portal_root / "source"),
        _mount_unit_name(portal_root / "destination"),
    ]
    for name in units:
        run(["systemctl", "stop", name])
    return {"unmounted_units": units}


def action_run_rsync(params: dict[str, Any]) -> dict[str, Any]:
    config = load_config(params.get("config_path", "/etc/transferportal/config.yaml"))
    command = _required(params, "command")
    if not isinstance(command, list) or not command or command[0] != "rsync":
        raise HelperInputError("command must be a non-empty rsync argument array")
    for arg in command:
        if not isinstance(arg, str) or "\x00" in arg:
            raise HelperInputError("command contains an invalid argument")
    if len(command) < 3:
        raise HelperInputError("rsync command is missing source and destination")
    for path_arg in command[-2:]:
        path = Path(path_arg.rstrip("/")).resolve(strict=False)
        if not _is_relative_to(path, config.portal_base.resolve(strict=False)):
            raise HelperInputError("rsync paths must stay under the configured portal base")
    log_path = Path(_required(params, "log_path"))
    status_path = Path(_required(params, "status_path"))
    status_path.parent.mkdir(parents=True, exist_ok=True)
    runner_command = [
        sys.executable,
        "-m",
        "transferportal.job_runner",
        str(status_path),
        str(log_path),
        json.dumps(command),
    ]
    process = subprocess.Popen(runner_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    return {"pid": process.pid, "log_path": str(log_path), "status_path": str(status_path)}


def action_job_status(params: dict[str, Any]) -> dict[str, Any]:
    pid = int(_required(params, "pid"))
    status_path = Path(_required(params, "status_path"))
    if status_path.exists():
        payload = json.loads(status_path.read_text(encoding="utf-8"))
        if payload.get("state") != "running":
            return {"running": False, **payload}
    return {"running": _pid_exists(pid), "pid": pid, "status_path": str(status_path)}


def action_stop_job(params: dict[str, Any]) -> dict[str, Any]:
    pid = int(_required(params, "pid"))
    if pid <= 1:
        raise HelperInputError("refusing to signal invalid pid")
    if not _is_managed_job_runner(pid):
        raise HelperInputError("refusing to signal a process not managed by transferportal")
    os.killpg(pid, signal.SIGTERM)
    return {"pid": pid, "signal": "SIGTERM"}


def _mount_unit_name(path: Path) -> str:
    escaped = run(["systemd-escape", "--path", "--suffix=mount", str(path)], check=True).stdout.strip()
    if not escaped.endswith(".mount"):
        raise HelperInputError("failed to generate mount unit name")
    return escaped


def _mount_unit(source: Path, target: Path) -> str:
    return f"""[Unit]
Description=Transfer Portal bind mount for {target}

[Mount]
What={source}
Where={target}
Type=none
Options=bind

[Install]
WantedBy=multi-user.target
"""


def _is_allowed_mount_root(path: Path, allowed_mount_prefixes: tuple[Path, ...]) -> bool:
    return any(_is_relative_to(path, prefix) for prefix in allowed_mount_prefixes)


def _is_blocked_path(path: Path, blocked_paths: tuple[Path, ...]) -> bool:
    return any(path == blocked or _is_relative_to(path, blocked) for blocked in blocked_paths if str(blocked) != "/")


def _browse_entry(path: Path) -> dict[str, str]:
    return {"name": path.name or str(path), "path": str(path)}


def _systemd_unit_symlinks(unit_name: str) -> list[Path]:
    if not SYSTEMD_SYSTEM_DIR.exists():
        return []
    return sorted(path for path in SYSTEMD_SYSTEM_DIR.rglob(unit_name) if path.is_symlink())


def _portal_removal_leftovers(unit_names: list[str], mount_points: list[Path]) -> dict[str, list[str]]:
    leftovers: dict[str, list[str]] = {}
    unit_set = set(unit_names)

    unit_files = [name for name in unit_names if (SYSTEMD_SYSTEM_DIR / name).exists() or (SYSTEMD_SYSTEM_DIR / name).is_symlink()]
    if unit_files:
        leftovers["unit_files"] = unit_files

    symlinks = [str(path) for name in unit_names for path in _systemd_unit_symlinks(name)]
    if symlinks:
        leftovers["symlinks"] = symlinks

    unit_file_rows = _listed_systemd_units(["systemctl", "list-unit-files", *unit_names])
    listed_files = sorted(unit_set.intersection(unit_file_rows))
    if listed_files:
        leftovers["listed_unit_files"] = listed_files

    unit_rows = _listed_systemd_units(["systemctl", "list-units", "--all", *unit_names])
    listed_units = sorted(unit_set.intersection(unit_rows))
    if listed_units:
        leftovers["listed_units"] = listed_units

    dependency_result = run(["systemctl", "list-dependencies", "multi-user.target", "--all"], check=False)
    dependency_lines = [line.strip() for line in dependency_result.stdout.splitlines()]
    dependency_refs = sorted(name for name in unit_names if any(name in line for line in dependency_lines))
    if dependency_refs:
        leftovers["dependencies"] = dependency_refs

    mounted_paths = []
    for path in mount_points:
        result = run(["findmnt", "--mountpoint", str(path)], check=False)
        if result.returncode == 0:
            mounted_paths.append(str(path))
    if mounted_paths:
        leftovers["mounted_paths"] = mounted_paths

    return leftovers


def _listed_systemd_units(command: list[str]) -> set[str]:
    result = run(command, check=False)
    units: set[str] = set()
    for line in result.stdout.splitlines():
        first = line.strip().split(maxsplit=1)
        if first and first[0].endswith(".mount"):
            units.add(first[0].lstrip("●"))
    return units


def _is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _pid_exists(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def _is_managed_job_runner(pid: int) -> bool:
    try:
        if os.getpgid(pid) != pid:
            return False
    except ProcessLookupError:
        return False
    except PermissionError:
        return False

    cmdline_path = Path("/proc") / str(pid) / "cmdline"
    try:
        parts = [part for part in cmdline_path.read_bytes().split(b"\0") if part]
    except OSError:
        return False
    return b"-m" in parts and b"transferportal.job_runner" in parts


def _required(params: dict[str, Any], key: str) -> Any:
    if key not in params:
        raise HelperInputError(f"missing required parameter: {key}")
    return params[key]


def _unused(params: dict[str, Any]) -> None:
    if params:
        raise HelperInputError("this action does not accept parameters")


ACTIONS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "list-mounts": action_list_mounts,
    "preflight": action_preflight,
    "browse-path": action_browse_path,
    "create-portal": action_create_portal,
    "remove-portal": action_remove_portal,
    "mount-portal": action_mount_portal,
    "unmount-portal": action_unmount_portal,
    "run-rsync": action_run_rsync,
    "job-status": action_job_status,
    "stop-job": action_stop_job,
}


def handle(payload: dict[str, Any]) -> dict[str, Any]:
    action = payload.get("action")
    params = payload.get("params", {})
    if not isinstance(action, str) or action not in ACTIONS:
        raise HelperInputError("unknown helper action")
    if not isinstance(params, dict):
        raise HelperInputError("params must be an object")
    return ACTIONS[action](params)


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read())
        response = {"ok": True, "response": handle(payload)}
    except (HelperInputError, PathValidationError, ValueError, subprocess.CalledProcessError, OSError) as exc:
        response = {"ok": False, "error": str(exc)}
    sys.stdout.write(json.dumps(response, sort_keys=True))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
