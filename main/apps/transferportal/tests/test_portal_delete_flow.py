from pathlib import Path

from fastapi.testclient import TestClient

from transferportal import app as app_module
from transferportal.models import JobStatus, Portal
from transferportal.portals import load_portals, save_portals


class FakeHelper:
    def __init__(self) -> None:
        self.requests: list[tuple[str, dict[str, str]]] = []

    def request(self, action: str, params: dict[str, str]) -> dict[str, object]:
        self.requests.append((action, params))
        return {"response": {"removed_units": ["source.mount", "destination.mount"]}}


def make_client(tmp_path, monkeypatch, portals: list[Portal]) -> tuple[TestClient, FakeHelper, Path]:
    config = tmp_path / "config.yaml"
    config.write_text(
        f"""
database_path: {tmp_path / "jobs.sqlite"}
log_dir: {tmp_path}
portal_base: /srv/transferportal
helper_path: /usr/local/lib/transferportal/root-helper
""",
        encoding="utf-8",
    )
    save_portals(portals, config)
    monkeypatch.setattr(app_module, "CONFIG_PATH", config)
    monkeypatch.setenv("TRANSFERPORTAL_ADMIN_PASSWORD", "test-password")
    app = app_module.create_app()
    helper = FakeHelper()
    app.state.helper = helper
    client = TestClient(app)
    response = client.post("/login", data={"username": "admin", "password": "test-password"})
    assert response.status_code == 200
    return client, helper, config


def test_delete_portal_cleans_helper_before_removing_config(tmp_path, monkeypatch):
    portal = Portal("cleanupcheck", "Cleanup Check", Path("/srv/source"), Path("/srv/destination"))
    client, helper, config = make_client(tmp_path, monkeypatch, [portal])

    response = client.post("/portals/cleanupcheck/delete", data={"confirm_slug": "cleanupcheck"}, follow_redirects=False)

    assert response.status_code == 303
    assert helper.requests == [
        (
            "remove-portal",
            {"slug": "cleanupcheck"},
        )
    ]
    assert load_portals(config) == []


def test_delete_portal_confirmation_mismatch_keeps_config_and_shows_html_error(tmp_path, monkeypatch):
    portal = Portal("cleanupcheck", "Cleanup Check", Path("/srv/source"), Path("/srv/destination"))
    client, helper, config = make_client(tmp_path, monkeypatch, [portal])

    response = client.post("/portals/cleanupcheck/delete", data={"confirm_slug": "wrong"})

    body = response.text
    assert response.status_code == 400
    assert "confirmation did not match" in body
    assert '"detail"' not in body
    assert helper.requests == []
    assert [stored.slug for stored in load_portals(config)] == ["cleanupcheck"]


def test_delete_portal_blocks_when_portal_has_active_job(tmp_path, monkeypatch):
    portal = Portal("cleanupcheck", "Cleanup Check", Path("/srv/source"), Path("/srv/destination"))
    client, helper, config = make_client(tmp_path, monkeypatch, [portal])
    client.app.state.store.create_job(
        "cleanupcheck",
        "copy",
        JobStatus.RUNNING.value,
        {},
        ("rsync", "-a", "/srv/source/", "/srv/destination/"),
        "rsync",
        tmp_path / "job.log",
        tmp_path / "job.status.json",
    )

    response = client.post("/portals/cleanupcheck/delete", data={"confirm_slug": "cleanupcheck"})

    assert response.status_code == 409
    assert "active transfer job" in response.text
    assert helper.requests == []
    assert [stored.slug for stored in load_portals(config)] == ["cleanupcheck"]


def test_duplicate_portal_slug_is_rejected_before_helper_call(tmp_path, monkeypatch):
    portal = Portal("duplicate", "Duplicate", Path("/srv/source"), Path("/srv/destination"))
    client, helper, _config = make_client(tmp_path, monkeypatch, [portal])

    response = client.post(
        "/portals",
        data={
            "slug": "duplicate",
            "display_name": "Replacement",
            "source_path": "/srv/other-source",
            "destination_path": "/srv/other-destination",
        },
    )

    assert response.status_code == 409
    assert "already exists" in response.text
    assert helper.requests == []


def test_preview_copy_stores_dry_run_and_cannot_be_retried(tmp_path, monkeypatch):
    portal = Portal("preview", "Preview", Path("/srv/source"), Path("/srv/destination"))
    client, helper, _config = make_client(tmp_path, monkeypatch, [portal])

    response = client.post(
        "/jobs/copy",
        data={"portal_slug": "preview", "preview_only": "on"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    job = client.app.state.store.list_jobs()[0]
    assert "--dry-run" in job["command_json"]
    retry = client.post(f"/jobs/{job['id']}/retry")
    assert retry.status_code == 409
    assert "preview jobs cannot be retried" in retry.text
    assert helper.requests == []


def test_move_route_is_disabled(tmp_path, monkeypatch):
    portal = Portal("move", "Move", Path("/srv/source"), Path("/srv/destination"), allow_source_delete=True)
    client, helper, _config = make_client(tmp_path, monkeypatch, [portal])

    response = client.post("/jobs/move", data={"portal_slug": "move", "confirm_move": "confirm"})

    assert response.status_code == 409
    assert "move mode is disabled" in response.text
    assert helper.requests == []
