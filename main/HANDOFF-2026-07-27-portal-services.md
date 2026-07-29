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

## Approved designs; nothing deployed yet

The following are designs and decision gates only. No service/container,
credential, VPN subscription, tracker, Usenet provider, media transfer or new
firewall rule has been created for them.

### Vaultwarden

- Target: docker-host, persistent data under `/opt/stacks/vaultwarden/data`.
- Access: a dedicated local-CA HTTPS hostname and fixed proxy route; no raw
  HTTP publishing and no Homepage iframe.
- Before real secrets: source-scoped firewall, sign-ups disabled, 2FA/recovery
  policy, owner-controlled emergency access, and isolated backup/restore proof.
- The previous install manual is now intentionally `planned-not-installable`;
  use the current plan rather than treating its Compose shape as authorisation.

### Media

- Create a dedicated OMV media export mounted at `/mnt/omv/media` on
  docker-host. Jellyfin receives read-only library mounts.
- Immich remains the photo system of record. A future allow-listed exporter
  copies chosen album assets into `jellyfin/immich-curated/` with a manifest and
  review queue; it is not a filesystem album mount or two-way sync.
- Calibre-Web and Atsumeru receive separate least-privilege book/comic roots and
  must each prove metadata/config backup before Homepage is updated.
- Start Jellyfin without iGPU transcoding. Revisit only after capacity review,
  because Frigate and CT 114 already consume shared iGPU resources.

### Download automation

- qBittorrent is the first proposed downloader, behind a dedicated VPN gateway
  container and kill switch. It will have no direct WAN route when the tunnel is
  down.
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
  recreation process.

## Next safe work

1. Repair and visually validate the Homepage narrow/intermediate layout.
2. When authorised, begin Vaultwarden at its HTTPS and backup/restore proof
   gate—do not import real credentials until the isolated restore succeeds.
3. Create and prove the OMV media export before any media container is deployed.
4. Defer docker-host package patching until the user chooses a maintenance
   window.

## Repository state

- Branch: `codex/portal-refinement`
- Recent relevant commits:
  - `358bb17 docs(services): define household rollout gates`
  - `03a8213 fix(monitoring): restore portal health checks`
  - `9083c24 feat(homepage): add trusted HTTPS previews`
- User-owned Obsidian changes may be present under `.obsidian/`; do not stage or
  overwrite them during project work.
