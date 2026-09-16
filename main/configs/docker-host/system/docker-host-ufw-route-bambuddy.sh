#!/bin/sh
set -eu

# Permit only Bambuddy's explicit bridge to the Home Assistant services and the
# P1S services it needs. UFW's default deny-routed policy otherwise blocks this
# traffic after host networking is removed.

UFW_BIN="${UFW_BIN:-/usr/sbin/ufw}"
BAMBUDDY_SUBNET="${BAMBUDDY_SUBNET:-10.240.23.0/24}"
HOME_ASSISTANT_IP="${HOME_ASSISTANT_IP:-192.168.20.101}"
P1S_IP="${P1S_IP:-192.168.35.200}"

if ! command -v "$UFW_BIN" >/dev/null 2>&1; then
    echo "ERROR: ufw binary not found at $UFW_BIN" >&2
    exit 1
fi

for port in 8123 8883; do
    "$UFW_BIN" route allow from "$BAMBUDDY_SUBNET" to "$HOME_ASSISTANT_IP" port "$port" proto tcp comment "Bambuddy to Home Assistant" >/dev/null
done
for port in 21 8883; do
    "$UFW_BIN" route allow from "$BAMBUDDY_SUBNET" to "$P1S_IP" port "$port" proto tcp comment "Bambuddy to P1S" >/dev/null
done

echo "Applied routed UFW rules for Bambuddy"
