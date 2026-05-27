#!/bin/sh
set -eu

# Reapply routed DNS allowances required for AdGuard's Docker bridge subnet
# when UFW uses "default deny routed" on docker-host.

UFW_BIN="${UFW_BIN:-/usr/sbin/ufw}"
SRC_SUBNET="${SRC_SUBNET:-172.20.0.0/16}"

if ! command -v "$UFW_BIN" >/dev/null 2>&1; then
    echo "ERROR: ufw binary not found at $UFW_BIN" >&2
    exit 1
fi

add_rule() {
    proto="$1"
    port="$2"
    comment="$3"
    "$UFW_BIN" route allow in on docker0 out on eth0 from "$SRC_SUBNET" to any port "$port" proto "$proto" comment "$comment" >/dev/null
}

# Idempotence relies on UFW de-duplicating equivalent rules.
add_rule udp 53 "AdGuard bridge DNS UDP upstream"
add_rule tcp 53 "AdGuard bridge DNS TCP upstream"
add_rule tcp 853 "AdGuard bridge DoT upstream"

echo "Applied routed DNS UFW rules for $SRC_SUBNET"
