from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath


@dataclass(frozen=True)
class MountInfo:
    target: Path
    source: str
    fstype: str
    options: str = ""


class PathValidationError(ValueError):
    """Raised when a requested portal path fails safety validation."""


def _posix(path: Path) -> PurePosixPath:
    value = str(path).replace("\\", "/")
    if value.startswith("//"):
        value = "/" + value.lstrip("/")
    if value.startswith("/"):
        return PurePosixPath(value)
    return PurePosixPath(Path(value).expanduser().resolve(strict=False).as_posix())


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def nearest_mount(path: Path, mounts: list[MountInfo]) -> MountInfo | None:
    resolved_path = _posix(path)
    candidates = [mount for mount in mounts if is_relative_to(resolved_path, _posix(mount.target))]
    if not candidates:
        return None
    return max(candidates, key=lambda mount: len(_posix(mount.target).parts))


def validate_data_path(
    path: Path,
    mounts: list[MountInfo],
    allowed_mount_prefixes: tuple[Path, ...],
    blocked_paths: tuple[Path, ...],
) -> Path:
    resolved_path = _posix(path)
    for blocked in blocked_paths:
        blocked_resolved = _posix(blocked)
        if resolved_path == blocked_resolved:
            raise PathValidationError(f"{resolved_path} is a blocked system path")
        if blocked_resolved != PurePosixPath("/") and is_relative_to(resolved_path, blocked_resolved):
            raise PathValidationError(f"{resolved_path} is inside blocked system path {blocked_resolved}")

    mount = nearest_mount(resolved_path, mounts)
    if mount is None:
        raise PathValidationError(f"{resolved_path} is not on a mounted filesystem")

    mount_target = _posix(mount.target)
    if mount_target == PurePosixPath("/"):
        raise PathValidationError(f"{resolved_path} resolves to the root filesystem")

    if not any(is_relative_to(mount_target, _posix(prefix)) for prefix in allowed_mount_prefixes):
        raise PathValidationError(f"{resolved_path} mount {mount_target} is outside allowed data prefixes")

    return resolved_path


def validate_no_overlap(source: Path, destination: Path) -> None:
    resolved_source = _posix(source)
    resolved_destination = _posix(destination)
    if resolved_source == resolved_destination:
        raise PathValidationError("source and destination cannot be the same path")
    if is_relative_to(resolved_source, resolved_destination):
        raise PathValidationError("source cannot be inside destination")
    if is_relative_to(resolved_destination, resolved_source):
        raise PathValidationError("destination cannot be inside source")
