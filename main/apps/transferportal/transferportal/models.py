from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path, PurePosixPath
from typing import Any


class JobMode(StrEnum):
    DRY_RUN = "dry_run"
    COPY = "copy"
    MOVE_AFTER_VERIFIED_COPY = "move_after_verified_copy"


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    VERIFYING = "verifying"
    WAITING_FOR_DELETE_CONFIRMATION = "waiting_for_delete_confirmation"
    DELETING_SOURCE = "deleting_source"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"


class MetadataPolicy(StrEnum):
    FULL = "full"
    STANDARD = "standard"
    COMPATIBLE = "compatible"


@dataclass(frozen=True)
class Portal:
    slug: str
    display_name: str
    source_path: Path
    destination_path: Path
    allow_source_delete: bool = False
    allow_destination_delete: bool = False
    metadata_policy: MetadataPolicy = MetadataPolicy.FULL
    enabled: bool = True

    @property
    def source_mount(self) -> PurePosixPath:
        return PurePosixPath("/srv/transferportal") / self.slug / "source"

    @property
    def destination_mount(self) -> PurePosixPath:
        return PurePosixPath("/srv/transferportal") / self.slug / "destination"


@dataclass(frozen=True)
class RsyncOptions:
    skip_existing: bool = False
    update_newer_only: bool = False
    checksum_compare: bool = False
    size_only_compare: bool = False
    delete_destination_extras: bool = False
    preserve_acls: bool = True
    preserve_xattrs: bool = True
    preserve_owner_group: bool = True
    preserve_permissions: bool = True
    preserve_hard_links: bool = True
    numeric_ids: bool = True
    partial_dir: str = ".rsync-partial"
    advanced_flags: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class TransferJob:
    id: int | None
    portal_slug: str
    mode: JobMode
    options: RsyncOptions
    status: JobStatus = JobStatus.QUEUED
    command: tuple[str, ...] = field(default_factory=tuple)
    current_phase: str = "queued"
    exit_code: int | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: datetime | None = None
    ended_at: datetime | None = None
    log_path: Path | None = None
    error: str | None = None

    def to_record(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "portal_slug": self.portal_slug,
            "mode": self.mode.value,
            "status": self.status.value,
            "command": list(self.command),
            "current_phase": self.current_phase,
            "exit_code": self.exit_code,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "log_path": str(self.log_path) if self.log_path else None,
            "error": self.error,
        }
