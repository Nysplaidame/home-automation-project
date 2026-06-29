#!/bin/sh
set -eu

STACK_DIR=/opt/stacks/gardenkeeper
BACKUP_DIR="$STACK_DIR/backups"
RETENTION_DAYS="${GARDENKEEPER_BACKUP_RETENTION_DAYS:-14}"

mkdir -p "$BACKUP_DIR"
cd "$STACK_DIR"

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
outfile="$BACKUP_DIR/gardenkeeper-postgres-$timestamp.sql.gz"

postgres_user="$(sed -n 's/^POSTGRES_USER=//p' .env | head -n 1)"
postgres_db="$(sed -n 's/^POSTGRES_DB=//p' .env | head -n 1)"
postgres_user="${postgres_user:-gardenkeeper}"
postgres_db="${postgres_db:-gardenkeeper}"

docker exec gardenkeeper-postgres pg_dump -U "$postgres_user" "$postgres_db" | gzip > "$outfile"
chmod 600 "$outfile"

find "$BACKUP_DIR" -type f -name 'gardenkeeper-postgres-*.sql.gz' -mtime +"$RETENTION_DAYS" -delete
printf 'GardenKeeper backup written: %s\n' "$outfile"
