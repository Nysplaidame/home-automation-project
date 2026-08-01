#!/bin/sh
set -eu

config_file=/etc/default/omv-smart-kuma-heartbeat
smartctl_bin=/usr/sbin/smartctl
curl_bin=/usr/bin/curl

if [ ! -r "$config_file" ]; then
  echo "Missing $config_file" >&2
  exit 1
fi

# shellcheck disable=SC1090
. "$config_file"
: "${KUMA_PUSH_URL:?KUMA_PUSH_URL is required}"

devices="$($smartctl_bin --scan-open | awk '{print $1}')"
if [ -z "$devices" ]; then
  $curl_bin -fsS --connect-timeout 5 --max-time 15 --get \
    --data-urlencode 'status=down' \
    --data-urlencode 'msg=smartctl found no physical disks' \
    "$KUMA_PUSH_URL" >/dev/null
  exit 1
fi

checked=0
failed=''
for device in $devices; do
  checked=$((checked + 1))
  output="$($smartctl_bin -H "$device" 2>&1 || true)"
  if ! printf '%s\n' "$output" | grep -Eq \
    'SMART overall-health self-assessment test result: PASSED|SMART Health Status: OK'; then
    failed="$failed $device"
  fi
done

if [ -n "$failed" ]; then
  $curl_bin -fsS --connect-timeout 5 --max-time 15 --get \
    --data-urlencode 'status=down' \
    --data-urlencode "msg=SMART health failed:${failed}" \
    --data-urlencode "ping=$checked" \
    "$KUMA_PUSH_URL" >/dev/null
  exit 1
fi

$curl_bin -fsS --connect-timeout 5 --max-time 15 --get \
  --data-urlencode 'status=up' \
  --data-urlencode "msg=All $checked physical disks report healthy" \
  --data-urlencode "ping=$checked" \
  "$KUMA_PUSH_URL" >/dev/null
