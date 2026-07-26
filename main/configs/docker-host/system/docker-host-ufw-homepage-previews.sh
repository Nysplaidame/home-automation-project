#!/bin/sh
set -eu

# Keep fixed-target Homepage preview listeners reachable only from approved
# client networks. The bridge exception is narrower: it exposes only Proxmox's
# local proxy endpoint to Homepage's own Compose network for server-side health.

UFW_BIN="${UFW_BIN:-/usr/sbin/ufw}"
HOMEPAGE_BRIDGE_SUBNET="${HOMEPAGE_BRIDGE_SUBNET:-172.18.0.0/16}"
HOMEPAGE_BRIDGE_GATEWAY="${HOMEPAGE_BRIDGE_GATEWAY:-172.18.0.1}"

if ! command -v "$UFW_BIN" >/dev/null 2>&1; then
    echo "ERROR: ufw binary not found at $UFW_BIN" >&2
    exit 1
fi

"$UFW_BIN" allow from 192.168.10.0/24 to any port 8180:8187 proto tcp comment "Management to Homepage previews" >/dev/null
"$UFW_BIN" allow from 192.168.1.0/24 to any port 8180:8187 proto tcp comment "LAN to Homepage previews" >/dev/null
"$UFW_BIN" allow from 192.168.20.0/24 to any port 8180:8187 proto tcp comment "Automation to Homepage previews" >/dev/null
"$UFW_BIN" allow in on tailscale0 to any port 8180:8187 proto tcp comment "Tailscale Homepage previews" >/dev/null
"$UFW_BIN" allow from "$HOMEPAGE_BRIDGE_SUBNET" to "$HOMEPAGE_BRIDGE_GATEWAY" port 8183 proto tcp comment "Homepage Proxmox status" >/dev/null

echo "Applied Homepage preview UFW rules"
