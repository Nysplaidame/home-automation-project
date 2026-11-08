#!/bin/sh
set -eu

incoming=${1:?release staging directory is required}
target=/opt/stacks/mermaid-viewer
backup_root=/opt/backups

case "$incoming" in
  /tmp/mermaid-viewer-release-*) ;;
  *) echo "Refusing unexpected release path: $incoming" >&2; exit 2 ;;
esac

test -d "$incoming/dist"
test -f "$incoming/docker-compose.yml"
test -f "$incoming/nginx.conf"

(
  cd "$incoming/dist"
  sha256sum -c SHA256SUMS
)
docker compose -f "$incoming/docker-compose.yml" config --quiet

stamp=$(date -u +%Y%m%dT%H%M%SZ)
backup="$backup_root/mermaid-viewer-release-$stamp"
previous="${target}.previous-$stamp"
install -d -m 0750 "$backup_root"

if [ -e "$target" ]; then
  cp -a "$target" "$backup"
  docker compose -f "$target/docker-compose.yml" down
  mv "$target" "$previous"
fi

if mv "$incoming" "$target" && docker compose -f "$target/docker-compose.yml" up -d; then
  rm -rf "$previous"
  docker compose -f "$target/docker-compose.yml" ps
  printf 'Deployed Mermaid Viewer release; backup: %s\n' "$backup"
  exit 0
fi

echo 'Deployment failed; restoring the previous stack.' >&2
docker compose -f "$target/docker-compose.yml" down 2>/dev/null || true
mv "$target" "${target}.failed-$stamp" 2>/dev/null || true
if [ -e "$previous" ]; then
  mv "$previous" "$target"
  docker compose -f "$target/docker-compose.yml" up -d
fi
exit 1
