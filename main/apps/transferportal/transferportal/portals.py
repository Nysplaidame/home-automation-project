from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from .models import MetadataPolicy, Portal


SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}$")


class PortalConfigError(ValueError):
    """Raised when portal configuration is invalid."""


def validate_slug(slug: str) -> str:
    if not SLUG_RE.fullmatch(slug):
        raise PortalConfigError("portal slug must use lowercase letters, numbers, and hyphens")
    return slug


def portal_from_mapping(data: dict[str, Any]) -> Portal:
    slug = validate_slug(str(data["slug"]))
    return Portal(
        slug=slug,
        display_name=str(data.get("display_name") or slug),
        source_path=Path(str(data["source_path"])),
        destination_path=Path(str(data["destination_path"])),
        allow_source_delete=bool(data.get("allow_source_delete", False)),
        allow_destination_delete=bool(data.get("allow_destination_delete", False)),
        metadata_policy=MetadataPolicy(str(data.get("metadata_policy", MetadataPolicy.FULL.value))),
        enabled=bool(data.get("enabled", True)),
    )


def portal_to_mapping(portal: Portal) -> dict[str, Any]:
    return {
        "slug": portal.slug,
        "display_name": portal.display_name,
        "source_path": str(portal.source_path),
        "destination_path": str(portal.destination_path),
        "allow_source_delete": portal.allow_source_delete,
        "allow_destination_delete": portal.allow_destination_delete,
        "metadata_policy": portal.metadata_policy.value,
        "enabled": portal.enabled,
    }


def load_portals(config_path: str | Path = "/etc/transferportal/config.yaml") -> list[Portal]:
    path = Path(config_path)
    if not path.exists():
        return []
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    portal_rows = raw.get("portals", [])
    if not isinstance(portal_rows, list):
        raise PortalConfigError("config key portals must be a list")
    return [portal_from_mapping(row) for row in portal_rows]


def save_portals(portals: list[Portal], config_path: str | Path = "/etc/transferportal/config.yaml") -> None:
    path = Path(config_path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {}
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise PortalConfigError("config root must be a mapping")
    raw["portals"] = [portal_to_mapping(portal) for portal in portals]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(raw, sort_keys=False), encoding="utf-8")


def upsert_portal(portal: Portal, config_path: str | Path = "/etc/transferportal/config.yaml") -> None:
    portals = [existing for existing in load_portals(config_path) if existing.slug != portal.slug]
    portals.append(portal)
    portals.sort(key=lambda item: item.slug)
    save_portals(portals, config_path)


def remove_portal(slug: str, config_path: str | Path = "/etc/transferportal/config.yaml") -> Portal:
    slug = validate_slug(slug)
    portals = load_portals(config_path)
    portal = find_portal(portals, slug)
    save_portals([existing for existing in portals if existing.slug != slug], config_path)
    return portal


def find_portal(portals: list[Portal], slug: str) -> Portal:
    for portal in portals:
        if portal.slug == slug:
            return portal
    raise PortalConfigError(f"unknown portal: {slug}")
