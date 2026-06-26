from pathlib import Path

import pytest

from transferportal.models import JobMode, Portal, RsyncOptions
from transferportal.rsync import RsyncOptionError, build_rsync_command


def portal(**kwargs) -> Portal:
    defaults = {
        "slug": "test",
        "display_name": "Test",
        "source_path": Path("/srv/source"),
        "destination_path": Path("/srv/destination"),
    }
    defaults.update(kwargs)
    return Portal(**defaults)


def test_default_command_is_array_preview_shape():
    command = build_rsync_command(portal(), RsyncOptions())

    assert command[0] == "rsync"
    assert "--numeric-ids" in command
    assert "--info=progress2" in command
    assert "--partial-dir=.rsync-partial" in command
    assert command[-2:] == ("/srv/transferportal/test/source/", "/srv/transferportal/test/destination/")


def test_dry_run_adds_dry_run_flag():
    command = build_rsync_command(portal(), RsyncOptions(), JobMode.DRY_RUN)

    assert "--dry-run" in command


def test_delete_destination_requires_portal_permission():
    with pytest.raises(RsyncOptionError, match="destination deletions"):
        build_rsync_command(portal(), RsyncOptions(delete_destination_extras=True))


def test_delete_destination_allowed_when_portal_permits_it():
    command = build_rsync_command(
        portal(allow_destination_delete=True),
        RsyncOptions(delete_destination_extras=True),
    )

    assert "--delete" in command


def test_checksum_and_size_only_are_mutually_exclusive():
    with pytest.raises(RsyncOptionError, match="cannot both"):
        build_rsync_command(portal(), RsyncOptions(checksum_compare=True, size_only_compare=True))


def test_rejects_non_allowlisted_advanced_flag():
    with pytest.raises(RsyncOptionError, match="not allowlisted"):
        build_rsync_command(portal(), RsyncOptions(advanced_flags=("--delete-excluded",)))

