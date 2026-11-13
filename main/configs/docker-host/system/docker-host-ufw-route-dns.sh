#!/bin/sh
set -eu

# Reapply routed DNS allowances required for AdGuard's Docker bridge subnet
# when UFW uses "default deny routed" on docker-host.

UFW_BIN="${UFW_BIN:-/usr/sbin/ufw}"
SRC_SUBNET="${SRC_SUBNET:-10.240.2.0/24}"
LEGACY_SRC_SUBNET="${LEGACY_SRC_SUBNET:-172.20.0.0/16}"
PRUNE_LEGACY="${PRUNE_LEGACY:-0}"

if ! command -v "$UFW_BIN" >/dev/null 2>&1; then
    echo "ERROR: ufw binary not found at $UFW_BIN" >&2
    exit 1
fi

add_rule() {
    proto="$1"
    port="$2"
    comment="$3"
    # Do not pin to a bridge interface name; Compose bridge names vary
    # (for example br-<hash>) and docker0 may be down/unused.
    "$UFW_BIN" route allow from "$SRC_SUBNET" to any port "$port" proto "$proto" comment "$comment" >/dev/null
}

# Idempotence relies on UFW de-duplicating equivalent rules.
add_rule udp 53 "AdGuard container upstream DNS UDP"
add_rule tcp 53 "AdGuard container upstream DNS TCP"
add_rule tcp 853 "AdGuard container upstream DoT"

if [ "$PRUNE_LEGACY" = "1" ]; then
    for rule in "udp 53" "tcp 53" "tcp 853"; do
        set -- $rule
        "$UFW_BIN" --force route delete allow from "$LEGACY_SRC_SUBNET" to any port "$2" proto "$1" >/dev/null 2>&1 || true
    done
fi

echo "Applied routed DNS UFW rules for $SRC_SUBNET"
