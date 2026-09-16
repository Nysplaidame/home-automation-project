#!/bin/sh
set -eu
umask 077
TARGET=/mnt/omv/docker-host-backups
EXPECTED_SOURCE=192.168.40.50:/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/docker-host
mountpoint -q "$TARGET"
test "$(findmnt -n -o SOURCE -T "$TARGET")" = "$EXPECTED_SOURCE"
case "$(findmnt -n -o FSTYPE -T "$TARGET")" in nfs|nfs4) ;; *) exit 1 ;; esac
cd /opt/stacks/mediamtx
docker compose config --quiet
test -f .env && test -f docker-compose.yml && test -f mediamtx.yml
install -d -m 0700 "$TARGET/mediamtx-config"
stage=$(mktemp -d "$TARGET/mediamtx-config/.pending.XXXXXX")
trap 'rm -rf -- "$stage"' EXIT
trap 'exit 1' HUP INT TERM
tar -czf "$stage/config.tar.gz" -- .env docker-compose.yml mediamtx.yml
gzip -t "$stage/config.tar.gz"
docker inspect mediamtx --format '{{.Image}}' > "$stage/image-id.txt"
(cd "$stage" && sha256sum config.tar.gz > SHA256SUMS)
# NFS default ACLs can override creation modes; enforce private file access.
chmod 600 "$stage/config.tar.gz" "$stage/image-id.txt" "$stage/SHA256SUMS"
destination="$TARGET/mediamtx-config/$(date -u +%Y%m%dT%H%M%SZ)"
test ! -e "$destination"
mv "$stage" "$destination"
trap - EXIT
printf 'MediaMTX protected config checkpoint: %s\n' "$destination"
# No recording deletion or backup pruning; review these small checkpoints manually.
