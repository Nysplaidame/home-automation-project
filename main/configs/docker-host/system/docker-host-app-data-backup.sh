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

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required for consistent SQLite backups" >&2
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

backup_path_if_present() {
  name="$1"
  source_path="$2"

  if [ -d "$source_path" ]; then
    backup_path "$name" "$source_path"
  else
    echo "optional backup source is absent, skipping: $name ($source_path)"
  fi
}

backup_sqlite() {
  source_path="$1"
  destination_path="$2"

  if [ ! -f "$source_path" ]; then
    echo "missing SQLite source: $source_path" >&2
    return 1
  fi

  python3 - "$source_path" "$destination_path" <<'PY'
import sqlite3
import sys

source_path, destination_path = sys.argv[1:3]
source = sqlite3.connect(f"file:{source_path}?mode=ro", uri=True)
destination = sqlite3.connect(destination_path)
try:
    source.backup(destination)
finally:
    destination.close()
    source.close()
PY
}

ntfy_stage="$(mktemp -d /var/tmp/ntfy-app-backup.XXXXXX)"
vaultwarden_stage="$(mktemp -d /var/tmp/vaultwarden-app-backup.XXXXXX)"
trap 'rm -rf "$ntfy_stage" "$vaultwarden_stage"' EXIT INT TERM
mkdir -p "$ntfy_stage/etc" "$ntfy_stage/cache"
rsync -aH --exclude=user.db --exclude='user.db-*' /opt/stacks/ntfy/etc/ "$ntfy_stage/etc/"
backup_sqlite /opt/stacks/ntfy/etc/user.db "$ntfy_stage/etc/user.db"
backup_sqlite /opt/stacks/ntfy/cache/cache.db "$ntfy_stage/cache/cache.db"

rsync -aH --exclude='db.sqlite3*' --exclude='db_*.sqlite3' \
  /opt/stacks/vaultwarden/data/ "$vaultwarden_stage/"
backup_sqlite /opt/stacks/vaultwarden/data/db.sqlite3 \
  "$vaultwarden_stage/db.sqlite3"

backup_path mealie /opt/stacks/mealie/data
backup_path grocy /opt/stacks/grocy/config
backup_path household-hub-exports /opt/stacks/household-hub/data/obsidian-exports
backup_path_if_present immich-curated-exporter /opt/stacks/immich-curated-exporter/state

recomp_tracker_stage="$(mktemp -d /var/tmp/recomp-tracker-app-backup.XXXXXX)"
trap 'rm -rf "$ntfy_stage" "$vaultwarden_stage" "$recomp_tracker_stage"' EXIT INT TERM
backup_sqlite /opt/stacks/recomp-tracker/data/recomp.db \
  "$recomp_tracker_stage/recomp.db"
backup_path recomp-tracker "$recomp_tracker_stage"
backup_path obsidian-livesync /opt/stacks/obsidian-livesync/data
backup_path gardenkeeper /opt/stacks/gardenkeeper/backups
backup_path ntfy "$ntfy_stage"
backup_path jellyfin /opt/stacks/jellyfin/config
backup_path calibre-web /opt/stacks/calibre-web/config
backup_path atsumeru-config /opt/stacks/atsumeru/config
backup_path atsumeru-database /opt/stacks/atsumeru/database
backup_path qbittorrent /opt/stacks/download-gateway/qbittorrent-config
backup_path vaultwarden "$vaultwarden_stage"

if [ "$DRY_RUN" != "1" ]; then
  find "$TARGET_ROOT/runs" -mindepth 1 -maxdepth 1 -type d -mtime +"$RETENTION_DAYS" -exec rm -rf {} +
fi

echo "docker-host app-data backup completed at $timestamp dry_run=$DRY_RUN target=$TARGET_ROOT"
