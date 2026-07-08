#!/bin/sh
set -eu

TARGET_ROOT="${DOCKER_HOST_APP_BACKUP_TARGET:-/mnt/omv/docker-host-backups}"
RETENTION_DAYS="${DOCKER_HOST_APP_BACKUP_RETENTION_DAYS:-14}"
DRY_RUN="${DOCKER_HOST_APP_BACKUP_DRY_RUN:-0}"

if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN=1
fi

if ! command -v rsync >/dev/null 2>&1; then
  echo "rsync is required" >&2
  exit 1
fi

if ! mountpoint -q "$TARGET_ROOT"; then
  echo "backup target is not mounted: $TARGET_ROOT" >&2
  exit 1
fi

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
latest_root="$TARGET_ROOT/latest"

if [ "$DRY_RUN" = "1" ]; then
  run_root="$TARGET_ROOT/dry-run/$timestamp"
else
  run_root="$TARGET_ROOT/runs/$timestamp"
  mkdir -p "$run_root"
fi

mkdir -p "$latest_root"

backup_path() {
  name="$1"
  source_path="$2"

  if [ ! -d "$source_path" ]; then
    echo "missing source path for $name: $source_path" >&2
    return 1
  fi

  mkdir -p "$run_root/$name" "$latest_root/$name"

  if [ "$DRY_RUN" = "1" ]; then
    rsync -aH --delete --dry-run "$source_path/" "$run_root/$name/"
    rsync -aH --delete --dry-run "$source_path/" "$latest_root/$name/"
  else
    rsync -aH --delete "$source_path/" "$run_root/$name/"
    rsync -aH --delete "$source_path/" "$latest_root/$name/"
  fi
}

backup_path mealie /opt/stacks/mealie/data
backup_path grocy /opt/stacks/grocy/config
backup_path obsidian-livesync /opt/stacks/obsidian-livesync/data
backup_path gardenkeeper /opt/stacks/gardenkeeper/backups

if [ "$DRY_RUN" != "1" ]; then
  find "$TARGET_ROOT/runs" -mindepth 1 -maxdepth 1 -type d -mtime +"$RETENTION_DAYS" -exec rm -rf {} +
fi

echo "docker-host app-data backup completed at $timestamp dry_run=$DRY_RUN target=$TARGET_ROOT"
