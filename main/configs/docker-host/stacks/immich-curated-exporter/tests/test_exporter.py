#!/usr/bin/env python3
"""Focused contract tests for the non-destructive Immich curated exporter."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import exporter  # noqa: E402


ALBUM_ID = "11111111-1111-4111-8111-111111111111"
ASSET_ID = "22222222-2222-4222-8222-222222222222"


class FakeImmichClient:
    assets: list[dict[str, object]] = []

    def __init__(self, *_: object) -> None:
        pass

    def json(self, endpoint: str) -> dict[str, object]:
        self.endpoint = endpoint
        return {"assets": self.assets}

    def download(self, asset_id: str, destination: Path, _maximum_bytes: int) -> tuple[str, int]:
        self.downloaded_asset = asset_id
        destination.write_bytes(b"curated-test-asset")
        return ("9d103cc44a0c4c0a4dcc4af0436650b8599a86ea1d07fc1f8cc271e11b8f1d8f", 18)


class ExporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.allow_list = self.root / "albums.json"
        self.allow_list.write_text(
            json.dumps({"schema_version": 1, "albums": [{"id": ALBUM_ID, "collection": "family-favourites"}]}),
            encoding="utf-8",
        )
        self.args = Namespace(
            api_url="http://127.0.0.1:2283/api",
            allow_list=str(self.allow_list),
            media_root=str(self.root / "media"),
            state_root=str(self.root / "state"),
            max_assets_per_album=10,
            max_asset_bytes=1024,
            timeout=5,
            dry_run=False,
        )
        self.old_client = exporter.ImmichClient
        self.old_mount_check = exporter.require_nfs_mount
        exporter.ImmichClient = FakeImmichClient
        exporter.require_nfs_mount = lambda _target: None
        self.old_key = os.environ.get("IMMICH_CURATED_EXPORTER_API_KEY")
        os.environ["IMMICH_CURATED_EXPORTER_API_KEY"] = "test-key"

    def tearDown(self) -> None:
        exporter.ImmichClient = self.old_client
        exporter.require_nfs_mount = self.old_mount_check
        if self.old_key is None:
            os.environ.pop("IMMICH_CURATED_EXPORTER_API_KEY", None)
        else:
            os.environ["IMMICH_CURATED_EXPORTER_API_KEY"] = self.old_key
        self.temp.cleanup()

    def set_assets(self, assets: list[dict[str, object]]) -> None:
        FakeImmichClient.assets = assets

    def test_exports_allowed_asset_and_records_manifest(self) -> None:
        self.set_assets([{"id": ASSET_ID, "checksum": "aGVsbG8=", "originalFileName": "holiday.jpg", "updatedAt": "2026-08-10T10:00:00Z"}])

        self.assertEqual(exporter.export(self.args), 0)
        output = self.root / "media" / "family-favourites" / f"{ASSET_ID}.jpg"
        self.assertEqual(output.read_bytes(), b"curated-test-asset")
        manifest = json.loads((self.root / "state" / "manifest.json").read_text(encoding="utf-8"))
        entry = manifest["exports"][f"family-favourites/{ASSET_ID}"]
        self.assertEqual(entry["asset_checksum"], "aGVsbG8=")
        self.assertEqual(entry["target_relpath"], f"family-favourites/{ASSET_ID}.jpg")

    def test_missing_album_asset_goes_to_review_without_deleting_copy(self) -> None:
        self.set_assets([{"id": ASSET_ID, "checksum": "aGVsbG8=", "originalFileName": "holiday.jpg"}])
        self.assertEqual(exporter.export(self.args), 0)
        output = self.root / "media" / "family-favourites" / f"{ASSET_ID}.jpg"
        self.assertTrue(output.exists())

        self.set_assets([])
        self.assertEqual(exporter.export(self.args), 0)
        self.assertTrue(output.exists())
        queue = json.loads((self.root / "state" / "review-queue.json").read_text(encoding="utf-8"))
        self.assertEqual(queue["items"][f"family-favourites/{ASSET_ID}"]["reason"], "absent_from_allowed_album")

    def test_rejects_path_traversal_collection(self) -> None:
        self.allow_list.write_text(
            json.dumps({"schema_version": 1, "albums": [{"id": ALBUM_ID, "collection": "../not-allowed"}]}),
            encoding="utf-8",
        )
        with self.assertRaises(exporter.ExportError):
            exporter.load_albums(self.allow_list)

    def test_refuses_album_above_configured_limit_before_writing(self) -> None:
        self.set_assets(
            [
                {"id": ASSET_ID, "checksum": "aGVsbG8=", "originalFileName": "one.jpg"},
                {"id": "33333333-3333-4333-8333-333333333333", "checksum": "d29ybGQ=", "originalFileName": "two.jpg"},
            ]
        )
        self.args.max_assets_per_album = 1

        with self.assertRaises(exporter.ExportError):
            exporter.export(self.args)
        self.assertFalse((self.root / "media").exists())


if __name__ == "__main__":
    unittest.main()
