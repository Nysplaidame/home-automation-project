---
title: Household Services Implementation Plan
description: Decision-gated design for Vaultwarden, media libraries, and authorised-download automation
tags: [planning, vaultwarden, media, jellyfin, downloads, autobrr]
created: 2026-07-26
type: implementation-plan
status: approved-design-pending-implementation
---

# Household Services Implementation Plan

This plan defines the intended implementation order and acceptance gates for
three new household-service areas. Nothing in this document authorises a live
deployment, account creation, tracker use, VPN subscription, Usenet provider,
or media acquisition. Deploy one bounded phase at a time and retain a working
Homepage and backup path throughout.

## Shared operating rules

- Run application containers on `docker-host` (VM 103), not OMV. OMV remains
  the storage appliance and NFS provider.
- Keep container configuration and databases local under `/opt/stacks/<app>`.
  Store bulk libraries on explicit OMV exports mounted on docker-host.
- Add only fixed HTTPS virtual hosts to the existing docker-host TLS proxy; do
  not create a generic proxy or dynamic target feature.
- Add OpenWrt, UFW and `DOCKER-USER` rules only for named ports, sources and
  destinations. Every new UI receives an Uptime Kuma monitor and Homepage card
  after its direct path has passed authentication and backup tests.
- Never commit passwords, API tokens, VPN credentials, tracker credentials,
  Usenet credentials, recovery codes or private keys.

## 1. Password manager — Vaultwarden

### Chosen design

Deploy Vaultwarden on docker-host with its persistent `/data` volume at
`/opt/stacks/vaultwarden/data`. It will be available only through a dedicated
local-CA HTTPS name such as `vault.home.local`, routed as a fixed virtual host
by the existing TLS proxy to a loopback/private Docker port. Do not expose the
container's HTTP port directly, publish it to the WAN, or include an embedded
Homepage preview. The official web vault needs HTTPS/secure-context browser
features; Vaultwarden itself recommends a reverse proxy. [Vaultwarden
documentation](https://github.com/dani-garcia/vaultwarden)

Use SQLite initially: the expected household scale does not justify a separate
database service, while the complete `/data` directory remains a small,
restorable unit. Disable public sign-ups. Keep the administrative endpoint
disabled unless it is needed for a short, documented maintenance task; when
enabled, use a separately stored, hashed admin token and remove the exposure
afterwards.

### Identity, recovery and access policy

- Create named household accounts; do not share a master password or an admin
  account.
- Require strong unique master passwords and enable 2FA before migrating any
  high-value credentials. Store recovery codes outside the vault, in a sealed
  offline location controlled by the owner.
- Define one owner-controlled emergency-contact policy with a deliberate wait
  period. Test it with a non-production account before relying on it.
- Keep remote use on Tailscale or trusted local networks. Do not make the vault
  Internet-facing merely to simplify mobile access.

### Backup and restore contract

The backup job creates a SQLite-consistent backup using Vaultwarden's supported
backup operation, copies that result plus attachments, sends and keys from
`/data` to the existing OMV `backups/docker-host` hierarchy, and retains dated
generations. A raw live SQLite file copy alone is not an accepted backup.

Before importing real secrets, prove a restore into an isolated temporary stack:

1. restore the data set under a different container name and hostname;
2. sign in with a test account and verify an attachment, an encrypted note,
   a Send item and a 2FA-protected login;
3. confirm the production vault has not been touched; and
4. record the tested backup generation and recovery time.

### Deployment gates and acceptance

1. Create local DNS and local-CA certificate coverage for the chosen dedicated
   hostname; validate desktop and mobile trust.
2. Add fixed proxy, OpenWrt and host-firewall rules for HTTPS only; deny the
   raw container port outside Docker.
3. Deploy with sign-ups disabled, a non-secret `.env` template, and the secrets
   stored outside Git.
4. Complete the restore proof and household 2FA/recovery setup.
5. Add direct Homepage navigation, Uptime Kuma HTTPS monitoring and a backup
   health check. Do not add an iframe preview.

## 2. Media library — Jellyfin, Calibre-Web and Atsumeru

### Storage layout and ownership

Create a dedicated OMV media export, mounted on docker-host at
`/mnt/omv/media`, with this logical layout:

```text
media/
  jellyfin/
    films/
    series/
    music/
    immich-curated/
  books/
    calibre-library/
  comics/
    atsumeru-library/
  incoming/
  quarantine/
```

Use a dedicated service group/GID consistently on OMV and docker-host. Jellyfin
gets read-only mounts for its published libraries; Calibre-Web and Atsumeru get
write access only to their own library roots. Database, configuration, cache and
metadata live under their respective `/opt/stacks` paths and join the existing
docker-host app-data backup job. Library content is backed up according to its
source-of-truth status, not blindly duplicated.

### Immich-to-Jellyfin curation

Immich albums are application metadata, not filesystem directories. Therefore
Jellyfin must not scan Immich's live upload/library tree as if albums were
folders. Instead, a small scheduled exporter runs with an Immich API account
limited to selected shared albums and asset download access. The exporter:

1. maps allow-listed Immich album IDs to named Jellyfin collections;
2. downloads only approved image/video assets to
   `media/jellyfin/immich-curated/<collection>/`;
3. maintains a manifest containing Immich asset ID, checksum/version, target
   path and export time;
4. writes to a temporary path then atomically promotes completed files; and
5. treats deletion as a review queue at first, not an automatic source of media
   deletion.

This is intentionally a copy/export workflow, not a two-way sync. It preserves
Immich as the photo system of record and gives Jellyfin stable, read-only media
paths. Immich exposes download information for permitted album/assets through
its API. [Immich API reference](https://api.immich.app/endpoints/download/getDownloadInfo)

### Jellyfin operation

Start without hardware transcoding. Enable Intel Quick Sync only after a
separate capacity and shared-iGPU allocation review, because Frigate and CT 114
already use the host iGPU. Jellyfin libraries point only at approved media roots;
never at `incoming`, `quarantine`, Immich's live upload directories or backup
folders. Preserve original files and use metadata/download artwork caches as
rebuildable data.

### Books and comics

Calibre-Web is the household book front end for `books/calibre-library`; it is
the only application allowed to edit Calibre metadata. Atsumeru serves
`comics/atsumeru-library`; its scanner/indexer may write only its own metadata
paths. Ingest new books/comics through Transfer Portal or a reviewed staging
folder, then move them into the appropriate library with the service account.
Neither app receives broad write access to `media/`.

### Deployment gates and acceptance

1. Create OMV export, NFS mount, service group and a test write/read/delete
   proof from docker-host before containers exist.
2. Deploy Jellyfin with a read-only test library and local config/database
   backup. Validate a browser and mobile-client direct HTTPS login.
3. Create the exporter with a test album and manifest; prove that a removal from
   an Immich album does not delete the original or published copy automatically.
4. Deploy Calibre-Web then Atsumeru independently, each with a sample library,
   metadata-backup proof and least-privilege mount.
5. Add Homepage Media cards, direct links, Uptime Kuma monitors and only
   non-secret widgets supported by each application.

## 3. Authorised download automation — qBittorrent, NZBGet, aria2 and Autobrr

### Chosen baseline

qBittorrent is the first and only proposed downloader. Run it behind a dedicated
VPN gateway container with a kill switch: qBittorrent shares the gateway's
network namespace and has no direct Docker/WAN egress path. The Web UI is
published only through a fixed local-CA HTTPS host and the existing source-
scoped firewall model. A VPN provider supporting the required protocol and, if
needed, port forwarding must be selected and tested before enabling any torrent
workflow.

Use `media/incoming/qbittorrent/{incomplete,complete}` for temporary payloads.
Completed items enter `quarantine/` for manual/legal review before any curated
move into a Jellyfin library. Do not grant qBittorrent write access to the final
libraries. The plan is restricted to material the household is authorised to
download, share or redistribute.

### Autobrr's role

Autobrr is optional and comes after qBittorrent is proven. It is not a download
client: it receives authorised indexer IRC/RSS/Torznab/Newznab announcements,
filters them and sends approved matches to a configured client. It supports
qBittorrent and can send notifications including ntfy. [Autobrr
documentation](https://autobrr.com/)

If adopted, it gets its own config directory and non-secret Compose template;
tracker credentials stay in a protected runtime secret. Initial rules must be
allow-list based, use a dedicated `autobrr` qBittorrent category/save path,
require a size ceiling and emit an ntfy message. No broad regex or automatic
library import is permitted in the first phase.

### Deferred components

- **NZBGet:** deploy only after a specific Usenet provider, retention policy,
  account secret, category mapping and firewall/egress design are approved.
- **aria2:** optional direct-download utility only. Keep it separate from media
  automation and restrict RPC to authenticated local access; do not make it the
  library manager.
- **Arr applications:** not part of this plan. Revisit only after manual
  quarantine and categorisation are reliable.

### Deployment gates and acceptance

1. Choose and document the VPN provider, protocol, credential storage and
   expected port-forward behaviour; make no torrent connection before this.
2. Build the gateway/qBittorrent Compose stack with a kill-switch test: remove
   the tunnel and prove qBittorrent has no Internet route while its Web UI stays
   local-only.
3. Prove the storage permissions and quarantine boundary using a legal test
   payload. Confirm incomplete files cannot appear in Jellyfin.
4. Add Uptime Kuma checks for the Web UI and VPN gateway, plus an ntfy alert for
   tunnel failure or a blocked downloader.
5. Only then evaluate Autobrr against one authorised source and one explicit
   category. Revert by disabling its filter/client integration; do not delete
   completed files as part of rollback.

## Recommended implementation order

1. Vaultwarden design-gate review, dedicated HTTPS host and backup/restore proof.
2. OMV media export and Jellyfin read-only test library.
3. Immich curated-export proof, then Calibre-Web and Atsumeru.
4. VPN gateway and qBittorrent containment proof.
5. Autobrr evaluation; NZBGet and aria2 remain separate decisions.
