from __future__ import annotations

from dataclasses import dataclass

from .models import JobStatus, Portal


class MoveModeError(ValueError):
    """Raised when move-after-copy cannot advance safely."""


@dataclass(frozen=True)
class MoveState:
    status: JobStatus
    copy_exit_code: int | None = None
    verify_pending_changes: bool | None = None
    user_confirmed_delete: bool = False


def next_move_status(portal: Portal, state: MoveState) -> JobStatus:
    if state.status == JobStatus.RUNNING:
        if state.copy_exit_code is None:
            return JobStatus.RUNNING
        if state.copy_exit_code != 0:
            return JobStatus.FAILED
        return JobStatus.VERIFYING

    if state.status == JobStatus.VERIFYING:
        if state.verify_pending_changes is None:
            return JobStatus.VERIFYING
        if state.verify_pending_changes:
            return JobStatus.FAILED
        if not portal.allow_source_delete:
            raise MoveModeError("portal does not permit source deletion")
        return JobStatus.WAITING_FOR_DELETE_CONFIRMATION

    if state.status == JobStatus.WAITING_FOR_DELETE_CONFIRMATION:
        if not state.user_confirmed_delete:
            return JobStatus.WAITING_FOR_DELETE_CONFIRMATION
        if not portal.allow_source_delete:
            raise MoveModeError("portal does not permit source deletion")
        return JobStatus.DELETING_SOURCE

    if state.status == JobStatus.DELETING_SOURCE:
        return JobStatus.COMPLETED

    return state.status

