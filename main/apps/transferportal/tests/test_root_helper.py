from pathlib import Path
from subprocess import CompletedProcess
from types import SimpleNamespace

import pytest

from transferportal import root_helper
from transferportal.models import Portal
from transferportal.portals import load_portals, remove_portal, save_portals
from transferportal.root_helper import HelperInputError, action_browse_path, action_job_status, action_remove_portal, action_run_rsync, action_stop_job
from transferportal.settings import AppConfig


def set_root_policy(monkeypatch, portal_base: Path, log_dir: Path, allowed: tuple[Path, ...] | None = None) -> None:
    monkeypatch.setattr(
        root_helper,
        "ROOT_POLICY",
        AppConfig(
            portal_base=portal_base,
            log_dir=log_dir,
            allowed_mount_prefixes=allowed or (portal_base.parent,),
            blocked_paths=(Path("/"), Path("/etc"), Path("/var"), Path("/proc")),
        ),
    )


def test_root_helper_rejects_non_rsync_command():
    with pytest.raises(HelperInputError, match="rsync"):
        action_run_rsync({"command": ["bash", "-lc", "id"], "log_path": "/tmp/job.log"})


def test_root_helper_rejects_rsync_paths_outside_portal_base(tmp_path, monkeypatch):
    portal_base = tmp_path / "portal"
    set_root_policy(monkeypatch, portal_base, tmp_path)

    with pytest.raises(HelperInputError, match="portal base"):
        action_run_rsync(
            {
                "command": ["rsync", "-r", "/etc/", str(portal_base / "test" / "destination")],
                "status_path": str(tmp_path / "job.status.json"),
                "log_path": str(tmp_path / "job.log"),
            }
        )


def test_job_status_reads_finished_status_file(tmp_path, monkeypatch):
    set_root_policy(monkeypatch, tmp_path / "portal", tmp_path)
    status = tmp_path / "job.status.json"
    status.write_text('{"state":"completed","pid":999999,"exit_code":0}', encoding="utf-8")

    result = action_job_status({"pid": 999999, "status_path": str(status)})

    assert result["running"] is False
    assert result["state"] == "completed"
    assert result["exit_code"] == 0


def test_job_status_rejects_stale_file_from_another_pid(tmp_path, monkeypatch):
    set_root_policy(monkeypatch, tmp_path / "portal", tmp_path)
    status = tmp_path / "job.status.json"
    status.write_text('{"state":"completed","pid":1234,"exit_code":0}', encoding="utf-8")

    with pytest.raises(HelperInputError, match="does not belong"):
        action_job_status({"pid": 999999, "status_path": str(status)})


def test_stop_job_rejects_unmanaged_pid(monkeypatch):
    monkeypatch.setattr(root_helper, "_is_managed_job_runner", lambda pid: False)

    with pytest.raises(HelperInputError, match="not managed"):
        action_stop_job({"pid": 1234})


def test_stop_job_signals_managed_process_group(monkeypatch):
    killed: list[tuple[int, int]] = []
    monkeypatch.setattr(root_helper, "_is_managed_job_runner", lambda pid: True)
    monkeypatch.setattr(root_helper.os, "killpg", lambda pid, sig: killed.append((pid, sig)), raising=False)

    result = action_stop_job({"pid": 1234})

    assert result == {"pid": 1234, "signal": "SIGTERM"}
    assert killed == [(1234, root_helper.signal.SIGTERM)]


def test_browse_path_lists_allowed_mount_roots_and_child_dirs(tmp_path, monkeypatch):
    disk = tmp_path / "disk"
    portal_mount = tmp_path / "portal" / "existing"
    photos = disk / "photos"
    movies = disk / "movies"
    disk.mkdir()
    portal_mount.mkdir(parents=True)
    photos.mkdir()
    movies.mkdir()
    (disk / "file.txt").write_text("not a folder", encoding="utf-8")
    if hasattr(Path, "symlink_to"):
        try:
            (disk / "linked").symlink_to(tmp_path, target_is_directory=True)
        except OSError:
            pass
    set_root_policy(monkeypatch, tmp_path / "portal", tmp_path, (tmp_path,))
    monkeypatch.setattr(
        root_helper,
        "load_mounts",
        lambda: [
            root_helper.MountInfo(target=disk, source="/dev/test", fstype="ext4"),
            root_helper.MountInfo(target=portal_mount, source="/dev/bind", fstype="ext4"),
        ],
    )

    roots = action_browse_path({})
    children = action_browse_path({"path": str(disk)})

    assert roots["entries"] == [{"name": "disk", "path": str(disk)}]
    assert [entry["name"] for entry in children["entries"]] == ["movies", "photos"]
    assert children["path"] == str(disk)


def test_remove_portal_cleans_units_symlinks_and_empty_dirs(tmp_path, monkeypatch):
    portal_base = tmp_path / "transferportal"
    portal_root = portal_base / "cleanupcheck"
    source_mount = portal_root / "source"
    destination_mount = portal_root / "destination"
    source_mount.mkdir(parents=True)
    destination_mount.mkdir()
    set_root_policy(monkeypatch, portal_base, tmp_path)

    systemd_dir = tmp_path / "systemd"
    wants_dir = systemd_dir / "multi-user.target.wants"
    wants_dir.mkdir(parents=True)
    monkeypatch.setattr(root_helper, "SYSTEMD_SYSTEM_DIR", systemd_dir)
    monkeypatch.setattr(
        root_helper,
        "_mount_unit_name",
        lambda path: f"{path.name}.mount",
    )

    for unit in ("source.mount", "destination.mount"):
        unit_path = systemd_dir / unit
        unit_path.write_text("[Mount]\n", encoding="utf-8")
        try:
            (wants_dir / unit).symlink_to(unit_path)
        except OSError:
            pytest.skip("symlinks are unavailable on this test host")

    commands: list[list[str]] = []

    def fake_run(command: list[str], check: bool = True) -> CompletedProcess[str]:
        commands.append(command)
        return CompletedProcess(command, 1 if command[0] == "findmnt" else 0, "", "")

    monkeypatch.setattr(root_helper, "run", fake_run)

    result = action_remove_portal({"slug": "cleanupcheck"})

    assert result["removed_units"] == ["source.mount", "destination.mount"]
    assert not (systemd_dir / "source.mount").exists()
    assert not (systemd_dir / "destination.mount").exists()
    assert not (wants_dir / "source.mount").exists()
    assert not (wants_dir / "destination.mount").exists()
    assert not portal_root.exists()
    assert ["systemctl", "stop", "destination.mount"] in commands
    assert ["systemctl", "disable", "destination.mount"] in commands
    assert ["systemctl", "reset-failed", "source.mount"] in commands
    assert ["systemctl", "list-dependencies", "multi-user.target", "--all"] in commands


def test_remove_portal_fails_if_systemd_still_lists_unit(tmp_path, monkeypatch):
    portal_base = tmp_path / "transferportal"
    (portal_base / "cleanupcheck" / "source").mkdir(parents=True)
    (portal_base / "cleanupcheck" / "destination").mkdir()
    set_root_policy(monkeypatch, portal_base, tmp_path)

    systemd_dir = tmp_path / "systemd"
    systemd_dir.mkdir()
    monkeypatch.setattr(root_helper, "SYSTEMD_SYSTEM_DIR", systemd_dir)
    monkeypatch.setattr(root_helper, "_mount_unit_name", lambda path: f"{path.name}.mount")

    def fake_run(command: list[str], check: bool = True) -> CompletedProcess[str]:
        stdout = ""
        if command[:2] == ["systemctl", "list-unit-files"]:
            stdout = "source.mount enabled\n"
        return CompletedProcess(command, 1 if command[0] == "findmnt" else 0, stdout, "")

    monkeypatch.setattr(root_helper, "run", fake_run)

    with pytest.raises(HelperInputError, match="left dependencies"):
        action_remove_portal({"slug": "cleanupcheck"})


def test_run_rsync_rejects_extra_source_operand(tmp_path, monkeypatch):
    portal_base = tmp_path / "portal"
    source = portal_base / "test" / "source"
    destination = portal_base / "test" / "destination"
    set_root_policy(monkeypatch, portal_base, tmp_path)

    with pytest.raises(HelperInputError, match="allowlisted"):
        action_run_rsync(
            {
                "command": ["rsync", "-r", "/etc/shadow", str(source), str(destination)],
                "status_path": str(tmp_path / "job.status.json"),
                "log_path": str(tmp_path / "job.log"),
            }
        )


def test_run_rsync_requires_both_portal_mounts(tmp_path, monkeypatch):
    portal_base = tmp_path / "portal"
    source = portal_base / "test" / "source"
    destination = portal_base / "test" / "destination"
    source.mkdir(parents=True)
    destination.mkdir()
    set_root_policy(monkeypatch, portal_base, tmp_path)
    monkeypatch.setattr(root_helper, "load_mounts", lambda: [])

    with pytest.raises(HelperInputError, match="not an active mount"):
        action_run_rsync(
            {
                "command": ["rsync", "-r", f"{source}/", f"{destination}/"],
                "status_path": str(tmp_path / "job.status.json"),
                "log_path": str(tmp_path / "job.log"),
            }
        )


def test_run_rsync_accepts_exact_generated_shape_with_active_mounts(tmp_path, monkeypatch):
    portal_base = tmp_path / "portal"
    source = portal_base / "test" / "source"
    destination = portal_base / "test" / "destination"
    source.mkdir(parents=True)
    destination.mkdir()
    set_root_policy(monkeypatch, portal_base, tmp_path)
    monkeypatch.setattr(
        root_helper,
        "load_mounts",
        lambda: [
            root_helper.MountInfo(source, "/source", "none"),
            root_helper.MountInfo(destination, "/destination", "none"),
        ],
    )
    launches: list[list[str]] = []
    monkeypatch.setattr(
        root_helper.subprocess,
        "Popen",
        lambda command, **_kwargs: launches.append(command) or SimpleNamespace(pid=4321),
    )

    result = action_run_rsync(
        {
            "command": ["rsync", "-r", "--dry-run", f"{source}/", f"{destination}/"],
            "status_path": str(tmp_path / "job.status.json"),
            "log_path": str(tmp_path / "job.log"),
        }
    )

    assert result["pid"] == 4321
    assert launches[0][1:3] == ["-m", "transferportal.job_runner"]


def test_run_rsync_rejects_delete_even_with_valid_mounts(tmp_path, monkeypatch):
    portal_base = tmp_path / "portal"
    source = portal_base / "test" / "source"
    destination = portal_base / "test" / "destination"
    source.mkdir(parents=True)
    destination.mkdir()
    set_root_policy(monkeypatch, portal_base, tmp_path)

    with pytest.raises(HelperInputError, match="allowlisted"):
        action_run_rsync(
            {
                "command": ["rsync", "-r", "--delete", f"{source}/", f"{destination}/"],
                "status_path": str(tmp_path / "job.status.json"),
                "log_path": str(tmp_path / "job.log"),
            }
        )


def test_run_rsync_rejects_output_path_outside_log_dir(tmp_path, monkeypatch):
    portal_base = tmp_path / "portal"
    source = portal_base / "test" / "source"
    destination = portal_base / "test" / "destination"
    source.mkdir(parents=True)
    destination.mkdir()
    set_root_policy(monkeypatch, portal_base, tmp_path / "logs")
    monkeypatch.setattr(
        root_helper,
        "load_mounts",
        lambda: [
            root_helper.MountInfo(source, "/source", "none"),
            root_helper.MountInfo(destination, "/destination", "none"),
        ],
    )

    with pytest.raises(HelperInputError, match="log directory"):
        action_run_rsync(
            {
                "command": ["rsync", "-r", f"{source}/", f"{destination}/"],
                "status_path": str(tmp_path / "job.status.json"),
                "log_path": str(tmp_path / "job.log"),
            }
        )


def test_remove_portal_config_removes_only_matching_slug(tmp_path):
    config = tmp_path / "config.yaml"
    first = Portal("first", "First", Path("/srv/a"), Path("/srv/b"))
    second = Portal("second", "Second", Path("/srv/c"), Path("/srv/d"))
    save_portals([first, second], config)

    removed = remove_portal("first", config)

    assert removed.slug == "first"
    assert [portal.slug for portal in load_portals(config)] == ["second"]
