---
title: Written Diagnostic Walkthroughs
description: Offline companion to the five read-only troubleshooting app investigations
tags: [troubleshooting, diagnostics, evidence, diagrams]
created: 2026-09-10
modified: 2026-09-10
type: runbook
status: active
---

# Written Diagnostic Walkthroughs

Use these instructions with or without the troubleshooting app. The app orders
evidence; it does not probe hosts, execute commands or repair services. Keep
this page available in the local vault if docker-host is unavailable.
The [cross-system reference](troubleshooting_reference.md) covers additional
systems and [Phase 12](../install/phases/12-validation-troubleshooting.md)
covers rebuild acceptance and controlled recovery drills.

## Recorded baseline and evidence

The [canonical inventory](../reference/current-live-state.md) records the
September 7 baseline. Cameras and the Zyxel were deliberately disconnected,
P1S was uncommissioned, and VentSys hardware acceptance remained pending.
Confirm whether the owner has changed that state before interpreting a failure.
Frigate, storage, Bambuddy and MQTT must still be assessed independently.

The dashboard is staged at [management port 8094](http://192.168.20.102:8094/).
Its September 10 evidence-age improvements are deployed and live-tested;
see the [app deployment record](../../apps/troubleshooting-dashboard/README.md).
DNS/Homepage promotion and fresh Proxmox snapshot acceptance remain open.
The Windows collector uses the canonical checkout. The Proxmox installed
collector update remains blocked by SSH access. The deployment also recorded
a pre-existing IPv6 Tailscale rule discrepancy; the current service publishes
IPv4 only and its bridge has IPv6 disabled.

For each incident record time with timezone, source host/network, symptom,
expected result, actual result and last passing layer. Preserve errors before
restarting anything. Remove credentials and authenticated URLs from reports.

Run on: Windows management workstation, PowerShell from the repository root.

```powershell
& .\main\scripts\monitoring\health_check.ps1 -Full -Json |
    Set-Content -Encoding UTF8 .\health.json
```

Expected result: a JSON snapshot with timestamp, source, checks and observed
details. A nonzero collector exit or failed check is evidence, not a reason to
discard the file. Import the file in the app if available, or inspect it locally.
The Windows snapshot cannot establish Proxmox guest archives or CT mount state.

Run on: Proxmox host shell, using the installed collector.

```sh
/usr/local/sbin/home-automation-health-check --json > /tmp/proxmox-health.json
```

Copy the resulting file to the management workstation through an established
authenticated path. If SSH is denied, record the access gap and use the host
console or restore approved access; do not substitute a Windows snapshot.

Run on: Windows management workstation, PowerShell from the repository root.

```powershell
python main/scripts/monitoring/validate_proxmox_snapshot.py ./proxmox-health.json --require-pass
```

Expected result for acceptance: exit zero with required mount, capacity and
per-guest archive checks passing. Evidence must be at most 36 hours old with
an explicit timezone. Older installed collectors may omit the offset; the
validator's `--timestamp-offset` option is appropriate only when the actual
collection offset is independently known. Do not infer it from browser time.
Missing, skipped, ambiguous, future or stale evidence means **Needs evidence**.
A fresh passing backup check proves archive freshness, not integrity or restore.

## 1. Homepage unavailable or one card fails

Diagrams: [DNS/NTP](../diagrams/network/dns-ntp-flow.mermaid),
[remote access](../diagrams/network/remote-access-flow.mermaid),
[service placement](../diagrams/infrastructure/docker-host-service-placement.mermaid).

Run on: Windows HomeAdmin workstation in PowerShell.

```powershell
Resolve-DnsName homepage.home.local -Server 192.168.10.1 -DnsOnly
Test-NetConnection 192.168.20.102 -Port 443
Invoke-WebRequest https://homepage.home.local/ -UseBasicParsing
```

Expected: local DNS returns `192.168.20.102`, TCP succeeds, and HTTPS loads
without a trust warning. Off-site OnePlus split DNS instead targets
`100.94.122.18`; use its approved fixed proxies, not an assumed admin host route.
If TCP works but HTTPS fails, record the certificate/name/error and use the
[TLS guide](../procedures/ssl_tls_guide.md). A TLS-bypassed probe does not prove trust.

Run on: docker-host VM 103 over SSH.

```sh
cd /opt/stacks/homepage
docker compose ps
docker compose logs --tail=60 homepage preview-proxy
docker compose exec -T preview-proxy nginx -t
curl -I http://127.0.0.1:3001/
```

Expected: both services running, proxy configuration valid, raw Homepage
responding. Raw success with public HTTPS failure narrows the problem to
DNS/TLS/proxy/access. If only one card fails, compare its fixed upstream and
port with the [service matrix](../reference/service-matrix.md); test that
upstream from docker-host. qBittorrent uses `/portal-preview/qbittorrent/`.
Follow [Homepage recovery](../install/services/homepage.md) after identifying
the failed layer; do not broaden routes to make a card work.

## 2. Home Assistant unavailable

Diagrams: [guest placement](../diagrams/infrastructure/proxmox-guests-and-backups.mermaid)
and [access policy](../diagrams/network/security-access-flow.mermaid).

Run on: Windows HomeAdmin workstation in PowerShell.

```powershell
Test-NetConnection 192.168.20.101 -Port 8123
Invoke-WebRequest https://192.168.20.101:8123/ -UseBasicParsing
```

Expected: TCP and trusted HTTPS succeed. If TCP fails, check VM 100's state and
console in Proxmox before changing HA. If HTTPS responds but a dashboard fails,
inspect its browser error and authentication separately.

Run on: Home Assistant Terminal & SSH add-on, if available.

```sh
ha core info
ha core check
ha core logs
```

Expected: core running and configuration valid. For a restart loop, preserve
the first named YAML/package error and repair that file through the add-on or
the documented recovery path; do not restart every service. A Proxmox host
shell is not the HA add-on shell. See
[HA install/recovery](../install/phases/03-home-assistant.md).

## 3. Camera unavailable or recordings missing

Diagrams: [physical camera path](../diagrams/network/physical-port-and-cabling.mermaid)
and [recording storage](../diagrams/storage/storage-and-backup-flow.mermaid).

First establish whether cameras remain intentionally disconnected. For an
intended-live camera, use its recorded address, PoE port and stream from the
[cabling inventory](../reference/physical-port-and-cabling.md). `.21` is camera 1,
`.22` Gate and `.23` Patio; `.24` is future scope.

Run on: Frigate CT 111 shell.

```sh
nc -zv 192.168.30.21 554
cd /opt/frigate
docker compose ps
docker compose logs --tail=60 frigate
findmnt -T /mnt/nas/frigate
```

Expected for a connected camera: RTSP listener reachable and Frigate running.
A timeout narrows investigation to power/link/VLAN/firewall; a reachable
listener with stream errors needs path/auth/codec investigation. Avoid putting
an RTSP password in command history or incident reports.

Run on: Proxmox host shell.

```sh
findmnt -T /mnt/omv/frigate
df -h /mnt/omv/frigate
pct config 111 | grep '^mp'
```

Expected: `192.168.40.50:/export/frigate` mounted on the host and passed into
CT 111 at `/mnt/nas/frigate`. A local root filesystem returned by `findmnt -T`
is not the required NFS mount. Do not enable NFS mounts inside CT 111. If the
mount is correct but writes fail, check the documented UID `100000` ACL.
Disconnected cameras cannot prove new recording/playback acceptance. Follow
[Frigate recovery](../install/phases/04-frigate.md) and the
[camera preflight](../procedures/frigate_camera_preflight_checklist.md).

## 4. P1S telemetry missing

Diagrams: [VLAN placement](../diagrams/network/vlan_architecture_clean.mermaid)
and [docker-host placement](../diagrams/infrastructure/docker-host-service-placement.mermaid).

First confirm P1S has actually been commissioned on HomePrinters/VLAN35.
`192.168.35.200` is the intended address, not proof of a live printer.

Run on: docker-host VM 103 shell.

```sh
cd /opt/stacks/bambuddy
docker compose ps
docker compose logs --tail=60 bambuddy
nc -zv 192.168.35.200 8883
nc -zv 192.168.35.200 21
nc -zv 192.168.20.101 8883
```

Expected after commissioning: Bambuddy running, printer control listeners and
HA MQTT TLS reachable. Check actual DHCP reservation, printer access settings
and credentials when connectivity succeeds but authentication fails. Then
check Bambuddy MQTT publishing and the HA package's real serial/topic mapping.
HA and Bambuddy share VLAN20; the router does not enforce that local path.
Bambuddy stays on host networking until the printer path is proven; do not
promote its prepared bridge as an incident workaround. See the
[workload guide](../../scripts/setup/proxmox/bambuddy_vm_setup_guide.md).

## 5. Backup freshness uncertain

Diagrams: [guest backups](../diagrams/infrastructure/proxmox-guests-and-backups.mermaid)
and [storage/restore paths](../diagrams/storage/storage-and-backup-flow.mermaid).

Use the Proxmox snapshot described above for VMs 100/102/103 and CTs 111/114.
Windows endpoint success and VM 103's application backup timer cannot establish
those guest archives.

Run on: Proxmox host shell.

```sh
pvesm status
pvesm list omv-backups --content backup
```

Expected: `omv-backups` active and an archive for each required guest within
the policy window. Check each guest separately; a successful VM job does not
prove the CT job succeeded. Review the Proxmox task log for missing archives,
including the CT job's required host-local `tmpdir=/var/tmp` setting.
For locks or leftover snapshots use the
[backup guard](../../scripts/backup/proxmox-lxc-backup-guard.sh) in read-only
mode first. Never clear a lock while a backup/snapshot task is active.

For VM 103 application backups, use the separate
[backup strategy](../../scripts/backup/backup_strategy.md) and current job
record. The September 7 report established job success, but fresh Proxmox
archives and OMV SMART were unverified because direct SSH access was denied.
Restore testing must use the strategy's isolated target and a separate
maintenance plan. See the [resilience test cards](../audits/2026-07-full-system-audit/08-resilience-test-cards.md).

## Diagram viewing and closing an incident

The links above open canonical Mermaid sources without a running service.
Use the [diagram library](../diagrams/README.md) or
[rendered viewer](https://homepage.home.local:8195/) for pan/zoom and source
inspection when available. The viewer's direct LAN endpoint is
[port 8092](http://192.168.20.102:8092/).

Record the failed layer, bounded correction, repeated original check, and any
remaining unknowns in the current handoff. Update the canonical state only for
newly established facts. A copied report or a green endpoint alone does not
close functional, restore or hardware acceptance.
