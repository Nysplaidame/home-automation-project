from __future__ import annotations

from pathlib import Path

from .models import JobMode, Portal, RsyncOptions


ADVANCED_ALLOWLIST = {
    "--ignore-times",
    "--whole-file",
    "--one-file-system",
    "--inplace",
}


class RsyncOptionError(ValueError):
    """Raised when a requested rsync option is unsafe or contradictory."""


def _slash(path: Path) -> str:
    value = str(path)
    return value if value.endswith("/") else f"{value}/"


def build_rsync_command(
    portal: Portal,
    options: RsyncOptions,
    mode: JobMode = JobMode.COPY,
    verify: bool = False,
) -> tuple[str, ...]:
    if options.checksum_compare and options.size_only_compare:
        raise RsyncOptionError("checksum compare and size-only compare cannot both be enabled")
    if options.delete_destination_extras and not portal.allow_destination_delete:
        raise RsyncOptionError("portal does not permit destination deletions")

    command: list[str] = ["rsync", "-r"]
    if options.preserve_permissions:
        command.append("-p")
    if options.preserve_owner_group:
        command.extend(["-o", "-g"])
    if options.preserve_hard_links:
        command.append("-H")
    if options.preserve_acls:
        command.append("-A")
    if options.preserve_xattrs:
        command.append("-X")
    if options.numeric_ids:
        command.append("--numeric-ids")

    command.extend(["--info=progress2", f"--partial-dir={options.partial_dir}"])

    if mode == JobMode.DRY_RUN or verify:
        command.append("--dry-run")
    if options.skip_existing:
        command.append("--ignore-existing")
    if options.update_newer_only:
        command.append("--update")
    if options.checksum_compare:
        command.append("--checksum")
    if options.size_only_compare:
        command.append("--size-only")
    if options.delete_destination_extras:
        command.append("--delete")

    for flag in options.advanced_flags:
        if flag not in ADVANCED_ALLOWLIST:
            raise RsyncOptionError(f"advanced flag is not allowlisted: {flag}")
        command.append(flag)

    command.extend([_slash(portal.source_mount), _slash(portal.destination_mount)])
    return tuple(command)

