---
title: Portal, Monitoring and Household Services Handoff
description: Live Homepage/monitoring state and the next decision-gated service work
created: 2026-07-27
modified: 2026-08-25
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
- qBittorrent is the exception to the port-per-service preview pattern. Its
  legacy WebUI assumes that its parent window is qBittorrent, so its preview is
  served same-origin at `https://192.168.20.102/portal-preview/qbittorrent/`.
  The Homepage bridge supplies only the two parent-window hooks that WebUI
  requires. Do not reintroduce a dedicated `:8207` iframe route. Its verified
  permanent credential was reset and stored in Windows Credential Manager at
  `home-automation/qbittorrent`; no password is recorded in this repository.
- ntfy's raw listener on `8085` is HTTP-only and must not be used in a browser:
  the secure LAN UI and advertised base URL are now
  `https://192.168.20.102:8193/`. This is required for the browser
  Notifications API. Tailscale Serve remains the separate mobile endpoint on
  `https://docker-host.tail7012a0.ts.net:8444/`.

### Homepage mobile-card access (2026-08-21)

- All user-facing Homepage cards now navigate to fixed HTTPS proxy routes on
  `homepage.home.local` instead of private `192.168.x.x` URLs; qBittorrent
  remains the fixed same-origin `/portal-preview/qbittorrent/` exception.
- The fixed-target proxy has the new Recomp Tracker route at `8209` and all
  fixed proxy ports `8180`-`8209` are covered by its source-scoped UFW script.
  Nginx configuration validation and each fixed upstream route passed locally.
- Tailscale's live grant allows only OnePlus `100.105.216.6` to docker-host
  `100.94.122.18` on `tcp:8180-8209`, in addition to the existing DNS and
  `tcp:443` access. No broad subnet route was added. On home WiFi with
  Tailscale off, router DNS and the LAN proxy binding preserve the same links.
- Phone-side acceptance passed on mobile data after reconnecting Tailscale and
  opening cards from every Homepage tab.

### Household Hub search authentication repair

- The 2026-08-09 workbench `401` failures were caused by browser authentication
  being kept only in per-tab `sessionStorage`; new tabs and embedded preview
  origins therefore sent no bearer token.
- The production web container now receives the existing API token from the
  live `.env`, expands an Nginx template at container start and attaches the
  bearer credential only on proxied `/api/` requests. The token is not built
  into the image or exposed to browser JavaScript, and the obsolete access-token
  field has been removed from the workbench.
- Live verification passed: the production web build and `nginx -t` succeeded,
  recipe and YouTube searches each returned six candidates, a separate proxy
  contract probe returned `200`, and a direct unauthenticated API request still
  returned `401`.
- The two high-severity frontend npm advisories were cleared by updating only
  the lockfile resolutions for transitive `nanoid` (`3.3.18`) and `postcss`
  (`8.5.26`). The rebuilt image reported zero vulnerabilities and passed health,
  recipe-search and direct-API authentication regression probes.
- Timestamped rollback copies of the five changed live files use the suffix
  `.bak.20260808-search401` under `/opt/stacks/household-hub/`.
- The pre-remediation lockfile is retained as
  `/opt/stacks/household-hub/package-lock.json.bak.20260809-npm-audit`.
- Recipe review now creates a persisted UUID workflow record containing the
  candidate and search provenance. Mealie import requires the confirmation UUID
  and matching source URL, rejects duplicate/in-progress calls, and records
  imported or retryable failed state. The workbench gates both search candidates
  and assistant-extracted drafts behind an explicit review step.
- Alembic revision `20260809_0002` added `recipe_workflows`. Ruff, 59 backend
  tests, production builds, SQLite and disposable-PostgreSQL migration round
  trips, live health/search/auth checks, and desktop/mobile browser verification
  passed. No production Mealie import was executed; the live workflow table
  remained empty after verification.
- The protected pre-migration database dump is
  `/opt/backups/household-hub/pre-recipe-workflow-20260809.sql.gz`; live source
  rollback copies use `.bak.20260809-recipe-workflow`.

### Household Hub household integrations

- Grocy is live in Household Hub through a bounded read-only overview of
  locations, stock/expiry and unchecked shopping-list items. It uses a distinct
  `household-hub-read-only` API key stored only on docker-host; the client has no
  write methods or mutation routes. The first live read returned all five seeded
  locations with stock and shopping lists currently empty.
- A Grocy database checkpoint exists at
  `/opt/stacks/grocy/config/data/grocy.db.pre-household-hub-20260809`. Household
  Hub source/config rollback copies use `.bak.20260809-household-integrations`.
- Obsidian recipe Markdown export is configured to the persistent staging outbox
  `/opt/stacks/household-hub/data/obsidian-exports`. It deliberately does not
  manipulate LiveSync's CouchDB. The deployment smoke wrote valid Markdown and
  removed the exact disposable test note afterward. Subsequent hardening made a
  matching persisted recipe confirmation UUID mandatory at the API boundary;
  an unconfirmed live probe returned `404` without creating a file.
- Nextcloud remains absent from the live workload and has no CalDAV credential.
  Calendar task/event dry-runs remain standards-compliant and can now be
  downloaded as `.ics` from the workbench.
- Verification passed 62 backend tests, changed-code Ruff checks, production
  builds, live API probes, desktop interaction and 390 px responsive checks.
  A pre-existing dark-on-dark button theme override was fixed; the final browser
  console reported no warnings or errors.
- The NAS app-data backup source now includes `household-hub-exports`; dry-run
  validation and real run `20260809T130054Z` succeeded, capturing the Grocy key
  state and creating the latest outbox backup directory.

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
- New follow-up (2026-08-02): server-side inspection proved the 14 TB root
  really contains two distinct physical directories: canonical populated
  `Media` (inode `196345857`, created 2026-06-19) and a separate `media`
  wrapper (inode `369688577`, created 2026-07-29 14:22) containing only an
  empty-looking `media/Media` child. The canonical directory contains all
  existing libraries and staging roots; neither root path is a mount point.
  Windows SMB enumerates both names but case-insensitive lookup opens either
  spelling as the canonical `Media` object, causing the intermittent Explorer
  unavailable/disappearing-child behaviour. The NFS configuration is correct:
  `/export/media` is the active bind mount of `14tb/Media` and is the only
  exported media path; `/etc/fstab`, `/etc/exports` and active mount units have
  no reference to the stray lowercase wrapper. It is therefore not used by the
  media services or download pipeline. The remaining action is a separately
  approved, reversible recovery of the unused `14tb/media` wrapper; do not
  delete or rename it until that plan and rollback path are agreed.
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

## Docker-host network recovery (2026-08-10)

- `recomp-tracker` was initially deployed with Docker's automatic
  `192.168.0.0/20` bridge at 20:25 BST. That range includes the management
  subnet, so replies to the operator workstation `192.168.10.116` used the
  Docker bridge instead of VM 103's normal VLAN 20 gateway. SSH and every
  docker-host published service then timed out from management.
- The service was stopped and recreated with explicit default IPAM
  `10.240.31.0/24`. The tracker data bind mount was retained. Post-repair,
  `ip route get 192.168.10.116` returned via `192.168.20.1 dev eth0 src
  192.168.20.102`; workstation checks confirmed TCP reachability on SSH 22,
  Homepage HTTPS 443, qBittorrent 8084 and Recomp Tracker 8420.
- The tracked Compose template now has the same explicit subnet. Preserve this
  policy for every new docker-host Compose network; never rely on Docker's
  automatic address-pool selection.

## Docker-host network/firewall remediation (started 2026-08-21)

- The required live preflight captured every Docker bridge, attached container,
  running image ID/digest, route, UFW rule, IPv4/IPv6 `DOCKER-USER` rule and
  firewall persistence unit. No non-project network occupied `10.240.0.0/16`.
- The persistent firewall now includes the missing IPv6 port-`8000` drop, the
  Bambuddy routed-UFW rules are installed, and the security audit covers that
  denial path. The allocation map now also assigns Mermaid Viewer
  `10.240.13.0/24` and Household Hub `10.240.14.0/24`.
- Every project bridge now exists at its canonical explicit allocation and
  network name. This includes the coordinated Household Hub/SearXNG/Mealie/
  Grocy cutover, the four-consumer `local-alerting` recreation, the media and
  download networks, and the previously omitted Mermaid Viewer and Household
  Hub allocations. Bambuddy's `.23` bridge is prepared but has no consumer yet.
- Service health, 20 HTTP/API checks, authenticated CouchDB `_up`, Nginx
  validation, monitoring-VLAN DNS resolution, internal Household Hub and ntfy
  dependency connections, VPN/host egress separation, persisted data mounts,
  Compose parsing, firewall reload and unit persistence all passed. No
  container remained exited, unhealthy or starting. An unapproved container
  was denied direct access to Recomp while the management path returned `200`.
- Immich remained on v2.7.5 during its network-only recreation; staged v3.1.0
  images were deliberately not deployed. A protected pre-change PostgreSQL
  dump was captured. Fresh Household Hub and GardenKeeper database dumps plus
  NAS app-data backup run `20260821T095807Z` also completed before their
  coordinated changes.
- Bambuddy's bridge candidate passed health, UI and Home Assistant connections,
  but the P1S ports were unreachable from both the candidate bridge and VM 103
  itself. Its rollback completed and the original host-network container is
  healthy. Retry only when the printer/VLAN path is reachable.
- Each changed live Compose file has a timestamped rollback copy beside it;
  Bambuddy also has a protected pre-change `data`/`logs` archive under
  `/opt/backups/network-remediation-20260821/`.
- The live security audit passes every network and firewall assertion except
  the deliberate Bambuddy bridge-attachment check. Do not mark the parent task
  complete until the P1S path is reachable, Bambuddy is moved from host mode,
  and the audit exits zero.

## Next safe work

1. Restore or power the P1S/VLAN-35 path, confirm ports `21` and `8883` are
   reachable from VM 103, then retry the prepared Bambuddy migration to
   `10.240.23.0/24`. Re-run `docker-host-security-audit.sh --verify`; this is
   the only remaining assertion before the network/firewall remediation can be
   marked complete.
2. Review and promote the completed read-only troubleshooting-dashboard POC.
   Approve its wording and exposure, then deploy staged port `8094` only after
   DNS/Homepage and operator-acceptance decisions. Arbitrary shell and
   automatic remediation remain excluded.
3. Deploy live `vault.home.local` DNS, then complete the bounded Vaultwarden
   owner onboarding/2FA/recovery process before importing real credentials.
4. Implement the allow-listed Immich curated-album exporter.
5. Evaluate one tightly allow-listed Autobrr source/category only if desired;
   NZBGet and aria2 remain separate decisions.
6. Continue weekly update review; the 2026-08-01 docker-host package window is
   complete and did not require a reboot.

## Architecture documentation reconciliation (2026-08-25)

- Reconciled the canonical current-state, service, access, naming and physical
  cabling references against tracked configuration and the accepted 2026-08-21
  deployment evidence. Corrected the obsolete one-camera and direct-router-NAS
  representations, the missing Frigate Tailscale route, the fixed Homepage
  proxy range, the deployed docker-host application set and the Bambuddy
  host-network exception.
- Updated the active troubleshooting, monitoring, Homepage, router testing,
  Raspberry Pi, OMV cutover, Docker-host and related setup material for HA
  native HTTPS, three live cameras, OMV on GS1900 port 8, fixed mobile portal
  routes and explicit Compose networks. Historical audits and superseded
  handoffs were retained as dated evidence rather than rewritten.
- Updated all affected canonical Mermaid diagrams and rebuilt the Mermaid
  Viewer's generated data. A browser-side parse passed all 11 diagram sources.
- Corrected the Windows `health_check.ps1` local-CA handling. The POC extension
  adds dashboard-compatible JSON plus Homepage HTTPS and Camera 1 RTSP; its
  full run now passes all 13 checks.
- Live SSH inventory of VM 103 could not be repeated from this workstation
  because root public-key authentication was denied. The latest accepted live
  container/network inventory therefore remains the 2026-08-21 remediation
  evidence; no unverified live version or container claim was added.

## Troubleshooting dashboard POC (2026-08-25)

- Added `apps/troubleshooting-dashboard/`, a dependency-free static interface
  for Homepage access, Home Assistant availability, Camera 1, P1S telemetry
  and backup freshness.
- The browser imports `health_check.sh --json` or Windows
  `health_check.ps1 -Full -Json` locally. It does not probe the network, upload
  evidence, execute commands or expose automatic remediation.
- Each symptom maps health signals onto a dependency path, presents an ordered
  read-only evidence sequence, links canonical runbooks and can copy a
  credential-free incident report. Missing checks remain `Needs evidence`.
- Nine model tests, Compose validation, WSL `bash -n`, a live 13/13 Windows JSON
  collection and Playwright desktop/mobile smoke checks passed. The staged
  Compose definition reserves `10.240.32.0/24` and port `8094`, but no live
  deployment, DNS entry or Homepage card has been approved.
- The promotion review now names the execution host for every command, shows
  the first failed or missing signal, preserves bounded endpoint/HTTP detail
  from Windows snapshots, and keeps Proxmox-only backup evidence explicitly
  unknown when a workstation snapshot cannot collect it.

## Installation manual continuation (2026-08-24)

- The canonical install suite was dry-read from `docs/install/START-HERE.md`.
  All 50 active install-document links resolve, all 52 angle-bracket
  placeholders appear in the secrets ledger, all 311 shell blocks pass
  `bash -n`, and all 66 PowerShell blocks parse.
- Mealie, Grocy and Obsidian LiveSync now document explicit pre-live gates,
  operator acceptance, consistent off-host backup, loopback-only isolated
  restore, update and matching-data rollback. LiveSync now names the canonical
  `K:` vault rather than the stale `E:` checkout and remains correctly parked
  while the canonical tree is dirty.
- `docs/install/services/README.md` records the last safe stop and promotion
  evidence for all 23 service manuals. Version and decision-gate references now
  cover volatile-release lookup, public exposure, credential stores, camera
  bridges, low-code/agent automation and automatic updates.
- The dependency audit added OpenWrt `ethtool`, workstation Node/npm and Garage
  Pi virtual-environment dependencies; the stale OLED Python 2 install hint was
  corrected. The service matrix gained the staged Immich curated-exporter row
  and now points Mermaid Viewer to its install manual.
- The final dry-run remains open. Using Windows `py -3`, router lint,
  `first-flight` compile and placeholder-tolerant `full` preview all still stop
  at `architecture.docker_host_tailscale_egress_rule_present`. Normal `full`
  compile additionally requires the real WireGuard, device-MAC and Wi-Fi
  inputs. The next documentation pass should reconcile that router invariant,
  then finish service/access-matrix verification before claiming a complete
  end-to-end dry run.

## Repository state

- Branch: `codex/portal-refinement`
- Recent relevant commits:
  - `6a82bb0 docs(architecture): reconcile live system`
  - `fc5c174 docs(install): expand service runbooks`
  - `d8610fb fix(docker): pin service bridge networks`
  - `0b1fb29 chore: merge origin/main`
  - `b426537 chore(infra): capture August service updates`
  - `1f7d557 feat(services): finish household rollout`
- User-owned Obsidian changes may be present under `.obsidian/`; do not stage or
  overwrite them during project work.
