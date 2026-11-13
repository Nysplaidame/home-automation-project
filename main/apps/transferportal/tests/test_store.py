from pathlib import Path

import pytest

from transferportal.models import JobStatus
from transferportal.store import JobCapacityError, JobStore


def test_atomic_reservation_enforces_capacity(tmp_path: Path):
    store = JobStore(tmp_path / "jobs.sqlite")
    command = ("rsync", "-r", "/srv/transferportal/test/source/", "/srv/transferportal/test/destination/")
    store.reserve_job("test", "copy", {}, command, tmp_path / "one.log", tmp_path / "one.status.json", 1)

    with pytest.raises(JobCapacityError, match="active"):
        store.reserve_job("test", "copy", {}, command, tmp_path / "two.log", tmp_path / "two.status.json", 1)


def test_startup_marks_unlaunched_queued_job_failed(tmp_path: Path):
    store = JobStore(tmp_path / "jobs.sqlite")
    job_id = store.create_job(
        "test",
        "copy",
        JobStatus.QUEUED.value,
        {},
        ("rsync", "-r", "/source/", "/destination/"),
        "queued",
        tmp_path / "job.log",
        tmp_path / "job.status.json",
    )

    assert store.fail_unlaunched_jobs() == 1
    job = store.get_job(job_id)
    assert job["status"] == JobStatus.FAILED.value
    assert "restart" in job["error"]
