#!/usr/bin/env python3
"""Export explicitly allow-listed Immich albums into Jellyfin's read-only tree.

The exporter is deliberately one-way.  It never mutates Immich and never
removes a published file.  Assets no longer returned by an allowed album are
recorded in a review queue for a human to decide on later.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


SCHEMA_VERSION = 1
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$", re.I)
COLLECTION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._-]{0,79}$")
EXTENSION_RE = re.compile(r"^\.[A-Za-z0-9]{1,10}$")


class ExportError(RuntimeError):
    """A safe, operator-actionable exporter failure."""


def now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
        temp_name = handle.name
    os.chmod(temp_name, 0o640)
    os.replace(temp_name, path)


def require_nfs_mount(target: Path) -> None:
    """Reject an accidental local-directory fallback below the OMV export."""
    try:
        result = subprocess.run(
            ["findmnt", "-n", "-o", "FSTYPE", "-T", str(target)],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ExportError(f"cannot verify mount backing {target}: {exc}") from exc
    if result.stdout.strip() not in {"nfs", "nfs4"}:
        raise ExportError(f"refusing to write outside an NFS mount: {target}")


def checksum_text(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    return value


def safe_extension(name: Any) -> str:
    if not isinstance(name, str):
        return ""
    suffix = Path(name).suffix.lower()
    return suffix if EXTENSION_RE.fullmatch(suffix) else ""


@dataclass(frozen=True)
class Album:
    id: str
    collection: str


def load_albums(path: Path) -> list[Album]:
    payload = read_json(path, None)
    if not isinstance(payload, dict) or payload.get("schema_version") != SCHEMA_VERSION:
        raise ExportError(f"{path} must be schema_version {SCHEMA_VERSION}")
    raw_albums = payload.get("albums")
    if not isinstance(raw_albums, list) or not raw_albums:
        raise ExportError("album allow-list must contain at least one album")
    albums: list[Album] = []
    seen_ids: set[str] = set()
    seen_collections: set[str] = set()
    for raw in raw_albums:
        if not isinstance(raw, dict):
            raise ExportError("every album allow-list entry must be an object")
        album_id = raw.get("id")
        collection = raw.get("collection")
        if not isinstance(album_id, str) or not UUID_RE.fullmatch(album_id):
            raise ExportError(f"invalid Immich album UUID: {album_id!r}")
        if not isinstance(collection, str) or not COLLECTION_RE.fullmatch(collection):
            raise ExportError(f"unsafe collection name: {collection!r}")
        normalized_collection = collection.casefold()
        if album_id in seen_ids or normalized_collection in seen_collections:
            raise ExportError("album IDs and collection names must be unique")
        seen_ids.add(album_id)
        seen_collections.add(normalized_collection)
        albums.append(Album(id=album_id, collection=collection))
    return albums


class ImmichClient:
    def __init__(self, api_url: str, api_key: str, timeout: int) -> None:
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

    def request(self, method: str, endpoint: str) -> tuple[bytes, dict[str, str]]:
        request = Request(
            f"{self.api_url}{endpoint}",
            method=method,
            headers={"x-api-key": self.api_key, "Accept": "application/json"},
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:  # nosec B310 -- URL is operator config
                return response.read(), dict(response.headers.items())
        except HTTPError as exc:
            raise ExportError(f"Immich {method} {endpoint} returned HTTP {exc.code}") from exc
        except URLError as exc:
            raise ExportError(f"Immich {method} {endpoint} failed: {exc.reason}") from exc

    def json(self, endpoint: str) -> dict[str, Any]:
        body, _ = self.request("GET", endpoint)
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as exc:
            raise ExportError(f"Immich returned invalid JSON for {endpoint}") from exc
        if not isinstance(payload, dict):
            raise ExportError(f"Immich returned an unexpected JSON shape for {endpoint}")
        return payload

    def download(self, asset_id: str, destination: Path, maximum_bytes: int) -> tuple[str, int]:
        endpoint = f"/assets/{quote(asset_id, safe='')}/original"
        request = Request(
            f"{self.api_url}{endpoint}",
            method="GET",
            headers={"x-api-key": self.api_key},
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:  # nosec B310 -- URL is operator config
                header = response.headers.get("Content-Length")
                if header and int(header) > maximum_bytes:
                    raise ExportError(f"asset {asset_id} exceeds MAX_ASSET_BYTES")
                digest = hashlib.sha256()
                total = 0
                with destination.open("wb") as handle:
                    while chunk := response.read(1024 * 1024):
                        total += len(chunk)
                        if total > maximum_bytes:
                            raise ExportError(f"asset {asset_id} exceeds MAX_ASSET_BYTES")
                        digest.update(chunk)
                        handle.write(chunk)
                    handle.flush()
                    os.fsync(handle.fileno())
                return digest.hexdigest(), total
        except HTTPError as exc:
            raise ExportError(f"Immich GET {endpoint} returned HTTP {exc.code}") from exc
        except (OSError, URLError, ValueError) as exc:
            raise ExportError(f"Immich asset download {asset_id} failed: {exc}") from exc


def details_for_asset(client: ImmichClient, asset: dict[str, Any]) -> dict[str, Any]:
    asset_id = asset.get("id")
    if not isinstance(asset_id, str) or not UUID_RE.fullmatch(asset_id):
        raise ExportError(f"album included an invalid asset ID: {asset_id!r}")
    if checksum_text(asset.get("checksum")) is None or not isinstance(asset.get("originalFileName"), str):
        details = client.json(f"/assets/{quote(asset_id, safe='')}")
        if details.get("id") != asset_id:
            raise ExportError(f"Immich returned mismatched asset details for {asset_id}")
        return details
    return asset


def asset_key(collection: str, asset_id: str) -> str:
    return f"{collection}/{asset_id}"


def review_entry(previous: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "asset_id": previous["asset_id"],
        "collection": previous["collection"],
        "first_detected_at": now(),
        "reason": reason,
        "target_relpath": previous["target_relpath"],
    }


def export(args: argparse.Namespace) -> int:
    api_key = os.environ.get("IMMICH_CURATED_EXPORTER_API_KEY", "")
    if not api_key or api_key.startswith("<"):
        raise ExportError("IMMICH_CURATED_EXPORTER_API_KEY must be set in the local environment file")
    media_root = Path(args.media_root).resolve()
    state_root = Path(args.state_root).resolve()
    allow_list_path = Path(args.allow_list).resolve()
    if not args.dry_run:
        require_nfs_mount(media_root)
    albums = load_albums(allow_list_path)
    manifest_path = state_root / "manifest.json"
    review_path = state_root / "review-queue.json"
    manifest = read_json(manifest_path, {"schema_version": SCHEMA_VERSION, "exports": {}})
    reviews = read_json(review_path, {"schema_version": SCHEMA_VERSION, "items": {}})
    if not isinstance(manifest, dict) or manifest.get("schema_version") != SCHEMA_VERSION or not isinstance(manifest.get("exports"), dict):
        raise ExportError(f"invalid manifest: {manifest_path}")
    if not isinstance(reviews, dict) or reviews.get("schema_version") != SCHEMA_VERSION or not isinstance(reviews.get("items"), dict):
        raise ExportError(f"invalid review queue: {review_path}")

    client = ImmichClient(args.api_url, api_key, args.timeout)
    next_exports = dict(manifest["exports"])
    next_reviews = dict(reviews["items"])
    current_keys: set[str] = set()
    complete_collections: set[str] = set()
    exported = skipped = failures = 0

    for album in albums:
        response = client.json(f"/albums/{quote(album.id, safe='')}")
        assets = response.get("assets")
        if not isinstance(assets, list):
            raise ExportError(f"album {album.id} did not include an assets array")
        if len(assets) > args.max_assets_per_album:
            raise ExportError(f"album {album.id} has {len(assets)} assets; exceeds MAX_ASSETS_PER_ALBUM")
        for raw_asset in assets:
            if not isinstance(raw_asset, dict):
                raise ExportError(f"album {album.id} included an invalid asset record")
            asset = details_for_asset(client, raw_asset)
            asset_id = asset["id"]
            checksum = checksum_text(asset.get("checksum"))
            if checksum is None:
                raise ExportError(f"asset {asset_id} did not provide a checksum")
            key = asset_key(album.collection, asset_id)
            current_keys.add(key)
            extension = safe_extension(asset.get("originalFileName"))
            target_relpath = f"{album.collection}/{asset_id}{extension}"
            target = media_root / target_relpath
            previous = next_exports.get(key)
            if (
                isinstance(previous, dict)
                and previous.get("asset_checksum") == checksum
                and previous.get("target_relpath") == target_relpath
                and target.is_file()
            ):
                skipped += 1
                next_reviews.pop(key, None)
                continue
            if args.dry_run:
                exported += 1
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.parent / f".{asset_id}.part"
            try:
                sha256, size = client.download(asset_id, temporary, args.max_asset_bytes)
                os.chmod(temporary, 0o640)
                os.replace(temporary, target)
            except ExportError as exc:
                temporary.unlink(missing_ok=True)
                next_reviews[key] = review_entry(
                    {
                        "asset_id": asset_id,
                        "collection": album.collection,
                        "target_relpath": target_relpath,
                    },
                    f"download_failed: {exc}",
                )
                failures += 1
                continue
            next_exports[key] = {
                "album_id": album.id,
                "asset_checksum": checksum,
                "asset_id": asset_id,
                "asset_updated_at": asset.get("updatedAt"),
                "bytes": size,
                "collection": album.collection,
                "downloaded_at": now(),
                "sha256": sha256,
                "source_filename": asset.get("originalFileName"),
                "target_relpath": target_relpath,
            }
            next_reviews.pop(key, None)
            exported += 1
        complete_collections.add(album.collection)

    allowed_collections = {album.collection for album in albums}
    for key, previous in manifest["exports"].items():
        if not isinstance(previous, dict) or key in current_keys:
            continue
        if previous.get("collection") not in allowed_collections:
            next_reviews.setdefault(key, review_entry(previous, "collection_removed_from_allow_list"))
        elif previous.get("collection") in complete_collections:
            next_reviews.setdefault(key, review_entry(previous, "absent_from_allowed_album"))

    if not args.dry_run:
        atomic_json(manifest_path, {"schema_version": SCHEMA_VERSION, "generated_at": now(), "exports": next_exports})
        atomic_json(review_path, {"schema_version": SCHEMA_VERSION, "generated_at": now(), "items": next_reviews})
    print(f"immich curated export dry_run={args.dry_run} exported={exported} skipped={skipped} review_items={len(next_reviews)} failures={failures}")
    return 1 if failures else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default=os.environ.get("IMMICH_CURATED_EXPORTER_API_URL", "http://127.0.0.1:2283/api"))
    parser.add_argument("--allow-list", default=os.environ.get("IMMICH_CURATED_EXPORTER_ALLOW_LIST", "/opt/stacks/immich-curated-exporter/albums.json"))
    parser.add_argument("--media-root", default=os.environ.get("IMMICH_CURATED_EXPORTER_MEDIA_ROOT", "/mnt/omv/media/jellyfin/immich-curated"))
    parser.add_argument("--state-root", default=os.environ.get("IMMICH_CURATED_EXPORTER_STATE_ROOT", "/opt/stacks/immich-curated-exporter/state"))
    parser.add_argument("--max-assets-per-album", type=int, default=int(os.environ.get("IMMICH_CURATED_EXPORTER_MAX_ASSETS_PER_ALBUM", "1000")))
    parser.add_argument("--max-asset-bytes", type=int, default=int(os.environ.get("IMMICH_CURATED_EXPORTER_MAX_ASSET_BYTES", str(10 * 1024 * 1024 * 1024))))
    parser.add_argument("--timeout", type=int, default=int(os.environ.get("IMMICH_CURATED_EXPORTER_TIMEOUT", "60")))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if args.max_assets_per_album < 1 or args.max_asset_bytes < 1 or args.timeout < 1:
        parser.error("limits and timeout must be positive")
    return args


if __name__ == "__main__":
    try:
        raise SystemExit(export(parse_args()))
    except ExportError as exc:
        print(f"immich curated export refused: {exc}", file=sys.stderr)
        raise SystemExit(2)
