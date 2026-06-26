from pathlib import Path

import pytest

from transferportal.models import JobStatus, Portal
from transferportal.move_mode import MoveModeError, MoveState, next_move_status


def portal(allow_source_delete: bool = False) -> Portal:
    return Portal(
        slug="test",
        display_name="Test",
        source_path=Path("/srv/source"),
        destination_path=Path("/srv/destination"),
        allow_source_delete=allow_source_delete,
    )


def test_copy_success_advances_to_verify():
    state = MoveState(JobStatus.RUNNING, copy_exit_code=0)

    assert next_move_status(portal(), state) == JobStatus.VERIFYING


def test_verify_with_pending_changes_fails():
    state = MoveState(JobStatus.VERIFYING, verify_pending_changes=True)

    assert next_move_status(portal(allow_source_delete=True), state) == JobStatus.FAILED


def test_verify_without_delete_permission_raises():
    state = MoveState(JobStatus.VERIFYING, verify_pending_changes=False)

    with pytest.raises(MoveModeError):
        next_move_status(portal(allow_source_delete=False), state)


def test_confirmed_delete_advances_to_delete_phase():
    state = MoveState(JobStatus.WAITING_FOR_DELETE_CONFIRMATION, user_confirmed_delete=True)

    assert next_move_status(portal(allow_source_delete=True), state) == JobStatus.DELETING_SOURCE

