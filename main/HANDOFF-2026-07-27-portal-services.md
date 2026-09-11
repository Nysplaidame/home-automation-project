---
title: Portal, Monitoring and Household Services Handoff
description: Live Homepage/monitoring state and the next decision-gated service work
created: 2026-07-27
modified: 2026-09-10
type: handoff
status: current
---

# Handoff — Portal, Monitoring and Household Services (2026-07-27)

## 2026-09-10 troubleshooting deployment

- Deployed the verified evidence-age/context update from `10db89f` to the
  existing VM103 stack. Updated app.js, diagnostic-model.js and index.html;
  built with the already-cached Nginx1.27-alpine image using `--pull=false`,
  then ran `docker compose up -d --no-build --no-deps troubleshooting-dashboard`.
  Compose, Nginx config, dependencies and other services were unchanged.
- New image: `sha256:a85ef04432a6be7975b0280a19c3ed86e5c68a18891d5e81e56f696674ed7e4c`.
  Local, staged-source and running-container file hashes match:
  app.js `d6ccac79e5d2b6f1e5dbc5db79a4342d4b5c16ff2a849b09160498b9c60215dc`;
  model `f47b62c1ab6ac2cf8831abe192152a9ec56b46ab4b2c359545d2674370a1a836`;
  HTML `2e8916f8b5260db3f1ebb33bd2eeb57b6ca0b5b7080ec8a24e57c7ae24816bfa`.
- Nginx syntax passed, management HTTP200 and security headers retained,
  read-only root filesystem retained. Live Playwright desktop/mobile checks
  passed with actual Windows JSON and synthetic stale/example/age-transition
  cases; screenshots inspected. Monitoring-source probe returned no HTTP
  response (000). No new DNS/Homepage placement or public access.
- Fresh Windows collection at `2026-09-10T11:25:03+01:00`: 12 PASS / 1 FAIL,
  with only camera_01 failing, consistent with recorded disconnection.
  Timestamp parses as recent/usable. It is a reachability/HTTP snapshot,
  not certificate trust, physical acceptance or Proxmox backup proof.
  This workstation uses the canonical script; no matching scheduled Windows
  health/automation task was found.
- Proxmox SSH still returns `Permission denied (publickey)` for root from this
  workstation. Installed Proxmox collector update and real mount/backup JSON
  acceptance remain open; no authentication changes were made.
- IPv4 DOCKER-USER retains VLAN10 RETURN followed by DROP for the exact
  VM103:8094 destination. Contrary to the August blanket-denial description,
  IPv6 currently has a pre-existing tailscale0 RETURN for8094 before DROP.
  The current stack publishes IPv4 only and its bridge reports IPv6=false;
  record this policy discrepancy for reconciliation before IPv6 publication.
  No firewall rules changed in this deployment.
- Rollback copies (including firewall snapshots and prior image ID) are under
  `/opt/backups/troubleshooting-evidence-20260910/`. The previous image is tagged
  `troubleshooting-dashboard:rollback-20260910`. To roll back on VM103, restore
  app.js/model/index.html from that directory into the stack, tag the rollback
  image as `troubleshooting-dashboard-troubleshooting-dashboard:latest`, then
  run `docker compose up -d --no-build --no-deps troubleshooting-dashboard`
  from `/opt/stacks/troubleshooting-dashboard/` and verify HTTP/rendering.
  The retained image was not removed and rollback was not exercised this pass.

## 2026-09-10 troubleshooting evidence presentation (local)

- Added a 36-hour evidence-age review window to the read-only dashboard.
  Missing/ambiguous/invalid/future/stale timestamps cannot produce current
  Healthy or Action-needed claims; raw observations remain visible and in
  copied reports. The UI refreshes age every minute without discarding focus,
  step progress or notes. Import/clear deliberately resets step progress.
- Built-in examples have an explicit non-live label in the UI and report;
  external JSON cannot opt itself into the example freshness exemption.
- Camera and P1S display dated September7 disconnected/uncommissioned context.
  No device failures are silently suppressed, and related service/storage
  evidence remains independently visible.
- Windows collector source now emits an explicit UTC offset and Bash emits
  UTC Z. Installed collectors are unchanged; legacy timezone-free imports
  remain visible but require fresh, unambiguous evidence for assessment.
- Verification: 14 model tests, desktop/mobile browser checks including the
  live age-boundary transition and focus/notes preservation, six existing
  Proxmox validator tests, PowerShell parsing and Bash syntax passed.
  Screenshots were inspected for layout and readable evidence/context text.
- Source-only change: no dashboard or collector deployment, network collection,
  notifications, credentials, firewall changes or physical actions in this pass.
  Next is a bounded update of the existing staged stack and installed collectors.
  Fresh Proxmox backup/mount acceptance and owner DNS/Homepage choice remain open.

## 2026-09-10 diagram readability and troubleshooting check

- Reworked all 11 canonical Mermaid sources into purpose-specific grouped
  views. Master covers placement; network inventory, physical attachments,
  access policy, service inventory and storage retain their dedicated detail.
  Disconnected cameras, rollback guests and uncommissioned hardware remain
  explicit. System claims use the September7 baseline, not a fresh full audit.
- At the same 1600x1100 browser viewport, master fit rose from 14% to 79%,
  VLAN from 24% to 89%, and Docker placement from 30% to 73%. Wider labels,
  straight connectors and title margins remove unnecessary wrapping and
  heading collisions. Phones still require zoom/pan for detailed reading.
- All 11 generated sources match canonical files and render without browser
  errors. Three complex views pass mobile overflow, zoom, 100% and Fit checks.
  Reusable check: `apps/mermaid-viewer/scripts/verify-diagrams.mjs`.
- Atomically deployed only `dist/diagram-data.js` to the existing docker-host
  bind-mounted stack. LAN8092 and fixed HTTPS8195 return SHA256
  `876395a974946f8f939fb5e2f820561510ff0fad3d2b84c8e150e1e9dfff1f5c`.
  HTTPS content verification used curl's certificate bypass; it does not
  establish client trust. Prior data is retained at
  `/opt/backups/mermaid-layout-20260910/diagram-data.js`; rollback by copying
  that file to a temporary sibling in the live dist directory and renaming
  it over `diagram-data.js`. No container restart or access-policy change.
- Troubleshooting dashboard LAN8094 returns HTTP200 today. September7 source
  hashes matched the deployed read-only app; no troubleshooting code changed
  in this pass. It remains management-only, pending fresh Proxmox backup/mount
  acceptance and an owner DNS/Homepage placement choice. The Home Operations
  Workbench remains a separate local prototype. Next no-input app work can
  improve evidence freshness and planned-offline presentation using fixture
  imports; live evidence and promotion gates remain separate.

## 2026-09-07 audit follow-through

Owner authorized all four no-input follow-ups. Completed local work and
read-only collection; no live configuration/deployment, account/credential
change, notification send, package update, physical actuation or restore drill.

- Reconciled README, current-state/task baselines, router WAN guidance and
  main-tree AGENTS checkout path with K: canonical authority, 64GB RAM,
  VLAN55/Hive, LAN4 OMV and deliberately disconnected cameras. September
  tabletop reasoning extends the existing July resilience test cards rather
  than creating a competing recovery manual.
- Recovered six missing Fail2ban jail/filter/runbook files from `6bee788`.
  The five old branch commits were reviewed semantically: retained newer
  Homepage proxy/DHCP/docs; preserved the deferred Proxmox web-UI jail decision;
  restored Proxmox and CT114 MAC reservations only after router neighbors
  freshly matched `38:05:25:31:55:D3` and `BC:24:11:CE:B9:E5`. Source-only;
  no router deployment. Historical branch ancestry is not merged wholesale.
- VM102 Fail2ban `sshd` active, zero bans; VM103 active. CT114 inactive, no
  APT proxy, cache TCP3142 timeout and direct Debian HTTP failure. Its 56
  cached candidates rely on June19 security/update metadata. Proxmox and OMV
  deny available workstation SSH keys, so SMART and fresh guest archives/
  integrity/restores remain unknown. No access policy was changed to bypass this.
- Updated maintenance log with current cached VM103/VM102 package candidates,
  backup/timer results and capacity. Watchtower's monitor-only setting is
  confirmed, but September6/7 ntfy notification delivery fails with attachment
  error40014. Healthy container state does not establish working alert delivery.
- Added Windows/Proxmox offline health adapters, browser import and a CLI that
  refuses existing output. Known statuses only; raw collector detail discarded;
  missing evidence unknown; 36-hour freshness and explicit legacy timezone;
  backups never imply integrity/restore proof. A fresh Windows snapshot was
  converted successfully outside Git. Workbench remains local/import-only.
- Tightened Proxmox snapshot `--require-pass` to reject stale, future, invalid
  or timezone-ambiguous observations. Legacy timestamps require the collector's
  actual `--timestamp-offset`. Direct Proxmox snapshot acceptance stays open.
- Full Transfer Portal pytest in an isolated temporary Python3.13 venv:
  48 passed / 2 skipped (Windows symlink privilege). Local dependencies were
  installed in that venv only. Linux privileged-helper acceptance is still open.
- Workbench syntax +10 tests, Troubleshooting model9, snapshot validator6,
  router recovery4 and source lint pass. All11 canonical diagrams match generated viewer data and
  pass browser Mermaid parsing. Both compiler profiles' placeholder
  previews pass in temporary directories without reading deployment secrets.
  Workbench and Troubleshooting desktop/mobile browser smoke pass; Workbench
  screenshots inspected. All five VentSys browser/mock tests pass after fixing
  an undefined startup helper. Recomp JS syntax passes and both app/service-worker
  SHA256 hashes match VM103. No new Recomp write-flow acceptance was performed.
- VentSys public credential removal left an incomplete card/page bridge. The
  startup fix keeps the page honestly offline; `dashboards/ventsys-card-status.md`
  marks draft state and acceptance work. Do not deploy it as a working bridge.
- `git diff --check` passes. A targeted private-key/JWT/GitHub-token marker
  scan of changed/untracked files found no matches; this is not a full security
  certification. Existing changes are preserved in separate feature-branch commits:
  `e47f8bb` network recovery; `5907eea` transfer safety; `364eaf0` Recomp;
  `699073e` VentSys draft; `d4fad16` Fail2ban; `bf8ecf8` offline workbench.
  Reconciled documentation/wiki is the final follow-through commit. Push this
  feature branch normally; main remains unchanged and should not receive the
  unaccepted VentSys bridge as a deployment-ready change.

## 2026-09-07 project health audit

Scope: canonical K: checkout, fetched origin refs, targeted documentation and
local checks, plus read-only management-workstation and docker-host probes.
No live configuration, deployment, commit, push or branch merge was performed.

- Git at audit start: `codex/portal-refinement` / `19f16a9` matches its fetched
  upstream (zero ahead/behind). There are 47 modified tracked files and 19
  untracked files, spanning network recovery, Transfer Portal safety changes,
  Recomp UI, VentSys dashboard/card, Home Operations Workbench, snapshot
  validation, roadmap and wiki. These working files are not protected by a Git
  push. The tracked diff is 1,834 insertions / 407 deletions before this entry.
- `origin/main` remains `ab81a70` (2026-07-16), 34 commits behind this branch.
  Those 34 commits are already pushed to the feature branch, not merged to main.
- `origin/claude/todo-list-review-6c88a1` has five commits absent here, ending
  at `6bee788` (2026-08-01). They record Proxmox/VM102 Fail2ban deployment,
  CT114's APT-path gap and task cleanup. Reconcile deliberately against current
  source/live evidence; do not redeploy or mark their historical claims current
  merely because the remote branch contains them. Two other local-only commits
  (`ceacc16`, `9416865`) concern stale Excalidraw artifact cleanup on old branches.
- Fresh `health_check.ps1 -Full -Json` at 22:28 BST: 12 PASS / 1 FAIL.
  Camera 1 RTSP is the sole failure, consistent with the documented deliberately
  disconnected cameras. Router, HA HTTPS, Frigate SSH/UI port, docker-host,
  Homepage, Bambuddy, MQTT TLS, Grafana, Kuma, llama.cpp and OMV NFS pass.
  HTTP checks relax certificate validation; these are reachability checks, not
  certificate, camera-stream, inference or end-to-end functional acceptance.
- Authenticated docker-host read: all 38 running containers are Up; all
  configured container health checks are healthy. App-data backup service
  reports success / exit 0 on 2026-09-07 at 03:50:33 BST, with its next timer
  scheduled for 2026-09-08 03:45. Root disk is 75% used (16G available);
  `/mnt/omv/immich` is 60% used (5.8T available). This does not prove Proxmox
  guest-backup freshness, NAS SMART health or a new restore test.
- Local checks: Workbench syntax + 6 model tests, Troubleshooting syntax + 9
  model tests, snapshot validator 4 tests, router recovery 4 tests and router
  lint all pass. `git diff --check` passes. Transfer Portal targeted safety/store
  tests: 29 passed, 2 skipped. Full pytest collection is blocked by missing
  `itsdangerous` in the workstation Python environment. Browser smoke, Linux
  root-helper acceptance and complete deployment/source parity were not rerun.
- Roadmap verdict: the September household/workshop roadmap correctly labels
  the Workbench local/import-only and hardware deferred. Older overview/task
  sections remain stale: README says three cameras live, 32GB RAM and ten
  segments without VLAN55; TO-DO's planning baseline still says cameras live;
  router README still describes temporary Wi-Fi WAN. Latest update-review log
  entry is 2026-08-01 (37 days ago), despite a weekly review policy. Proxmox
  snapshot acceptance remains open. Historical backup dates are not fresh proof.

Recommended no-input work order: reconcile roadmap/status documentation and
the missing branch evidence; validate and organize existing changes into
reviewable groups; refresh read-only backup/SMART/update evidence through
existing authorized access; then develop offline evidence adapters and recovery
tabletop documentation. Keep live publishing, physical commissioning, owner
accounts, retention choices and disruptive maintenance at their existing gates.

## 2026-09-05 HomeGuest broadcast repair

Owner reported that `HomeGuest` was absent from Wi-Fi scans. Authenticated
inspection found `wireless.guest_2g` had an invalid section type rather than
`wifi-iface`; `ubus` omitted it and `phy0-ap4` did not exist. The SSID, guest
network attachment, WPA2 security, client isolation and saved password option
were otherwise present. A backup of `/etc/config/wireless` was saved on the
router at `/tmp/wireless-before-homeguest-repair-1788632657`.

Restored only the section type to `wifi-iface`, committed wireless UCI and ran
`wifi reload`. This may have briefly reconnected 2.4 GHz clients. Validation:
`ubus` reports `phy0-ap4`; `iw` reports `HomeGuest` active; its SSID and WPA2
mode remain intact. The guest password was neither recorded here nor changed.
No firewall, VLAN, DHCP or 5 GHz setting changed.

## 2026-09-04 post-fibre recovery (supersedes the audit below)

Owner authorized repair of the audit findings. Live changes and acceptance:

- VM 103: backed up its Proxmox config locally, restored memory from 1024 to
  6144 MiB, performed a graceful shutdown (task OK) and started it. Guest now
  sees 5.8 GiB usable; after nine minutes load was 0.03/0.23/0.21, available
  RAM 1.7 GiB and swap 46 MiB instead of 2 GiB full. QEMU guest agent is active.
  All containers are running; all defined Docker health checks are healthy.
  Three OMV NFS mounts are present (backups, Immich, media). Root disk 75% used.
- Homepage HTTPS/HTTP, AdGuard UI and upstream DNS, Immich and Dozzle recovered
  without application reconfiguration. Final HTTP checks returned 200 for all
  five, plus OMV, Open WebUI and Frigate HTTPS. The core health script passed
  11/12 checks; its sole failure is the deliberately unplugged camera.
  All 48 authoritative home.local aliases passed validation again.
- Disabled the disconnected `wireless.router_uplink` Zyxel station and reloaded
  radio0. All five 2.4 GHz APs started, and a HomeIoT station joined. The 5 GHz
  APs remained available. Live radio0 is configured channel 5/HE40 (effective
  20 MHz); radio1 auto/HE80 selected channel 100. Source channel preferences
  are aligned with these live values. P1S is not yet set up, owner-confirmed;
  its absence is not a remaining router fault.
- LAN2 now exclusively accesses `cloud_iot`, VLAN 55, 192.168.55.0/24.
  Hive MAC `00:1c:2b:b1:02:20` received reserved `192.168.55.10` after the
  owner power-cycled it. Ethernet negotiates 100 Mbps full duplex. Router
  DHCP/DNS/NTP work; conntrack shows bidirectional established internet TCP
  443 and router NTP. The owner still sees Hive offline in the app and reports
  older unresolved issues: application/account acceptance remains OPEN.
- Cloud IoT firewall: router input REJECT except IPv4 DHCP/DNS/NTP, forwarding
  REJECT except WAN; external DNS ports 53/853 rejected before WAN forwarding.
  No forwarding to internal zones. Runtime nftables and `fw4 check` pass.
  This was configuration/ruleset verification, not an active penetration test
  from the Hive device. Hive was observed using external UDP 9953: blocking
  standard DNS ports does not prevent all encrypted/nonstandard DNS.
  No VLAN 50 safety-device internet permission was added.
- WAN stays untagged Zen/Openreach PPPoE on `eth1`. Explicit WAN6 now uses
  `@wan`, with `wan.ipv6=1`, DHCPv6 and required scoped WAN ICMPv6 input/error
  forwarding rules. Packet capture proves Zen returns **NoAddrsAvail** and
  **NoPrefixAvail**. A temporary prefix-only /48 request also received
  NoPrefixAvail; reverted to reqaddress=try, reqprefix=auto. IPv6 remains
  unavailable; owner is unsure whether Zen enabled it. Ask Zen to check IPv6
  provisioning/allocation, quoting those server responses. IPv4 continues
  working with zero loss in the bounded ping check.
- HomeAdmin PC signal measured from the router: about -77 dBm, two spatial
  streams, 80 MHz, about 432 Mbps current PHY rate. This supports investigating
  antennas/placement and a wired comparison for the reported ~200 Mbps Wi-Fi
  throughput. No rate cap found; full 900 Mbps service acceptance remains open.

Backups: router `/root/recovery-20260904/` contains original network, firewall,
DHCP and wireless configs. A delayed network rollback was armed with
`start-stop-daemon` and cancelled by the verified `network-accepted` marker.
The initial `nohup` launch was unsupported; connectivity and firewall were
subsequently verified before cancelling the working watchdog. VM config backup:
`C:/Users/Admin/AppData/Local/Temp/vm103-before-recovery-20260904.json`.
No router, Proxmox or PPPoE password is recorded in tracked files.

Saved rebuild source now includes PPPoE/eth1, logical WAN6, cloud VLAN55,
Hive DHCP and firewall policies. Both compile preview profiles and lint pass;
four offline regression tests cover missing/unsafe credentials and WAN/LAN2
mapping regressions. Both actual deploy profiles refuse absent PPPoE secrets;
provide them only through ignored `tools/router-deploy/keys/router_secrets.json`.
All 11 Mermaid diagrams passed a headless browser parse. Updated diagram-data.js
was deployed atomically to the live viewer on port8092 and verified byte-for-byte
over HTTP; the previous data file is backed up beside its dist directory.
Both the scoped repair script and full firewall source pass router sh -n.

Full generated configuration was NOT redeployed: the scoped repair script
preserved existing application rules and live secrets. Preview artifacts are
not a deployment-ready credentialed configuration.

Hive's current service page acknowledges false offline status and recommends
force-closing/reopening the app without logout. This is a possible explanation,
not proof of this hub's problem. Remaining diagnostic input: hub model/light
pattern and status under Manage → Devices after restarting the app.
Sources checked 2026-09-04:
- https://status.hivehome.com/
- https://support.hivehome.com/portal/app/portlets/results/viewsolution.jsp?solutionid=022433716182024
- https://docs.opnsense.org/manual/how-tos/IPv6_ZenUK.html

## 2026-09-04 HomeAdmin throughput investigation

Owner reports approximately 200 Mbps over HomeAdmin after the Zen 900 Mbps
fibre installation. Read-only checks and bounded download tests found:

- Management workstation `192.168.10.116` uses its Intel AX210 Wi-Fi adapter
  with a reported link rate of **576 Mbps**; Ethernet is disconnected and
  Mullvad reports disconnected. The default active path is `192.168.10.1`.
  Driver settings allow automatic 5 GHz channel width, 802.11ax, highest
  transmit power and no MIMO power saving. Windows denied detailed WLAN
  telemetry because location permission is unavailable; signal/channel were
  not measured and no privacy setting was changed.
- Source configuration places HomeAdmin on 5 GHz `radio1`, channel 36,
  `HE80`. The separate HomeAdmin-2G radio issue below does not establish the
  cause of this 5 GHz slowdown. No intentional 200 Mbps limiter was found
  in the targeted tracked router configuration; live shaping/offload settings
  remain uninspected because this session's router SSH key was rejected.
- Sequential HTTPS downloads from `fsn1-speed.hetzner.com`, discarded without
  writing payloads to disk: wired monitoring VM `192.168.60.10` downloaded
  100 MiB in 1.503 s (**558 Mbps**) and 1 GiB in 12.297 s (**699 Mbps**).
  The workstation downloaded the same 100 MiB file in 4.878 s (**172 Mbps**),
  with its reported Wi-Fi link still at 576 Mbps afterward.
- Monitoring VM name resolution initially timed out. Tests used curl
  `--resolve` with an A record obtained from the workstation, retaining
  normal HTTPS hostname/certificate verification and changing no DNS settings.
  Cloudflare returned HTTP 403, and a later parallel Hetzner attempt hit
  HTTP 429; neither is a valid throughput measurement and neither was retried.

Conclusion: there is no general 200 Mbps ceiling on the fibre path; the
workstation's wireless path underperforms the wired VM. The exact client,
radio or router-forwarding cause is not established. These single-file
results do **not** establish maximum WAN throughput or full 900 Mbps delivery.
Next: check workstation antenna attachment/placement and a close-range client
comparison, then inspect live HomeAdmin signal/rates/retries and channel use.
Use a proper wired speed test against Zen to verify the service ceiling.
No router/client configuration, service restarts or package installs occurred.

### Firmware research and SSH-key preparation

The owner confirmed the result is from this PC and its external antenna is a
single cabled unit. A subsequent link-rate sample was 432 Mbps. The installed
AX210 driver is `23.150.0.4` (driver date 2025-06-12); Intel currently lists
`24.60.0.3` for AX210 in package 24.60.0. This is an update candidate, not a
proven fix. [Intel driver source](https://www.intel.com/content/www/us/en/download/19351/intel-wireless-wi-fi-drivers-for-windows-10-and-windows-11.html)

- GL.iNet's table lists MT6000 stock `4.9.1` (MediaTek SDK/OpenWrt 21.02)
  and separate `4.9.0-op24` (OpenWrt 24.10). The stock release metadata dates
  4.9.1 to 2026-08-05 and lists no explicit Wi-Fi/PPPoE throughput fix.
  [Firmware table](https://www.gl-inet.com/pages/firmware-versions),
  [download centre](https://dl.gl-inet.com/router/mt6000/stable).
- Similar firsthand GL reports include unresolved approximately 500 Mbps
  PPPoE on 4.7.4 and 500-650 Mbps WAN-to-Wi-Fi with AX210 on 4.7.4 beta despite
  gigabit wired/local-Wi-Fi results. These are differing configurations and
  do not establish a universal defect or a cause here.
  [PPPoE report](https://forum.gl-inet.com/t/flint-2-only-getting-500-mbps-over-pppoe-instead-of-1-gbps/57230),
  [AX210/Wi-Fi report](https://forum.gl-inet.com/t/flint-2-wi-fi-download-speed-issue/54668).
- A May 2026 Zen 900 owner reported 180 Mbps and variable 230-700 Mbps tests
  including Windows PPPoE; no cause was established. Use Zen's recommended
  wired Speedtest.net test with the Zen Internet server for the WAN baseline.
  [Zen customer report](https://forums.thinkbroadband.com/unhappiness/4787671-zen-900-fttp.html?page=34&sb=9),
  [Zen test instructions](https://www.zen.co.uk/help-support/check-your-speed).

Installed router firmware was subsequently authenticated through LuCI and SSH:
**vanilla OpenWrt 24.10.3 `r28872-daca7c049b`, kernel 6.6.104**, with mt76
`2025.09.15~6467af3b`. GL.iNet stock 4.x release numbers and proprietary-driver
reports do not directly apply to this installed firmware.

Owner requested a dedicated SSH key. Created workstation-only Ed25519 key
`~/.ssh/home_router_desktop_ed25519` and SSH alias `home-router-lan`, using
the existing pinned router host key and strict host-key checking. Public-key
fingerprint: `SHA256:gSwXaFqLJK2YINlWQesU1rDE0SlQZH/VC7m2dnC7IIQ`.
**Complete at approximately 16:48 BST:** owner logged into LuCI; installed the
public key and verified `ssh -o BatchMode=yes home-router-lan` authenticates as
root. `/etc/dropbear/authorized_keys` is root-owned mode 600 and contains one
new `home-router-desktop` entry and the preserved `router-deploy@laptop` entry.
The private key stays in the workstation's protected `.ssh` directory outside
the vault. No password, SSH listener or firewall change was made.

### Authenticated Wi-Fi findings and upgrade candidates

- Live `radio1` is set to **auto channel**, currently **100 / 5500 MHz**, with
  **HE80**, country **GB**, and transmit power **23 dBm**. The tracked channel
  36 setting above is source intent, not the live channel.
- PC MAC `a4:f9:33:c7:82:33` associates to `phy1-ap1` (HomeAdmin). Ordinary
  received signal/average is approximately **-76 dBm**, noise **-92 dBm**;
  AP-to-PC rate is **432.3 Mbps**, HE-MCS 4/NSS 2; PC-to-AP snapshot is
  **360.3 Mbps**, HE-MCS 7/NSS 1. WMM and protected management frames are on.
  These support a limited wireless path but do not prove an antenna defect.
- ACK RSSI around -38 dBm is unreliable here: this exact mt76 revision has
  an erroneous fourth-chain ACK mask, documented by a later upstream fix.
  Also, its `tx_failed` includes retries; equal retry/failure counters are
  **not** a count of that many lost packets. Avoid interpreting these as
  contradictory strong signal or a measured packet-loss rate.
  [Driver source](https://github.com/openwrt/mt76/blob/6467af3bcf1154c2ceb032c903d533f0c718bbc2/mt7915/mac.c),
  [ACK reporting fix](https://www.spinics.net/lists/kernel/msg6141279.html).
- Software/hardware flow-offload options are absent and no nft flowtable is
  active; WED is disabled, packet steering is enabled. No SQM configuration
  or SQM/QoS package was found. This does not establish a CPU throughput
  limit; only idle CPU/load was measured. WAN still negotiates 2.5 Gb/s full
  duplex. The sampled log contained no matching mt76 crash/radar/timeout error.
- OpenWrt **25.12.5** is the current stable upgrade candidate; **24.10.8** is
  the maintenance branch, with 24.10 EOL projected for September 2026.
  25.12.5 includes a generic transmit-queue scheduling fix for low throughput,
  but no verified AX210-specific cure for this case was found. Plan a config
  and installed-package backup, account for `opkg` to `apk`, and preserve the
  live PPPoE/VLAN settings rather than deploying the stale source template.
  [24.10.8 notes](https://github.com/openwrt/openwrt/releases/tag/v24.10.8),
  [25.12.5 notes](https://github.com/openwrt/openwrt/releases/tag/v25.12.5),
  [Queue fix](https://github.com/openwrt/mt76/commit/2eb5d1e3cfbf3f08f197b22759be4950d501d3d8).

No radio tuning or firmware/driver update was performed. Next diagnostic is a
controlled local wired-to-Wi-Fi throughput comparison, followed by deliberate
client-driver and radio changes with before/after measurements. A proper wired
Zen speed test remains needed to assess full service delivery.

Separately, the 16:48 overview already shows the old Zyxel station disabled,
2.4 GHz APs up with three HomeIoT clients, LAN2 in `cloud_iot` VLAN 55 and Hive
leased at `192.168.55.10`. These supersede the earlier audit's radio/LAN2
observations below; they were not changed or functionally accepted by this
SSH-key/throughput task. Full Hive isolation and service repair evidence belongs
with the task performing those changes.

## 2026-09-04 post-fibre connectivity audit — degraded, not all clear

Read-only checks from the Windows management workstation `192.168.10.116`,
authenticated router SSH, Proxmox API, monitoring VM and llm-host. Router and
Proxmox credentials supplied by the owner were used in memory only. No live
configuration changes, reboots or service restarts were performed. The owner
confirmed the Zyxel switch is unplugged: switch/camera failures are expected.

### Verified working

- Zen PPPoE is authenticated and up on `eth1` / `pppoe-wan`. It is the only
  IPv4 default route. Router-bound public ping: 3/3 replies, about 9.5 ms,
  zero loss. Workstation public HTTPS also returns 200.
- WAN and Proxmox LAN1 negotiate 2.5 Gb/s full duplex; NAS LAN4 negotiates
  1 Gb/s full duplex. Live bridge-VLAN membership matches the recorded
  Proxmox trunk, management LAN2, switch LAN3, storage LAN4 and recovery LAN5.
  LAN3 and LAN5 have no carrier; LAN1/LAN2/LAN4 are linked.
- `fw4 check` passes. Running WAN input permits the recorded WireGuard UDP
  listener and ping, then rejects other traffic; no broad admin allowance
  was seen. This is configuration inspection, not an external penetration test.
- All 48 canonical `home.local` aliases pass the repo DNS validator against
  router `192.168.10.1`; system resolution of Homepage agrees. Router public
  resolution works through its configured fallback resolvers.
- Proxmox UI/API is accessible. VMs 100/102/103 and CTs 111/114 are running;
  rollback VMs 101/104 are stopped. OMV-backed Proxmox storage is active,
  approximately 60% used. Host local storage is approximately 77% used.
- Proxmox reports approximately 64 GB installed (62.3 GiB usable) and
  approximately 37.5 GiB available; older 32 GB hardware notes are stale.
- HA HTTP 200 and MQTT TLS listener reachable; Frigate HTTPS HTTP 200.
  Frigate API port 5000 times out from the workstation but returns HTTP 200
  from the authorized monitoring VM, so it is not an API outage.
- OMV web and Transfer Portal return HTTP 200; SMB 445 and NFS 2049 accept
  connections. Monitoring VM reaches OMV NFS too. This does not prove every
  application's mount or a new backup/recording write.
- Grafana health, Kuma and InfluxDB health return HTTP 200. Monitoring VM has
  no failed systemd units.
- llama.cpp models and Open WebUI return HTTP 200. Piper, Whisper and
  OpenWakeWord ports are open from monitoring; management-workstation timeouts
  match llm-host's source-scoped firewall. llm-host has no failed systemd units.
- Direct responses also received from Bambuddy, Mealie, Grocy, GardenKeeper
  UI/API, Household Hub, Mermaid Viewer, Gridfinity, Recomp health, Jellyfin
  health, Calibre-Web, qBittorrent, SearXNG, Whoogle, ntfy health and the
  Troubleshooting Dashboard. LiveSync/Atsumeru respond with authentication
  required (401); MediaMTX accepts TCP. These prove listener/UI reachability,
  not authenticated app workflows, media writes or cloud integrations.

### Actual issues and repair priorities

1. **VM 103 memory is 1024 MiB in Proxmox's live configuration and runtime.**
   This is not merely ballooning from a larger configured maximum. Four vCPUs
   are configured. Guest reports 948 MiB usable, essentially all 2 GiB swap
   used, very heavy swap I/O, and load averages rising from 127 to 206.
   Canonical inventory previously specified 6 GiB. Host memory is available.
   SSH works intermittently, then stalls before its banner; guest-agent exec
   returns `QEMU guest agent is not running`. Restore an appropriate VM memory
   allocation before diagnosing all application failures as network problems.
2. **Homepage HTTPS 443, AdGuard 8080 and Immich 2283 refuse connections.**
   Homepage HTTP 3001 and Dozzle 8081 time out. Router queries to AdGuard DNS
   at `192.168.20.102:53` are refused too: public fallback keeps DNS working,
   but filtering is not proven operational. Initial `docker ps` showed the
   Homepage container healthy while the HTTPS endpoint was absent, and very
   short uptimes for Mealie/Immich. Full stopped-container/OOM/mount inspection
   could not complete because SSH and the guest agent are unresponsive.
3. **All 2.4 GHz AP interfaces are down.** 5 GHz HomeMain/HomeAdmin/HomePrinters
   are up. The old `router_uplink` station remains enabled for `ZyXEL_F1E9`
   but is disconnected on the same radio; repeated hostapd probe-send errors
   appear. This is a likely cause of the unavailable 2.4 GHz SSIDs and needs
   a controlled retirement of the temporary uplink now that fibre works.
   P1S `192.168.35.200` is unreachable; do not assume the printer is powered on.
4. **IPv6 is not established.** Explicit `wan6` points at nonexistent `wan`
   and reports NO_DEVICE. Dynamic PPPoE `wan_6` is pending on `pppoe-wan`;
   there is no IPv6 default route. Reconcile the two interfaces and required
   DHCPv6/ICMPv6 firewall allowances before claiming IPv6 support.
5. **Hive is connected but not isolated.** `myHivehub` has DHCP lease
   `192.168.10.124`, MAC `00:1c:2b:b1:02:20`, and a reachable router neighbour
   entry. LAN2 remains untagged management VLAN 10. The planned cloud-device
   network is not implemented; Hive cloud/app operation was not tested.
6. The tracked WAN deployment template still contains old DHCP/`wan` device
   settings. Do not deploy it over the working PPPoE connection.

TLS limitation: the standard Windows health script skips certificate
validation. Separate strict Python TLS checks reject the local HA/Frigate CA
for missing key-usage extension; Windows curl reports unavailable revocation
checking. Proxmox is not trusted by the Python CA store. These are separate
certificate-validation findings, not evidence that those HTTPS listeners are down.
Windows curl with only revocation checking disabled (`--ssl-no-revoke`)
successfully checks the HA/Frigate certificate chain and name and receives
HTTP 200 from both; strict-client compatibility remains a follow-up.

Remaining coverage: no end-to-end mobile Tailscale test, guest/IoT client
isolation probe, authenticated HA/voice/Hive workflow, NAS write/backup proof,
or camera test while the switch is unplugged. OMV SSH key authentication was
rejected, so no direct NAS OS/SMART inspection was made.

## 2026-09-04 Zen/Openreach WAN restored (owner-confirmed)

- Physical connection: Openreach ONT directly to GL-MT6000 WAN socket.
- Working logical interface: `wan`; underlying Ethernet device: **`eth1`**.
- The owner selected PPPoE and entered Zen broadband credentials in LuCI.
  LuCI then reported `Network device is not present` because the selected
  device was the nonexistent `wan`. Selecting Ethernet adapter `eth1`
  resolved the connection; owner reported "we're up".
- Zen/Openreach requires no WAN VLAN tag. Access Concentrator and Service
  Name should be empty. Credentials are not recorded in project files.
- Hardware mapping reference: [OpenWrt GL-MT6000](https://openwrt.org/toh/gl.inet/gl-mt6000).
- **Deployment gap:** `configs/openwrt/vlan-config.conf` still specifies
  `device 'wan'` for WAN/WAN6 and DHCP for WAN. Do not redeploy that template
  over the working router. Reconcile live network configuration, PPPoE secret
  handling and IPv6 attachment with the compiler/validation tools first.
  IPv6 and retirement of the temporary Wi-Fi uplink have not been verified.
- Evidence is owner confirmation and LuCI screenshots, not an agent SSH
  inspection. Restoration of Proxmox and its services is not yet confirmed.

## 2026-09-04 fibre outage, NAS correction and Hive LAN2 research

The owner reports Proxmox down and all router-connected devices unplugged
during fibre installation. **OMV is connected to router `lan4`, VLAN 40**;
reconnect it there. GS1900 port 8 remains configured as spare VLAN 40 access.
This owner confirmation supersedes the August documentation reconciliation,
which incorrectly restored the older port-8 NAS attachment. The July 16
direct-router cutover in [[HANDOFF-2026-07-01-frigate-first-camera]] was correct.

The owner needs LAN2 for a Hive device and asked for requirements research.
Assumption: an Ethernet-connected Hive heating/smart-home hub; exact model
and MAC are still needed. No live router changes or probes were performed.

### Findings and proposed change (not deployed)

- Hive's official router-change guide says to connect the Ethernet hub to the
  working new router; it should reconnect automatically. No fixed default IP
  is supplied in that guide. Plan for automatic DHCP and confirm its lease;
  use a router-side reservation after the actual MAC is known.
- Hive explicitly warns against 2.5 Gbps router sockets. Use a 10/100/1000
  socket and verify which physical socket maps to OpenWrt `lan2` before apply.
  Leave link negotiation automatic initially.
- LAN2 currently belongs to management VLAN 10 (`lan2:u*`), with DHCP,
  router administration and broad internal/WAN access. A hub may connect
  there already, but this is inappropriate privilege for a cloud device.
- Recommended: a separate `cloud_iot` network/zone for LAN2. VLAN 55 and
  `192.168.55.0/24` are candidate identifiers, subject to live collision checks.
  Remove `lan2:u*` from VLAN 10 and add it only to the new VLAN as untagged/PVID.
  Add router interface, DHCP scope, router DNS/NTP input rules and WAN NAT
  egress; reject other router services and initiation into all internal zones.
  No Proxmox trunk or switch-trunk membership is needed for this single port.
- Keep VLAN 50's offline VentSys policy intact. VLAN 20 has shared service
  hosts and restricted internet, so neither existing network is a suitable
  drop-in home for this device. Guest VLAN 99 could provide a simpler initial
  internet path but would share its layer-2 segment with guest clients.
- The official pages consulted do not publish a complete model-specific
  destination/port allowlist. Start with isolated outbound internet access
  and established return traffic; observe the hub's traffic before narrowing
  egress. Do not assume HTTPS alone covers registration, time and updates.
  No inbound WAN port forwards, DMZ-host setting or UPnP are proposed.
- DNS must work with Proxmox off: tracked dnsmasq has AdGuard first and public
  Quad9/Cloudflare fallback. Verify fallback on the new segment rather than
  assuming it works live. DHCP/DNS/gateway must be provided by the GL router.
- Home Assistant's official Hive integration uses cloud polling and requires
  Hive account 2FA. That integration does not justify a general LAN2-to-HA
  firewall opening. Local HomeKit/model-specific features are separate scope.

### Implementation and acceptance sequence

1. Confirm model/MAC and restore a working upstream internet connection.
2. Verify a management session via HomeAdmin and a working LAN5 recovery
   path before changing LAN2. Back up live network/firewall/DHCP and inspect
   actual interface/zone/uplink state; the tracked firewall file is a full
   rebuild script and must not be run as an incremental change.
3. Prepare a scoped network/DHCP/firewall patch, update corresponding source
   and deployment-tool assumptions, validate generated UCI and `fw4 check`,
   and use rollback protection for the network apply.
4. Connect Hive on LAN2, verify link/lease/DNS, then the Hive app's online
   state and a deliberate user-observed functional check. Updates may take
   15-20 minutes or up to an hour according to Hive's router-change guide.
5. Confirm the device segment cannot reach router administration, management,
   NAS, cameras or automation hosts; confirm Proxmox/switch/NAS ports remain
   correctly assigned. Record deployed subnet, reservation and rules only
   after acceptance.

### Sources consulted on 2026-09-04

- [Hive: changing broadband providers/router](https://support.hivehome.com/portal/app/portlets/results/viewsolution.jsp?solutionid=240916092445787)
- [Hive: hub offline and Ethernet compatibility](https://support.hivehome.com/portal/app/portlets/results/viewsolution.jsp?page=1&position=0&q=hub+offline&solutionid=022433716182024)
- [GL.iNet: GL-MT6000 guide](https://docs.gl-inet.com/router/en/4/user_guide/gl-mt6000/)
- [GL.iNet: port specifications](https://static.gl-inet.com/www/images/products/datasheet/mt6000_datasheet_20251103.pdf)
- [Home Assistant: Hive integration](https://www.home-assistant.io/integrations/hive/)

Canonical cabling reference and three network diagram sources were corrected;
existing router/NAS wiki pages were synchronized. The generated/live Mermaid
Viewer has not been rebuilt or deployed during the outage.

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
2. Finish Troubleshooting Dashboard acceptance: authorize an appropriate
   workstation key on the Proxmox host, import a real Proxmox JSON snapshot,
   and accept the backup-freshness path. The dashboard is already staged on
   management-only port `8094`; DNS and Homepage remain unapproved.
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
  collection and Playwright desktop/mobile smoke checks passed.
- The promotion review now names the execution host for every command, shows
  the first failed or missing signal, preserves bounded endpoint/HTTP detail
  from Windows snapshots, and keeps Proxmox-only backup evidence explicitly
  unknown when a workstation snapshot cannot collect it.
- Commit `c5a57ee` was pushed, then the dashboard was staged live at
  `http://192.168.20.102:8094/` on bridge `10.240.32.0/24`. It binds only the
  VM 103 VLAN-20 address; `DOCKER-USER` allows VLAN 10 and drops other IPv4
  sources, while the IPv6 policy drops port `8094`. Management returned HTTP
  `200`; forced LAN and Tailscale tests were denied.
- The deployed desktop/mobile flow accepted the real Windows 13/13 snapshot.
  `docker compose down` removed the container, network and listener; the
  management probe failed closed; `docker compose up -d` restored the service
  and the access tests passed again. Rollback copies of the pre-change firewall
  and audit scripts are under
  `/opt/backups/troubleshooting-dashboard-20260825T1518Z/`.
- The live security audit passes the new dashboard network and IPv4/IPv6 scope
  checks. It still exits non-zero solely because Bambuddy remains on its
  documented temporary host-network exception. Proxmox-host JSON acceptance is
  still open because all available workstation keys are denied by Proxmox.

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

## MediaMTX phone relay deployment (2026-08-27)

- Deployed pinned MediaMTX `1.20.1` on VM 103 from
  `configs/docker-host/stacks/mediamtx/`, using explicit bridge
  `10.240.16.0/24` and host bind `192.168.20.102:8554/tcp`.
- Only RTSP-over-TCP is enabled. MediaMTX does no decode/transcode; it relays
  the phone's compressed stream to the garage Pi and writes fMP4 directly to
  `/mnt/omv/media/phone-recordings/garage-phone/` on the existing OMV media
  mount. The container runs as `media-service` (`1007:100`) with read-only root,
  all capabilities dropped, no-new-privileges, one CPU and 256 MiB limits.
- UFW and persistent `DOCKER-USER` rules allow only HomeAdmin
  `192.168.10.0/24` to port `8554`; IPv6 and other IPv4 sources are dropped.
  Separate host-only publisher and viewer credentials are path-scoped to
  `garage-phone` in `/opt/stacks/mediamtx/.env` (`0600`).
- Acceptance passed authenticated H.264 publish/read, unauthenticated
  publisher/reader denial and a decodable fMP4 owned by
  `media-service:users` on OMV. Synthetic recordings were removed after the
  test. Automatic deletion remains disabled pending an explicit retention
  decision.
- Post-deployment idle use was `0.00%` CPU and `22 MiB` RAM. VM 103 had 4 vCPU,
  2.7 GiB available RAM, 34 MiB of 2 GiB swap used, and 19 GiB free on its
  64 GiB virtual disk (`69%` used). OMV media had 6.4 TiB free. No VM resource
  increase is justified for MediaMTX; reclaim the roughly 17 GiB of unused
  Docker images/build cache during a separate reviewed cleanup if system-disk
  pressure grows.
- Proxmox host-wide headroom and the authoritative VM 103 allocation could not
  be queried because this workstation has no accepted Proxmox SSH key. Guest
  Linux reports 7.7 GiB usable memory, consistent with an 8 GiB allocation.
- Next acceptance: configure Larix on the OnePlus and the garage Pi RTSP
  viewer, then run one real 30-minute 1080p session before considering H.265 or
  4K.

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


## 2026-09-10 dashboard readability deployment

- Reworked troubleshooting into a numbered choose/add/check/review journey.
  Body text is18px, supporting copy and commands16px, with increased contrast.
  A two-column desktop layout gives the investigation room; evidence follows
  below. All five problem choices are visible on phones. Checks expand
  individually and show their execution host, command and expected result.
- Added collection guidance beside upload: run the Windows collector from
  the canonical checkout, import health.json, retain failed observations,
  and use Proxmox collection for mount/backup evidence. Its existing SSH and
  installed-collector timezone gates remain explicit.
- Deployed app.js, styles.css and index.html to the existing management stack
  using cached base image and a scoped Compose recreate. No evidence model,
  collector, firewall, DNS or Homepage changes in this pass. Live HTTP file
  bytes match local sources; Nginx syntax,14 model tests, desktop/mobile browser
  checks and expanded mobile collection-help layout all passed. Screenshots
  inspected; instructions/commands no longer require tiny text or horizontal
  scrolling. Updated app design contract and README.
- Current image: sha256:ff7f534d2f6d41c417a955ae9e673c78a038c5e070f4a62cf37dc9971ccfadd1.
  Rollback source files are in /opt/backups/troubleshooting-readable-20260910/;
  prior image is troubleshooting-dashboard:readability-rollback-20260910.
  Restore those app.js/index.html/styles.css files, tag that image as
  troubleshooting-dashboard-troubleshooting-dashboard:latest and run
  docker compose up -d --no-build --no-deps troubleshooting-dashboard from
  /opt/stacks/troubleshooting-dashboard/. Rollback retained, not exercised.


## 2026-09-11 extended diagnostic routes

- Expanded the management-only troubleshooting dashboard from5 to27 routes,
  grouped into Network/access, Hosts/storage, Home/devices, Monitoring/maintenance
  and Applications/data. Added search, area filtering and collapsible groups.
  Covers WAN/Wi-Fi, DNS/TLS/Tailscale, Proxmox, Docker pressure, NAS mounts/capacity,
  app-data backups, monitoring, local AI/voice, automations, notifications, APT,
  Immich, media, download containment, LiveSync, household APIs, vault and phone
  relay, plus the original five and explicit VentSys commissioning boundaries.
- Routes are failure scenarios grounded in the service inventory/runbooks, not
  a fresh whole-system audit. Every route names host, observations, expected
  result and interpretation. Existing collector signals are reused; uncollected
  application-specific checks remain unknown and require manual evidence/notes.
  No new collector probes, credentials, notification sends or repair actions.
- Generated docs/troubleshooting/extended-app-routes.md from additional-routes.js
  through scripts/export-routes.mjs, giving an offline companion when VM103 or
  the dashboard is down. Original written walkthroughs remain separate.
- 17 model tests pass, including route uniqueness and prevention of inferred
  app health from shared-host passes. Local and live browser checks exercised
  all27 route selections, filtering/no-match, evidence, expandable steps and
  mobile layout. Document targets exist; all five live JS/HTML/CSS assets match
  local bytes. Nginx syntax passed; screenshots inspected.
- Deployed through the existing cached-base Compose build and scoped recreate;
  management bind192.168.20.102:8094 retained. Current image:
  sha256:fe46252a3bc116d3356fb30b3d9ae5f6b837ac7a90d93fba907d49e93a5223b7.
  Prior sources/image ID: /opt/backups/troubleshooting-routes-20260911/;
  rollback image: troubleshooting-dashboard:routes-rollback-20260911.
  Restore saved sources/Dockerfile, tag rollback image as
  troubleshooting-dashboard-troubleshooting-dashboard:latest, then run
  docker compose up -d --no-build --no-deps troubleshooting-dashboard from
  /opt/stacks/troubleshooting-dashboard/. Rollback retained, not exercised.
  Proxmox SSH/collector acceptance and DNS/Homepage promotion remain open.


## 2026-09-11 expanded Windows evidence

- Expanded health_check.ps1 -Full -Json from13 to21 checks. New signals:
  dns_local/dns_public against192.168.10.1, trusted Homepage/vault HTTPS,
  Proxmox8006, workstation-to-cache3142, Immich API and Open WebUI listener.
  Default mode remains12 core probes. JSON timestamps retain explicit timezone.
- HTTP reads headers without redirects; core reachability probes explicitly
  disclaim certificate trust, while tls_trust/vault_tls use normal validation.
  HTTP401 is listener evidence, not login acceptance. Confirmed DNS timeout/
  resolver failure codes fail; unsupported/tool errors remain unknown.
- Offline PowerShell tests load function definitions only and mock HTTP/DNS:
  11 cases pass without probes.17 app model tests pass; local/live browser checks
  imported real fresh Windows JSON and exercised all27 routes. Asset parity and
  Nginx syntax passed. Photos/AI now show their specific listener evidence while
  retaining manual jobs/model/resource checks; exported offline guide refreshed.
- Read-only workstation sample at2026-09-11T15:13:34+01:00:16 PASS /5 FAIL.
  Failed: disconnected camera_01, both direct router DNS queries (ERROR_TIMEOUT),
  vault_tls, and package_cache3142. A separate curl probe to vault.home.local
  timed out resolving its name; this is not proof that Vaultwarden is stopped
  or that its certificate is wrong. Trusted Homepage HTTPS returned200. No
  resolver, trust-store, firewall, auth, package or service repairs were made.
- Next diagnosis: compare workstation DNS source/path and allowed router listener,
  then isolate vault name resolution and cache access. The sample is scoped to
  this management workstation, not proof of every VLAN/client's access.
  Proxmox installed collector and backup acceptance remain blocked by SSH.
- Deployed guidance/routes to existing management-only8094 stack, image
  sha256:8cdac135ea2c7e84c1ea932a6ecb2880c17ec10394de13645802b70d53373e36.
  Windows collector runs from the canonical checkout; no Proxmox deployment.
  Prior app sources/image ID: /opt/backups/troubleshooting-collector-20260911/;
  image tag troubleshooting-dashboard:collector-rollback-20260911. To roll back,
  restore saved additional-routes.js/index.html, tag the retained image as
  troubleshooting-dashboard-troubleshooting-dashboard:latest, and use
  docker compose up -d --no-build --no-deps troubleshooting-dashboard in the
  existing stack directory. Rollback retained, not exercised this pass.


## Homepage troubleshooting preview (2026-09-11)

Owner approved and deployed Tools > Troubleshooting > Troubleshooting Dashboard,
using the existing card style, Preview and Open tab controls. The fixed URL is
`https://homepage.home.local/portal-preview/troubleshooting/`; Nginx proxies only
to `http://192.168.20.102:8094/`. No new DNS alias, listener or firewall rule.
The existing Homepage audience can now access the dashboard through HTTPS;
the direct 8094 management boundary is unchanged. The proxy retains the app's
CSP restrictions, including `connect-src 'none'`, with explicit Homepage frame
ancestors. Direct access still disallows framing. Evidence stays browser-local.

Live Nginx validation and desktop/mobile preview checks passed: all 27 routes
loaded, Open tab points to the fixed URL, and the 390px viewport has no horizontal
overflow in either Homepage or its frame. Browser checks used an explicit local
hostname mapping and ignored TLS errors. A separate curl check returned HTTP200
with certificate validation and revocation checking disabled; this does not
resolve the workstation's existing DNS/revocation issues. Proxmox evidence
acceptance remains open.

Rollback: restore services.yaml and settings.yaml to `/opt/stacks/homepage/config/`
and nginx.conf to `/opt/stacks/homepage/preview-proxy/` from
`/opt/backups/homepage-troubleshooting-20260911/`. Regenerate the proxy config with
`docker exec homepage-preview-proxy /docker-entrypoint.d/20-envsubst-on-templates.sh`,
run `docker exec homepage-preview-proxy nginx -t`, reload Nginx, and restart Homepage.


## DNS and TLS fault isolation (2026-09-11)

Router-local DNS resolves homepage.home.local, vault.home.local and example.com.
The workstation has Mullvad connected with LAN sharing and DNS content blockers;
custom DNS is disabled. Direct router queries time out; TCP DNS also fails.
This strongly suggests the VPN/client DNS path, not missing router records.
No VPN, DNS, trust-store or firewall settings were changed. Choosing local custom
DNS would change the workstation's DNS privacy/filtering behavior and requires
an owner choice. Mullvad's official guide describes custom DNS as replacing its
VPN resolver: https://mullvad.net/en/help/using-mullvad-vpn-app .

A separate live regression was confirmed: Homepage optional.d was empty, so
vault.home.local received Homepage's certificate and content. Restored the
existing tracked vaultwarden.conf.example as optional.d/vaultwarden.conf after
checking the dedicated leaf certificate and loopback8222 health. Nginx validation
passed. Both sites returned200 with browser TLS validation enabled using explicit
hostname mapping; vault /alive returned200 with its correct SNI certificate,
HSTS and no-framing headers. This repairs HTTPS routing, not account onboarding.
The initial IP-forced200 before repair was Homepage, not proof of Vaultwarden.
The exact date/cause of the missing optional file is unknown.

Windows curl's strict revocation mode reports CRYPT_E_NO_REVOCATION_CHECK on the
local CA leaf. curl --ssl-revoke-best-effort passes chain/name validation with
explicit hostname mapping, but does not establish revocation availability.
Chromium's normal trust checks pass. No global verification bypass was installed.

HTTP collector failures now categorize DNS, network, TLS and timeout errors without
exporting raw exception data. Trust-check wording explicitly excludes revocation
availability. DNS/TLS app guidance now includes VPN/client comparison and SNI
isolation; the offline extended guide was regenerated. Offline tests:11 HTTP/DNS
contracts,6 failure categories,17 app model cases. Live desktop/mobile browser smoke passed against the deployed app, including
all27 routes. Homepage and Vaultwarden both returned200 in Chromium with normal
TLS verification and explicit DNS mapping.

Vault rollback evidence: /opt/backups/vault-route-repair-20260911/ includes the
previous empty optional.d and effective config. Removing only the restored
optional.d/vaultwarden.conf and validating/reloading Nginx reproduces the prior
broken route; do not use that as routine recovery. App rollback:
/opt/backups/troubleshooting-dns-tls-20260911/additional-routes.js and image tag
troubleshooting-dashboard:dns-tls-rollback-20260911. Current image config ID:
sha256:621fb8011f14485d6c9e6d0791b7e15b739418fd1c96824c508bc7bc3d4c0ad8.
