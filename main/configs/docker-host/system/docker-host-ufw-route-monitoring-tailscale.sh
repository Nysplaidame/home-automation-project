#!/usr/bin/env bash
set -euo pipefail

# Allow approved Tailscale clients routed through docker-host to reach only the
# monitoring UIs on VM 102. Keep InfluxDB private unless separately approved.
ufw route allow in on tailscale0 out on eth0 to 192.168.60.10 port 3000 proto tcp comment "Tailscale routed Grafana"
ufw route allow in on tailscale0 out on eth0 to 192.168.60.10 port 3001 proto tcp comment "Tailscale routed Uptime Kuma"

# Allow direct Frigate PWA/mobile UI access through Tailscale without exposing
# the full NVR VLAN or Frigate's internal unauthenticated API on port 5000.
ufw route allow in on tailscale0 out on eth0 to 192.168.30.20 port 8971 proto tcp comment "Tailscale routed Frigate HTTPS"
