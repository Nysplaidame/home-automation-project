from pathlib import Path

import pytest

from transferportal.path_safety import MountInfo, PathValidationError, validate_data_path, validate_no_overlap


MOUNTS = [
    MountInfo(target=Path("/"), source="/dev/sda1", fstype="ext4"),
    MountInfo(target=Path("/srv/source-disk"), source="/dev/sdb1", fstype="ext4"),
    MountInfo(target=Path("/srv/destination-disk"), source="/dev/sdc1", fstype="ext4"),
]


def test_accepts_path_on_allowed_data_mount():
    result = validate_data_path(
        Path("/srv/source-disk/photos"),
        MOUNTS,
        (Path("/srv"),),
        (Path("/"), Path("/etc"), Path("/var"), Path("/proc")),
    )

    assert str(result) == "/srv/source-disk/photos"


def test_rejects_blocked_system_path():
    with pytest.raises(PathValidationError, match="blocked"):
        validate_data_path(Path("/etc/passwd"), MOUNTS, (Path("/srv"),), (Path("/etc"),))


def test_rejects_root_filesystem():
    with pytest.raises(PathValidationError, match="root filesystem|blocked"):
        validate_data_path(Path("/home"), MOUNTS, (Path("/srv"),), (Path("/boot"),))


def test_rejects_overlapping_source_destination():
    with pytest.raises(PathValidationError, match="inside source"):
        validate_no_overlap(Path("/srv/source-disk"), Path("/srv/source-disk/subdir"))


def test_normalises_absolute_parent_segments_before_mount_checks():
    with pytest.raises(PathValidationError, match="blocked"):
        validate_data_path(
            Path("/srv/source-disk/../../etc"),
            MOUNTS,
            (Path("/srv"),),
            (Path("/etc"),),
        )


def test_resolves_symlink_before_mount_checks(tmp_path):
    data_mount = tmp_path / "data"
    blocked = tmp_path / "blocked"
    data_mount.mkdir()
    blocked.mkdir()
    link = data_mount / "escape"
    try:
        link.symlink_to(blocked, target_is_directory=True)
    except OSError:
        pytest.skip("symlinks are unavailable on this test host")

    with pytest.raises(PathValidationError, match="blocked|mounted filesystem"):
        validate_data_path(
            link,
            [MountInfo(target=data_mount, source="/dev/test", fstype="ext4")],
            (tmp_path,),
            (blocked,),
        )
