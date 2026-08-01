---
title: "qBittorrent Download Gateway"
category: entity
tags: [service, docker, qbittorrent, mullvad, gluetun, wireguard, storage]
created: 2026-08-01
updated: 2026-08-01
sources: [project-readme, project-todo]
status: active
---

# qBittorrent Download Gateway

**Type:** service - authorised download staging
**Status:** Live and fail-closed acceptance-proven
**Related:** [[entities/docker-host]], [[entities/openmediavault-nas]], [[entities/gl-mt6000]], [[entities/homepage]]

## Overview

qBittorrent runs on [[entities/docker-host]] behind Gluetun and Mullvad
WireGuard. It shares Gluetun's network namespace, so it has no independent WAN
route. The Web UI is source-scoped on port `8084`; the permanent credential is
kept outside git in Windows Credential Manager.

## Key Properties

- Stack: `/opt/stacks/download-gateway/`
- Docker subnet: `10.240.20.0/24`
- Payload mount: `/mnt/omv/media/incoming/qbittorrent` to `/downloads`
- Incomplete path: `/downloads/incomplete`
- Complete path: `/downloads/complete`
- No mount for quarantine, final media/book libraries, documents, or backups
- Mullvad does not offer port forwarding; no peer-listening host port is exposed
- Router egress is limited to the docker-host-specific VPN rule including UDP
  `51820`

## Acceptance Evidence

- Mullvad recognized the tunnel and its public route differed from the host.
- Dropping Gluetun's `tun0` interface blocked qBittorrent public egress while
  the local Web UI and host egress remained available; recovery was automatic.
- A full Gluetun provider stop also failed closed while the host and an unrelated
  container retained egress.
- NAS backup run `20260801T144643Z` restored the credential hash and both paths
  successfully into an isolated temporary directory.

## Open Questions

- [ ] Decide whether to evaluate one allow-listed Autobrr source and category.
- [ ] Keep NZBGet and aria2 as separate decisions.

## Change Log

- 2026-08-01: Gateway activated, configured, containment-proved and added to
  Homepage after isolated backup/restore proof.
