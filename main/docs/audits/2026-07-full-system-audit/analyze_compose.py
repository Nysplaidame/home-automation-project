#!/usr/bin/env python3
"""Create a redacted static inventory of repository Compose services."""

from __future__ import annotations

import csv
import re
from pathlib import Path

import yaml


AUDIT_DIR = Path(__file__).resolve().parent
MAIN = AUDIT_DIR.parents[2]


def image_policy(image: str) -> str:
    if image == "<build-only>":
        return "local-build"
    if "@sha256:" in image:
        return "digest-pinned"
    tag = image.rsplit(":", 1)[1] if ":" in image.rsplit("/", 1)[-1] else "implicit-latest"
    if tag in {"latest", "main", "stable", "release"} or "${" in tag:
        return "floating/logical-tag"
    return "version-tagged"


def main() -> None:
    rows: list[dict[str, str]] = []
    candidates = sorted(
        path
        for path in MAIN.rglob("*")
        if path.is_file() and path.name in {"docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"} and "_archive" not in path.parts
    )
    for path in candidates:
        data = yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}
        for service, config in (data.get("services") or {}).items():
            config = config or {}
            image = str(config.get("image", "<build-only>"))
            volumes = [str(value) for value in config.get("volumes", [])]
            socket_mount = any("/var/run/docker.sock" in value for value in volumes)
            env_names = sorted(
                str(value).split("=", 1)[0]
                for value in config.get("environment", [])
            ) if isinstance(config.get("environment"), list) else sorted((config.get("environment") or {}).keys())
            rows.append(
                {
                    "compose": path.relative_to(MAIN).as_posix(),
                    "service": str(service),
                    "image": image,
                    "image_policy": image_policy(image),
                    "ports": ";".join(str(value) for value in config.get("ports", [])),
                    "network_mode": str(config.get("network_mode", "compose-default")),
                    "privileged": str(bool(config.get("privileged", False))).lower(),
                    "docker_socket": str(socket_mount).lower(),
                    "healthcheck": str("healthcheck" in config).lower(),
                    "restart": str(config.get("restart", "unset")),
                    "read_only": str(bool(config.get("read_only", False))).lower(),
                    "cap_drop": ";".join(str(value) for value in config.get("cap_drop", [])),
                    "resource_limits": str(any(key in config for key in ("mem_limit", "cpus", "deploy"))).lower(),
                    "env_names": ";".join(env_names),
                    "env_files": ";".join(str(value) for value in config.get("env_file", [])) if isinstance(config.get("env_file"), list) else str(config.get("env_file", "")),
                    "volume_count": str(len(volumes)),
                }
            )
    fields = list(rows[0].keys())
    with (AUDIT_DIR / "compose-inventory.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"compose_files={len(candidates)} services={len(rows)}")


if __name__ == "__main__":
    main()
