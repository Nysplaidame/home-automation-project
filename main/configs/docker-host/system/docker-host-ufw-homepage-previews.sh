#!/bin/sh
set -eu

# Keep fixed-target Homepage preview listeners reachable only from approved
# client networks. The bridge exception is narrower: it exposes only Proxmox's
# internal HTTP health endpoint to Homepage's own Compose network.

UFW_BIN="${UFW_BIN:-/usr/sbin/ufw}"
HOMEPAGE_BRIDGE_SUBNET="${HOMEPAGE_BRIDGE_SUBNET:-10.240.1.0/24}"
HOMEPAGE_BRIDGE_GATEWAY="${HOMEPAGE_BRIDGE_GATEWAY:-10.240.1.1}"

if ! command -v "$UFW_BIN" >/dev/null 2>&1; then
    echo "ERROR: ufw binary not found at $UFW_BIN" >&2
    exit 1
fi

# Remove the superseded HTTP-only range and old bridge health exception before
# adding the HTTPS listeners. These deletes are intentionally idempotent.
"$UFW_BIN" --force delete allow from 192.168.10.0/24 to any port 8180:8204 proto tcp >/dev/null 2>&1 || true
"$UFW_BIN" --force delete allow from 192.168.1.0/24 to any port 8180:8204 proto tcp >/dev/null 2>&1 || true
"$UFW_BIN" --force delete allow from 192.168.20.0/24 to any port 8180:8204 proto tcp >/dev/null 2>&1 || true
"$UFW_BIN" --force delete allow in on tailscale0 to any port 8180:8204 proto tcp >/dev/null 2>&1 || true
"$UFW_BIN" --force delete allow from 192.168.10.0/24 to any port 8180:8207 proto tcp >/dev/null 2>&1 || true
"$UFW_BIN" --force delete allow from 192.168.1.0/24 to any port 8180:8207 proto tcp >/dev/null 2>&1 || true
"$UFW_BIN" --force delete allow from 192.168.20.0/24 to any port 8180:8207 proto tcp >/dev/null 2>&1 || true
"$UFW_BIN" --force delete allow in on tailscale0 to any port 8180:8207 proto tcp >/dev/null 2>&1 || true
"$UFW_BIN" --force delete allow from 192.168.10.0/24 to any port 8180:8187 proto tcp >/dev/null 2>&1 || true
"$UFW_BIN" --force delete allow from 192.168.1.0/24 to any port 8180:8187 proto tcp >/dev/null 2>&1 || true
"$UFW_BIN" --force delete allow from 192.168.20.0/24 to any port 8180:8187 proto tcp >/dev/null 2>&1 || true
"$UFW_BIN" --force delete allow in on tailscale0 to any port 8180:8187 proto tcp >/dev/null 2>&1 || true
"$UFW_BIN" --force delete allow from "$HOMEPAGE_BRIDGE_SUBNET" to "$HOMEPAGE_BRIDGE_GATEWAY" port 8183 proto tcp >/dev/null 2>&1 || true

"$UFW_BIN" allow from 192.168.10.0/24 to any port 443 proto tcp comment "Management to Homepage HTTPS" >/dev/null
"$UFW_BIN" allow from 192.168.1.0/24 to any port 443 proto tcp comment "LAN to Homepage HTTPS" >/dev/null
"$UFW_BIN" allow from 192.168.20.0/24 to any port 443 proto tcp comment "Automation to Homepage HTTPS" >/dev/null
"$UFW_BIN" allow in on tailscale0 to any port 443 proto tcp comment "Tailscale Homepage HTTPS" >/dev/null
"$UFW_BIN" allow from 192.168.10.0/24 to any port 8180:8208 proto tcp comment "Management to Homepage previews" >/dev/null
"$UFW_BIN" allow from 192.168.1.0/24 to any port 8180:8208 proto tcp comment "LAN to Homepage previews" >/dev/null
"$UFW_BIN" allow from 192.168.20.0/24 to any port 8180:8208 proto tcp comment "Automation to Homepage previews" >/dev/null
"$UFW_BIN" allow in on tailscale0 to any port 8180:8208 proto tcp comment "Tailscale Homepage previews" >/dev/null
"$UFW_BIN" allow from "$HOMEPAGE_BRIDGE_SUBNET" to "$HOMEPAGE_BRIDGE_GATEWAY" port 8299 proto tcp comment "Homepage Proxmox status" >/dev/null

echo "Applied Homepage preview UFW rules"
