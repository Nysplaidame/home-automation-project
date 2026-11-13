#!/bin/sh
set -eu
umask 077

STACK_DIR="${GARDENKEEPER_STACK_DIR:-/opt/stacks/gardenkeeper}"
BACKUP_DIR="$STACK_DIR/backups"
RETENTION_DAYS="${GARDENKEEPER_BACKUP_RETENTION_DAYS:-14}"
case "$RETENTION_DAYS" in
  ''|*[!0-9]*) echo "Retention must be a non-negative integer" >&2; exit 1 ;;
esac

mkdir -p "$BACKUP_DIR"
cd "$STACK_DIR"
# A concurrent invocation must not replace or prune another job's checkpoint.
lock_dir="$BACKUP_DIR/.backup-lock"
mkdir "$lock_dir" || { echo "Backup already running or stale lock requires review" >&2; exit 1; }
stage_dir=''
cleanup() {
  if [ -n "$stage_dir" ]; then rm -rf -- "$stage_dir"; fi
  rmdir "$lock_dir"
}
trap cleanup EXIT
trap 'exit 1' HUP INT TERM
stage_dir=$(mktemp -d "$BACKUP_DIR/.checkpoint.XXXXXX")
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
outfile="$BACKUP_DIR/gardenkeeper-postgres-$timestamp.sql.gz"
test ! -e "$outfile" || { echo "Checkpoint filename already exists" >&2; exit 1; }

# Separate commands: gzip success must never mask a failed pg_dump.
# Use the database container's actual settings, not shell parsing of .env.
docker exec gardenkeeper-postgres sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' > "$stage_dir/database.sql"
test -s "$stage_dir/database.sql" || { echo "Empty database dump" >&2; exit 1; }
gzip -c "$stage_dir/database.sql" > "$stage_dir/database.sql.gz"
gzip -t "$stage_dir/database.sql.gz"
chmod 600 "$stage_dir/database.sql.gz"
mv "$stage_dir/database.sql.gz" "$outfile"
# Prune only after a complete checked artifact has been published.
find "$BACKUP_DIR" -type f -name 'gardenkeeper-postgres-*.sql.gz' -mtime +"$RETENTION_DAYS" -delete
printf 'GardenKeeper backup written: %s\n' "$outfile"
