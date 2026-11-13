#!/bin/sh
set -eu

# Native apt-cacher-ng INPUT permission; not a Docker routed/DOCKER-USER rule.
# Preview is the default. Source preparation does not authorize live application.
UFW_BIN="${UFW_BIN:-/usr/sbin/ufw}"
mode="${1:---dry-run}"
if [ "$#" -gt 1 ]; then
  echo "Usage: $0 [--dry-run|--apply]" >&2
  exit 2
fi
case "$mode" in
  --dry-run) set -- --dry-run ;;
  --apply) set -- ;;
  *) echo "Usage: $0 [--dry-run|--apply]" >&2; exit 2 ;;
esac
if ! command -v "$UFW_BIN" >/dev/null 2>&1; then
  echo "ERROR: ufw binary unavailable" >&2
  exit 1
fi
"$UFW_BIN" "$@" allow in from 192.168.20.104 to 192.168.20.102 \
  port 3142 proto tcp comment "CT114 to APT cache"
