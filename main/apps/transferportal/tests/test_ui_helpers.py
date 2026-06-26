from pathlib import Path

from transferportal.app import job_portal_mapping, login_page, portal_card, portal_form, settings_view, transfer_form
from transferportal.models import Portal
from transferportal.settings import AppConfig


def test_invalid_login_page_renders_message_without_json_error_page():
    response = login_page("Username or password was not recognised.", username="admin", status_code=401)
    body = response.body.decode()

    assert response.status_code == 401
    assert "Username or password was not recognised." in body
    assert "name=\"username\"" in body
    assert "value=\"admin\"" in body
    assert '"detail"' not in body


def test_new_portal_form_has_back_cancel_and_field_help():
    body = portal_form()

    assert 'href="/">Back</a>' in body
    assert 'href="/">Cancel</a>' in body
    assert "Short machine name" in body
    assert "Existing directory on the source data filesystem" in body
    assert "Destructive permissions" in body
    assert 'name="source_path" placeholder="/srv/dev-disk-by-uuid-xxxxxxx/source_folder"' in body
    assert 'name="destination_path" placeholder="/srv/dev-disk-by-uuid-xxxxxxx/destination_folder"' in body
    assert 'data-browse-field="source_path"' in body
    assert 'data-browse-field="destination_path"' in body
    assert "/api/browse" in body
    assert 'name="source_path" value=' not in body
    assert 'name="destination_path" value=' not in body


def test_settings_view_is_human_readable_not_repr_dump():
    body = settings_view(
        AppConfig(
            bind_host="192.168.10.147",
            bind_port=8088,
            database_path=Path("/var/lib/transferportal/jobs.sqlite"),
            log_dir=Path("/var/log/transferportal"),
            helper_path=Path("/usr/local/lib/transferportal/root-helper"),
            portal_base=Path("/srv/transferportal"),
        ),
        [Portal("smoke", "Smoke", Path("/srv/source"), Path("/srv/destination"))],
        job_count=4,
        active_jobs=0,
    )

    assert "Runtime" in body
    assert "Allowed mount prefixes" in body
    assert "Portal paths" in body
    assert "do not need to be OMV shared folders" in body
    assert "mount points, not copies" in body
    assert "1 total, 1 enabled" in body
    assert "AppConfig(" not in body
    assert "<pre>" not in body


def test_transfer_form_does_not_preview_by_default():
    portal = Portal("test", "Test", Path("/srv/source"), Path("/srv/destination"))

    body = transfer_form([portal], "test")

    assert 'name="preview_only" checked' not in body
    assert "Preview command only, do not run rsync" in body


def test_portal_card_shows_real_backing_folders():
    portal = Portal(
        "test",
        "Test",
        Path("/srv/dev-disk-by-uuid-source/Print/Cases"),
        Path("/srv/dev-disk-by-uuid-destination/Media"),
    )

    body = portal_card(portal)

    assert "/srv/dev-disk-by-uuid-source/Print/Cases" in body
    assert "/srv/dev-disk-by-uuid-destination/Media" in body
    assert "/srv/transferportal/test/source" not in body


def test_job_mapping_shows_real_and_portal_paths(tmp_path, monkeypatch):
    config = tmp_path / "config.yaml"
    config.write_text(
        """
portals:
  - slug: test
    display_name: Test
    source_path: /srv/dev-disk-by-uuid-source/Print/Cases
    destination_path: /srv/dev-disk-by-uuid-destination/Media
""",
        encoding="utf-8",
    )
    monkeypatch.setattr("transferportal.app.CONFIG_PATH", config)

    body = job_portal_mapping({"portal_slug": "test"})

    assert "Real source folder" in body
    assert "/srv/dev-disk-by-uuid-source/Print/Cases" in body
    assert "Portal source mount" in body
    assert "/srv/transferportal/test/source" in body
    assert "Real destination folder" in body
    assert "/srv/dev-disk-by-uuid-destination/Media" in body
    assert "Portal destination mount" in body
    assert "/srv/transferportal/test/destination" in body
