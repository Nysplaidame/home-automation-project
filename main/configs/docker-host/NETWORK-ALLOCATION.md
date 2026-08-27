# Docker-host network allocation

Every bridge network is explicitly allocated. Docker automatic address pools
must never be used on VM 103: they have already selected `192.168.0.0/20`,
which overlaps the management VLAN and breaks return routing.

| Network | CIDR | Owner |
|---|---|---|
| `homepage` | `10.240.1.0/24` | Homepage dashboard |
| `adguard-home` | `10.240.2.0/24` | AdGuard Home |
| `dozzle` | `10.240.3.0/24` | Dozzle |
| `immich` | `10.240.4.0/24` | Immich |
| `mealie` | `10.240.5.0/24` | Mealie |
| `grocy` | `10.240.6.0/24` | Grocy |
| `obsidian-livesync` | `10.240.7.0/24` | CouchDB / LiveSync |
| `searxng` | `10.240.8.0/24` | SearXNG |
| `whoogle` | `10.240.9.0/24` | Whoogle |
| `jellyfin` | `10.240.10.0/24` | Jellyfin |
| `calibre-web` | `10.240.11.0/24` | Calibre-Web |
| `atsumeru` | `10.240.12.0/24` | Atsumeru |
| `mermaid-viewer` | `10.240.13.0/24` | Mermaid Viewer |
| `household-hub` | `10.240.14.0/24` | Household Hub |
| `local-alerting` | `10.240.15.0/24` | ntfy shared network |
| `mediamtx` | `10.240.16.0/24` | MediaMTX phone stream relay/recorder |
| `download-gateway` | `10.240.20.0/24` | Gluetun/qBittorrent |
| `gardenkeeper` | `10.240.21.0/24` | GardenKeeper |
| `docker-host-telegraf` | `10.240.22.0/24` | Telegraf |
| `bambuddy` | `10.240.23.0/24` | Bambuddy |
| `gridfinity-layout-tool` | `172.32.0.0/24` | Gridfinity (already explicit) |
| `vaultwarden` | `10.240.30.0/24` | Vaultwarden |
| `recomp-tracker` | `10.240.31.0/24` | Recomp Tracker |
| `troubleshooting-dashboard` | `10.240.32.0/24` | Troubleshooting Dashboard; staged live, management-only acceptance path |

## Change rules

- Create or recreate a stack only from its tracked Compose file after
  `docker compose config --quiet` passes.
- Use a Compose network key that matches the explicit network `name`. Docker
  Compose 5.3.1 rejects a pre-created network when its
  `com.docker.compose.network` label was produced by a differently named key
  such as `default`.
- A network CIDR cannot be changed in place. Stop only the owning stack,
  confirm its data is persisted outside the network, remove its now-unused
  network, then recreate the stack and verify the CIDR with `docker network
  inspect`.
- `local-alerting` is shared. Stop every connected workload before recreating
  it, and start `ntfy` first because it owns the network definition.
- Before a planned reallocation, run `docker network ls` and inspect every
  existing network. Stop if any non-project network uses a `10.240.0.0/16`
  range or overlaps a proposed CIDR.

All external access control still belongs in `DOCKER-USER` or UFW; selecting a
non-overlapping bridge range is a routing safeguard, not a security boundary.
