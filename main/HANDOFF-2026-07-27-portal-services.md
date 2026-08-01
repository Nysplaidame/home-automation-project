---
title: Portal, Monitoring and Household Services Handoff
description: Live Homepage/monitoring state and the next decision-gated service work
created: 2026-07-27
type: handoff
status: current
---

# Handoff — Portal, Monitoring and Household Services (2026-07-27)

## Read first

- Canonical live state: [[docs/reference/current-live-state]]
- Current work list: [[TO-DO]]
- Service rollout design: [[docs/procedures/household-services-implementation-plan]]
- Homepage operating notes: [[docs/install/services/homepage]]

## Live state confirmed this session

### Homepage portal

- Homepage is live over trusted local-CA HTTPS at
  `https://192.168.20.102/`; HTTP `:3001` remains rollback only.
- The fixed-target HTTPS preview proxy provides only named service routes; it is
  not a generic proxy. The embedded workspace is below the active service-card
  grid, closes when the tab changes and has working Reload, Open tab and Close
  controls.
- Home Assistant is previewed through `8188` and requires its own one-time
  login because that proxy is a different browser origin. Services that decline
  framing must keep direct navigation as the fallback.
- The completed preview/navigation audit includes direct paths and embedded
  paths. The remaining visual defect is not mobile-specific: the header,
  navigation and service-card layout needs visual repair at narrow/intermediate
  widths (explicitly include `320`, `350`, `375`, `390`, `430`, `480` px and
  tablet widths).
- Proxmox nested noVNC needs `'self'` in the dedicated preview proxy CSP on
  `8183`; that small exception is intentional and was deployed.

### Monitoring preview recovery

- VM 102 (`192.168.60.10`) now permits only docker-host
  `192.168.20.102` to Grafana `3000/tcp` and Uptime Kuma `3001/tcp`.
- UFW alone is insufficient for Docker-published ports. The matching
  `DOCKER-USER` returns are restored after Docker starts by the enabled
  `monitoring-firewall.service`.
- Canonical source/deployment templates:
  - `configs/monitoring/system/monitoring-firewall.sh` →
    `/usr/local/sbin/monitoring-firewall.sh`
  - `configs/monitoring/system/monitoring-firewall.service` →
    `/etc/systemd/system/monitoring-firewall.service`
- Verification from docker-host on 2026-07-26: Grafana `200`, Uptime Kuma
  `302`, proxy Grafana `8202=200`, proxy Kuma `8186=302`.
- A temporary root Proxmox API token was used solely through the guest agent to
  repair this access. It was revoked and its local temporary secret was removed
  after verification. Do not attempt to reuse it.

## Household service rollout state

### Vaultwarden

- Vaultwarden `1.36.0` is live on docker-host with persistent data under
  `/opt/stacks/vaultwarden/data` and explicit network `10.240.30.0/24`.
- Raw HTTP is loopback-only at `127.0.0.1:8222`. The fixed Nginx proxy serves
  `https://vault.home.local` using a dedicated local-CA certificate, HSTS and a
  no-framing policy. Do not add a Homepage iframe.
- Sign-ups and the admin endpoint remain disabled. A clean production backup
  and a stronger disposable-account backup both restored successfully into
  isolated temporary containers; SQLite integrity, exact account count and HTTP
  health passed, and all temporary data/networks were removed.
- Live OpenWrt DNS for `vault.home.local` is still pending. After DNS is live,
  create the owner account during a tightly bounded sign-up window, disable
  sign-up immediately and complete 2FA/recovery/emergency-access policy before
  importing real credentials.

### Media

- OMV now exports the populated 14 TB media tree only to docker-host, mounted at
  `/mnt/omv/media`. The dedicated `media-service` identity (`1007:100`) passed
  create/read/delete proof in the isolated new roots; legacy media was untouched.
- Jellyfin `10.11.11` is live on `8096` with read-only film/series/music and
  `immich-curated` mounts. Hardware transcoding remains disabled because Frigate
  and CT 114 already share the iGPU.
- Calibre-Web is live on `8083` with only its Calibre library writable. Atsumeru
  is live on `31337` with only its comics library writable. Both passed scoped
  write/delete, HTTP and restart checks; their local app state is in the NAS
  backup job.
- Immich remains the photo system of record. The allow-listed exporter into
  `jellyfin/immich-curated/`, manifest and review queue are not yet built; never
  mount Immich's live library directly into Jellyfin.
- The first Jellyfin network overlapped management (`192.168.0.0/20`) and was
  stopped immediately. All new stacks now use explicit non-overlapping IPAM:
  media `10.240.10.0/24`-`10.240.12.0/24`, downloads `10.240.20.0/24`, and
  Vaultwarden `10.240.30.0/24`.

### Download automation

- The Gluetun/Mullvad + qBittorrent Compose stack is live. The generated
  WireGuard private key/address exist only in the mode-`0600` live `.env`;
  temporary import copies were removed. OpenWrt's host-specific `Docker Host VPN
  Egress` rule permits `443`, `3478`, `41641` and UDP `51820` without opening
  general automation-zone internet access.
- qBittorrent shares Gluetun's network namespace. Mullvad recognized its route
  and the address differed from the host. Dropping `tun0` blocked qBittorrent
  public egress while its local Web UI and host egress stayed up; Gluetun then
  recovered automatically. A full provider stop also failed closed while host
  and unrelated-container egress continued. After a manual full provider
  stop/start, run `docker compose up -d --force-recreate qbittorrent` so it
  attaches to the restored namespace.
- The Web UI is live on `8084`; UFW and `DOCKER-USER` allow only management,
  monitoring and Tailscale. Its permanent credential is in Windows Credential
  Manager as `home-automation/qbittorrent` and is not in git. NAS backup run
  `20260801T144643Z` passed an isolated restore proof for the credential hash
  and both persisted download paths.
- All payload storage is on the OMV media export mounted at
  `/mnt/omv/media` on docker-host, not VM 103's local disk. Storage flow:
  `/mnt/omv/media/incoming/qbittorrent/incomplete` →
  `/mnt/omv/media/incoming/qbittorrent/complete` →
  `/mnt/omv/media/quarantine` → manually approved destination by content type.
  qBittorrent never writes final libraries, document shares or backup paths.
- Autobrr is optional and only follows a proven qBittorrent path. It listens to
  authorised indexer announcements/feeds, filters them and sends allowed matches
  to a dedicated qBittorrent category; it is not a downloader or library mover.
- NZBGet remains conditional on a chosen Usenet provider and policy. aria2 is a
  separate authenticated direct-download utility, not a media manager. No Arr
  application is in scope yet.

### Reboot recovery

- A VM 103 reboot exposed an AdGuard/Tailscale address race. The enabled
  `adguard-home-compose.service` waits for `100.94.122.18` on `tailscale0`, then
  force-recreates the stack so stale half-created containers are repaired.
  Local/Tailscale DNS listeners and the UI were revalidated after installation.

### OMV share-layout investigation and resolution (2026-07-27 to 2026-07-29)

- Windows share mapping confirms the intended live data roots are `Z:\Media`
  (the populated 14 TB media tree) and `Y:\Print` (the populated NAS print
  tree). The inverse roots `Y:\Media` (empty) and `Z:\Print` (an empty
  directory skeleton) were confirmed as stray. Both inverse roots have now
  been removed without changing either canonical data tree.
- Transfer Portal has no scheduler and currently records no active job. Its
  historical `test` portal has one confirmed actual copy (job 8, 2026-06-25)
  plus preview-only jobs. The live bind units point from the *inverse* roots
  (`14 TB/Print/Cases` to `NAS/Media`), not the canonical data roots. Retained
  logs and journal records contain no historical root-level Media/Print
  mapping. This portal is therefore not evidence for the original creation of
  either inverse root, but it is misconfigured and a future write risk.
- Directory metadata shows the stray `14 TB/Print` was created on 2026-06-20
  while retaining an older directory modification time, a pattern consistent
  with a historical recursive directory copy. The stray `NAS/Media` was
  created on 2026-07-12. The responsible process has not yet been identified.
- A read-only host configuration sweep found no Docker mount, Compose file,
  cron entry or systemd task referencing either inverse root. The only matching
  units are the expected Transfer Portal bind mounts for `Print/Cases` and
  `Media`; they do not reference `Y:\Media` or `Z:\Print`.
- OMV's shared-folder configuration defines only the `NAS` and `14tb` disk-root
  shares (plus HA/Frigate/Immich/config subshares on NAS); neither inverse
  Media/Print path is an OMV shared-folder definition. Transfer Portal's
  service sandbox has write paths only for its own app, logs, portal bind mounts
  and unit definitions, not the disk-root paths. Static host evidence is now
  exhausted; the creator was an earlier manual/SMB-client operation or a
  historical process whose logs are no longer retained.
- The misconfigured `test` Transfer Portal mapping was removed through its
  confirmed-delete UI on 2026-07-27. This stopped/disabled and removed its
  bind-mount units and removed the portal entry without deleting either real
  source/destination folder or their contents. Historical job records remain
  as audit evidence; only the disposable `Smoke Test` portal is active.
- The older `srv-transferportal-source.mount` and
  `srv-transferportal-destination.mount` units remain active by design: they
  bind the two whole disk roots into Transfer Portal for legacy browsing and
  the Smoke Test. They do not target either inverse Media/Print folder, so do
  not remove them as a remedy for the stray `14tb/Print` tree without a
  separate decision to retire/rebuild Transfer Portal.
- The OMV File Browser is a Podman container (not Docker), but it mounts only
  the NAS disk root at `/srv`; it has no 14 TB, Print or Transfer Portal mount
  and is ruled out as a creator of `14tb/Print`.
- The apparent re-creation of `14tb/Print` subfolders was an SMB/Windows view
  problem, not a live creator. Linux has OMV WebGUI `admin` at UID 996 and a
  storage user `Admin` at UID 1000, while Samba collapsed both case-only names
  into one passdb entry bound to UID 996. A distinct `nasadmin` account (UID
  1006, groups `users` and `sambashare`) now has read/write privileges on the
  `NAS` and `14tb` shares. The 14 TB root ACL also needed explicit access and
  default entries for `nasadmin`: its extended ACL gave the base `users` group
  only `r-x` even though `stat` presented mode `2775`. A direct local
  create/remove test and a Windows UNC create/remove test both passed after the
  ACL correction. The empty `14tb/Print` directory skeleton was then removed
  with an empty-directory-only operation. Explorer continued to display a
  stale directory handle until both SMB mappings were disconnected and
  remounted; the physical path remained absent, confirming there is no active
  recreation process. A final `nasadmin` write/delete test also passed on the
  `NAS` share. The obsolete uppercase `Admin` share privileges and temporary
  audit watches have been removed; the Linux UID 1000 account itself remains
  untouched pending any future ownership audit.

## Next safe work

1. Deploy live `vault.home.local` DNS, then complete the bounded Vaultwarden
   owner onboarding/2FA/recovery process before importing real credentials.
2. Implement the allow-listed Immich curated-album exporter.
3. Evaluate one tightly allow-listed Autobrr source/category only if desired;
   NZBGet and aria2 remain separate decisions.
4. Continue weekly update review; the 2026-08-01 docker-host package window is
   complete and did not require a reboot.

## Repository state

- Branch: `codex/portal-refinement`
- Recent relevant commits:
  - `358bb17 docs(services): define household rollout gates`
  - `03a8213 fix(monitoring): restore portal health checks`
  - `9083c24 feat(homepage): add trusted HTTPS previews`
- User-owned Obsidian changes may be present under `.obsidian/`; do not stage or
  overwrite them during project work.
