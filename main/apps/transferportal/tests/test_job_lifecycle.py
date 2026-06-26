from pathlib import Path
from types import SimpleNamespace

from transferportal.app import refresh_jobs
from transferportal.models import JobStatus
from transferportal.store import JobStore


class FakeHelper:
    def __init__(self, response):
        self.response = response

    def request(self, action, params):
        assert action == "job-status"
        assert "pid" in params
        assert "status_path" in params
        return {"response": self.response}


def make_app(store, response):
    return SimpleNamespace(state=SimpleNamespace(store=store, helper=FakeHelper(response)))


def create_running_job(store: JobStore, tmp_path: Path) -> int:
    job_id = store.create_job(
        "test",
        "copy",
        JobStatus.QUEUED.value,
        {},
        ("rsync", "-r", "/srv/transferportal/test/source/", "/srv/transferportal/test/destination/"),
        "queued",
        tmp_path / "job.log",
        tmp_path / "job.status.json",
    )
    store.mark_launched(job_id, 1234)
    return job_id


def test_refresh_marks_completed_job(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite")
    job_id = create_running_job(store, tmp_path)
    app = make_app(store, {"running": False, "state": "completed", "exit_code": 0})

    refresh_jobs(app, "tester")

    job = store.get_job(job_id)
    assert job["status"] == JobStatus.COMPLETED.value
    assert job["exit_code"] == 0


def test_refresh_marks_failed_job(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite")
    job_id = create_running_job(store, tmp_path)
    app = make_app(store, {"running": False, "state": "failed", "exit_code": 23})

    refresh_jobs(app, "tester")

    job = store.get_job(job_id)
    assert job["status"] == JobStatus.FAILED.value
    assert job["exit_code"] == 23
    assert "rsync exited 23" in job["error"]


def test_refresh_marks_interrupted_job(tmp_path):
    store = JobStore(tmp_path / "jobs.sqlite")
    job_id = create_running_job(store, tmp_path)
    app = make_app(store, {"running": False, "state": "interrupted", "exit_code": -15})

    refresh_jobs(app, "tester")

    job = store.get_job(job_id)
    assert job["status"] == JobStatus.INTERRUPTED.value
    assert job["exit_code"] == -15

