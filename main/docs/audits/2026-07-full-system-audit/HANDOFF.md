---
title: July 2026 Full Audit Handoff
created: 2026-07-10
modified: 2026-07-10
type: handoff
status: discovery-frozen-wave-0-in-progress
---

# Full Audit Handoff

## Boundary

Discovery is frozen against baseline commit
`b8db1c1b588bbe586ac0c367673e828c84984a64`. The baseline itself made no live
changes. Subsequent, explicitly approved Wave 0 remediation has changed the
live state; the completed items and their rollback points are recorded below.

The worktree contains the audit pack plus a separate post-baseline Mermaid
Viewer build/packaging overlay, docker-host stack template, and service-matrix
change. Preserve both workstreams. Do not represent the Mermaid overlay as
deployed or as part of the clean baseline without fresh live evidence.

## Decision and first actions

Decision is `not certified`. Begin only with a separately approved Wave 0:

1. rotate/remove the tracked Obsidian REST credential/private key and decide
   Git-history treatment;
2. verify the old CT 111 local-recording path and delete only that disposable
   pre-OMV footage; do not touch current OMV recordings or Frigate DB/config;
3. prepare mount-safe Immich recovery with database/media proof;
4. repair or stop the Transfer Portal restart loop in a bounded window.

F-003 was resolved on 2026-07-10 without a router deployment. The repository's
internal VLAN 50 interface, DHCP scope, firewall zone, Wi-Fi interface, compiler,
lint, and live validators now use `iot_sensors`, matching the router; the public
SSID remains `HomeIoT`. Standard router deployment still requires its normal
approved maintenance window and recovery path.

## 2026-07-10 Wave 0 execution record

The operator approved the CT 111 footage cleanup and bounded Immich recovery.

- **F-004 — CT 111 capacity:** Before deletion, Frigate was healthy, the NFS
  recording target had active writes, and the exact local-only target was
  confirmed as `/opt/frigate/storage/recordings` on CT 111's ext4 root.
  Only that directory's pre-OMV content was deleted (`20G` to `4.0K`). Root
  use fell from `93%` (`2.2G` free) to `26%` (`23G` free), while NFS writes
  continued. `fstrim /` was not permitted in the unprivileged CT, so the thin
  LV still reports `99.81%` allocation; guest capacity is contained, but thin
  allocation monitoring/host-side reclamation remains open.
- **F-002 — Immich recovery:** A fresh PostgreSQL dump was written to the
  mounted OMV docker-host backup share before mount changes:
  `immich/postgres-20260710T105140Z.sql.gz` (`16,398,666` bytes; SHA-256
  `f0caed21115a7d838c0ec2561a39319e1a690a18db44557b04d42bf09a82dba6`). The
  prior `/etc/fstab` was retained on VM 103 as
  `/etc/fstab.pre-immich-recovery-20260710T105258Z`. The failed unbounded NFS
  line was replaced with a bounded NFSv3 systemd automount. The intended
  `/export/immich` media tree mounted with six top-level entries; the server
  recovered from its loop without an extra manual restart, returned HTTP 200
  from the local API, and stayed `healthy` with restart count `5276` over the
  follow-up window. Reboot and storage-loss negative tests remain separately
  approval-gated.
- **F-001 — Obsidian REST secret:** Deferred by the operator. It remains
  tracked and present in four history commits; no rotation, Git rewrite, or
  tracking change was performed.
- **F-008 — Transfer Portal:** The earlier OMV recovery record identified the
  SSH account as `root`, rather than the web-console `admin` account. Fresh
  validation found both intended transfer mounts active and no active job or
  rsync process, but the service was still restart-looping on the obsolete
  `192.168.10.147:8088` bind. Before repair, its unit, config, and jobs SQLite
  database were copied under
  `/var/lib/transferportal/remediation-20260710T111338Z`. The unit now binds
  only to `192.168.40.50:8088`; it is active with zero restarts, has the
  expected HTTP `303` login redirect, and no post-repair bind errors. The
  existing destination ACL preserved all entries and gained only
  `transferportal:rwx` plus its default ACL, allowing the service account to
  read the source and write the destination. An authenticated browse/preview
  and a deliberately approved test transfer remain unperformed.

## 2026-07-10 source/live reconciliation record

- **F-003 — VLAN 50 identity drift:** Live UCI confirmed a healthy
  `iot_sensors` interface (`br-lan.50`, `192.168.50.1`), DHCP scope, firewall
  zone/rules, Wi-Fi network attachment, and nft chains, while retaining the
  public `HomeIoT` SSID. Repository internals were aligned to that established
  identifier; no router state was written. Router-source lint and preview
  compilation passed, then the live read-only validators passed cleanly:
  `test.ps1 -RouterIp 192.168.10.1 -Profile full` `PASS=87 WARN=0 FAIL=0` and
  `test-connectivity.ps1 -RouterIp 192.168.10.1 -Profile full`
  `PASS=85 WARN=0 FAIL=0`.

- **F-010 — Docker-published-port enforcement:** Live inspection proved that
  UFW was not enforcing several Docker-published paths: docker-host had no
  `DOCKER-USER` rules for Homepage (`3001`), Mermaid Viewer (`8092`), or
  Household Hub (`8100`/`8101`), while monitoring VM 102 had an empty chain.
  HA could reach all four docker-host ports before remediation. The canonical
  docker-host firewall now mirrors the existing declared source policy for
  those ports, including IPv6 Tailscale-only rules for all observed published
  Docker services; its live rollback snapshots are under
  `/root/docker-host-firewall-remediation-20260710T142018Z` and
  `/root/docker-host-firewall-remediation-20260710T142333Z`. VM 102 now has
  enabled `monitoring-docker-firewall.service`, sourced from
  `configs/grafana/system/`, with explicit defaults-deny for Grafana/Kuma,
  InfluxDB, and syslog. Its rollback snapshot is
  `/root/monitoring-docker-firewall-remediation-20260710T142119Z`.
  Retests proved HA is denied Homepage, Mermaid Viewer, and Household Hub UI
  while retaining its approved Household Hub API and monitoring paths;
  docker-host is denied Grafana/Kuma but retains InfluxDB export; management
  retains its documented paths. The separate owner-supervised Tailscale ACL
  remediation is recorded immediately below.

- **F-010 — Tailscale owner-side remediation (2026-07-10):** The docker-host
  router is connected and has exactly four approved routes:
  `192.168.20.101/32`, `192.168.30.20/32`, `192.168.40.50/32`, and
  `192.168.60.10/32`; no route was awaiting approval. The blanket allow-all
  grant was replaced, with owner approval, by one grant from the sole approved
  mobile node, `oneplus-9-pro` (`100.105.216.6`), to only those four routes on
  all IP protocols. The standard self-only Tailscale SSH check and existing
  Funnel node attribute were retained. This is default-deny for every other
  Tailnet source and destination. The console accepted and saved the policy
  with no pending changes. The pre-change emergency rollback policy is
  `tailscale-acl-prechange-2026-07-10.hujson`; restoring it would re-enable
  unrestricted Tailnet connectivity. On 2026-07-11, the operator verified the
  approved routes from `oneplus-9-pro`; the access test passed. If the phone is
  re-enrolled and its Tailnet IPv4 changes, this source address must be updated
  deliberately.

- **F-019 — Frigate source/live reconciliation (2026-07-11):** Read-only live
  validation found the Proxmox host NFS mount and CT 111 bind mount both backed
  by `192.168.40.50:/export/frigate`; the Frigate container is healthy and
  maps `/mnt/nas/frigate` to `/media/frigate/recordings`. Recent MP4 segments
  exist on that OMV-backed path. The live effective camera configuration has
  `detect.enabled: false`, 10 fps ingest, and recording/snapshots enabled;
  the API reported 10.1 camera/process fps, zero detection fps, and detection
  disabled. Repository source now states the same explicit disabled baseline.
  No service was restarted and detection was not enabled. Any move to object
  detection remains a separate camera/GPU and privacy approval.

- **F-011 — OMV NFS first remediation pass (2026-07-11):** Pre/post rollback
  evidence is retained at `/root/omv-nfs-f011-20260711T223802Z`. Advertised
  paths were reduced from eleven to six: the nonexistent direct `CCTV` export,
  unused direct `immich-db`, stale `/export/ha-backups`, both unused configs
  paths, and CT 111's unusable direct Frigate client entry were removed without
  deleting their underlying data. `/export/frigate` is now exposed only to
  Proxmox `192.168.10.10` with `root_squash`; the UID 100000 ACL remains.
  Proxmox root write was denied, UID 100000 create/delete passed, and CT 111,
  Frigate, HA backups, Immich, docker-host backups, Proxmox backups, NFS, and
  the expanded estate check all remained healthy. The advertised `/export`
  path is OMV's read-only, root-squashed pseudo-root for the two live managed
  children. Proxmox backup, HA backup, docker-host backup and Immich exports
  still use client-restricted `no_root_squash`; their root/mixed-owner write
  contracts require separate service-identity migrations. Full evidence and
  future gates are in `13-nfs-identity-review.md`.

- **F-014 — Health-check remediation (2026-07-11):** The canonical
  `scripts/monitoring/health_check.sh` now checks the live Frigate UI, Immich,
  Transfer Portal, llama.cpp and Open WebUI endpoints in the normal profile.
  On Proxmox it also checks CT 111/114 root usage, proves CT 111's recording
  mount source is `192.168.40.50:/export/frigate`, and enforces a 36-hour
  freshness ceiling for archives of VMs 100/102/103 and CTs 111/114. A
  sandbox-equivalent candidate passed shell parsing and a live read-only JSON
  run with `PASS=26 FAIL=0`. The first implementation used `pct exec` and then
  mount-namespace entry; both were correctly rejected by the hardened systemd
  sandbox and the original installed script was restored. The final version
  reads CT disk counters through the Proxmox API and validates the host-side
  bind source without namespace entry. It is deployed at
  `/usr/local/sbin/home-automation-health-check`; source and live SHA-256 both
  equal `aec4c5bf6c635157c68e9f0af2de12c2fdd2d4374b4eef717823f24ebead2962`.
  The real systemd unit completed with `PASS=28 FAIL=0`, `Result=success` and
  `ExecMainStatus=0`; its timer remains active. Rollback is
  `/usr/local/sbin/home-automation-health-check.pre-f014-20260711T223121Z` and
  all temporary candidates were removed.

- **F-009 — OMV configuration backup (2026-07-11):** A root-only daily backup
  is deployed through `/usr/local/sbin/omv-config-backup` and
  `omv-config-backup.timer`, scheduled for `01:30` with bounded random delay.
  It captures full OMV XML/export/mount/shared-folder evidence under unexported
  md0 `backups/configs/omv-config`. The first valid run
  `20260711T224614Z` passed every entry in its relative SHA-256 ledger; the
  timer is active and the systemd service result is success. The full XML stays
  root-only because it may contain sensitive state. Sanitized rebuild source
  and the current NFS contract are in `configs/omv/`; detailed proof is in
  `14-omv-config-backup.md`. This is a local same-array recovery aid, not an
  independent/off-site copy.

## 2026-07-15 Mermaid Viewer management-access repair

- The operator reported that the internal Mermaid Viewer timed out from the
  management Wi-Fi client `192.168.10.105`. VM 103 and the viewer remained
  reachable, but the deployed `DOCKER-USER` policy for port `8092` allowed
  only `192.168.1.0/24` and `tailscale0`. The approved remediation added the
  narrow `192.168.10.0/24` allow rule to the canonical
  `configs/docker-host/system/docker-host-firewall.sh` source and live
  `/usr/local/sbin/docker-host-firewall.sh`, then restarted the oneshot policy
  service. It is active; an HTTP request from the management client returned
  `200` for `http://192.168.20.102:8092/`. Live rollback copy:
  `/usr/local/sbin/docker-host-firewall.sh.pre-mermaid-mgmt-20260715T205608Z`.

## Required operator inputs

- Switch read-only credentials/session and tailnet owner session.
- Achievable local RPO/RTO choices. Off-site copies and isolated restores have
  been declined due unavailable resources; do not repeatedly reopen that choice.
- Approval for each restore, restart, firewall, route, certificate, NFS,
  camera/GPU, power, or physical test card.
- Retention decision for the old CT 111 recordings.
- Decision to retire, relocate, or govern Sonarr on HAOS.
- VentSys stays design-only until the operator declares it mature enough for
  physical acceptance. No UPS is present or planned.
- **Operator sequencing (2026-07-11):** complete OMV storage/export work and
  other non-credential remediation first. Credential rotation and SSH
  hardening (including F-001/F-016/F-017/F-028/F-029) are explicitly deferred
  to the end of this remediation run.

## Restart point

Read `10-final-correctness-report.md`, then `07-findings.md`, then select one
remediation wave from `09-remediation-backlog.md`. Before any state change,
revalidate only the affected evidence for drift and fill the corresponding card
in `08-resilience-test-cards.md` with operator, approval, timestamps, backup
proof and rollback owner.
