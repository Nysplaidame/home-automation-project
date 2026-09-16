#!/bin/sh
set -eu

config_file="${DOCKER_HOST_BACKUP_KUMA_ENV:-/etc/default/docker-host-backup-kuma-heartbeat}"

if [ ! -r "$config_file" ]; then
  echo "missing heartbeat configuration: $config_file" >&2
  exit 1
fi

set -a
. "$config_file"
set +a

: "${BACKUP_KUMA_PUSH_URL:?BACKUP_KUMA_PUSH_URL is required}"

curl --fail --silent --show-error --max-time 15 --get \
  --data-urlencode 'status=up' \
  --data-urlencode 'msg=Docker-host app-data backup completed' \
  "$BACKUP_KUMA_PUSH_URL" >/dev/null
