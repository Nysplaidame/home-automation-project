---
title: Phase 12 - Validation Troubleshooting
description: End-to-end acceptance and bounded recovery tests after rebuild
tags: [install, validation, troubleshooting]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: active
---

# Phase 12 - Validation Troubleshooting

## Purpose

Prove that the rebuilt system works from physical link through user workflow,
that access denied by design remains denied, and that every Tier 1 service has a
bounded diagnostic and rollback path.

This phase does not make a partly rebuilt component `live`. Record the last
passing layer and leave the component at `Prepared`, `Installed`, `Configured`,
or `Validated` until all requirements in the
[rebuild state matrix](../reference/rebuild-state-matrix.md) pass.

## Current source-validation blockers

The 2026-08-09 workstation audit found two blockers that must be cleared before
router source can pass final acceptance:

- `lint.py` and the `first-flight` compile report the missing architecture
  invariant `architecture.docker_host_tailscale_egress_rule_present`.
- The `full` compile reports unresolved WireGuard, device-MAC, and Wi-Fi-secret
  placeholders in deploy artifacts.

These are recorded deployment-state failures, not reasons to use broader rules
or invented values. Placeholder-tolerant output may be inspected as a preview,
but it is never a deployable acceptance artifact.

## Runs on

- Admin laptop in an elevated PowerShell terminal for source, DNS, and client
  access tests.
- OpenWrt router over SSH for routing, DNS-forwarder, NTP, and policy checks.
- Proxmox shell for hypervisor, guest, storage, and aggregate health checks.
- Home Assistant Terminal & SSH add-on for HA configuration, mounts, and backup
  checks.
- `docker-host`, Frigate CT, and OMV over SSH for their local checks.
- An approved Tailscale client and an intentionally unapproved client/network
  for positive and negative access tests.

## Prerequisites

- Phases 00-11 are complete or have an explicit blocker and lifecycle state.
- The [service matrix](../../reference/service-matrix.md),
  [access matrix](../../reference/access-matrix.md), and
  [troubleshooting reference](../../troubleshooting/troubleshooting_reference.md)
  are open for comparison.
- A fresh backup exists for every stateful service being tested.
- A maintenance window is active before any stop, fallback, restore, or
  denial-path test that could affect household users.
- The operator knows how to reach OpenWrt through physical `lan5` and can reach
  each host through its local console.

## Stop conditions

Stop the current test and recover the nearest failed layer if any of these
occur:

- the router or management laptop loses its recovery path;
- an expected storage mount disappears while a writer is still running;
- the tested firewall change permits a source marked denied in the access
  matrix;
- a restore is about to target the live production volume rather than an
  isolated destination;
- a command would require putting a password, token, private key, or camera URL
  into terminal history or the evidence bundle.

## 1. Create the acceptance record

For every phase and live service, copy this row into the current handoff or
maintenance record. `Blocked` is a result; a blank cell is not.

| Component | Lifecycle state | Positive proof | Denial proof | Backup/restore proof | Monitoring proof | Rollback proof | Result/time |
|---|---|---|---|---|---|---|---|
| Example | Validated | command or screenshot | source and denied target | isolated restore ID | monitor/event ID | recovery command/result | PASS/BLOCKED, ISO time |

Secrets, session cookies, full environment output, private addresses belonging
to remote clients, and signed media URLs must be redacted before evidence is
stored.

## 2. Validate repository source of truth

Run on: Admin laptop from repository root in PowerShell.

```powershell
Push-Location .\main
python tools/router-deploy/lint.py
python tools/router-deploy/compile.py --profile first-flight
python tools/router-deploy/compile.py --profile full
powershell -NoProfile -File scripts/validation/validate-home-local-dns.ps1 -SkipLive
Pop-Location
```

Expected result after the blockers above are resolved:

- every command exits `0`;
- lint reports no errors;
- both profiles compile without invariant or placeholder failures;
- DNS validation reports the same alias count in OpenWrt and the service
  matrix.

If full deployment inputs are deliberately incomplete, preview the render only.

Run on: Admin laptop from `main/` in PowerShell.

```powershell
python tools/router-deploy/compile.py --profile full --allow-placeholders
```

Expected result: the preview compiles only if all non-placeholder invariants
pass. Label the output `NON-DEPLOYABLE`; do not pass it to `deploy.ps1`.

Recovery path:

1. Read the first failing invariant or file/line group rather than the final
   exit-code message.
2. Correct the canonical config, matrix, or secret input; never edit generated
   output to hide the failure.
3. Re-run lint, then `first-flight`, then `full` in that order.
4. Keep the router phase blocked until all three pass without
   `--allow-placeholders`.

## 3. Validate physical, switching, and IP layers

Before testing applications, check the inventory LEDs, switch port/VLAN
assignment, cable label, and link speed against the Phase 00 inventory. Then
collect a client-side baseline.

Run on: Admin laptop in PowerShell.

```powershell
Get-NetAdapter | Where-Object Status -eq 'Up' |
  Format-Table Name, InterfaceDescription, LinkSpeed
Get-NetIPConfiguration
Test-Connection 192.168.10.1 -Count 2
Test-Connection 192.168.10.10 -Count 2
Test-Connection 192.168.20.101 -Count 2
Test-Connection 192.168.20.102 -Count 2
Test-Connection 192.168.40.50 -Count 2
```

Expected result: the active adapter has the intended DHCP/static address,
gateway, and DNS server. Required management paths respond. A failed ping alone
does not prove a host is down because ICMP may be denied; continue with the
documented TCP check for that target.

Run on: OpenWrt router over SSH.

```sh
ubus call system board
ip -brief link
ip -brief address
ip route show
bridge vlan show
ubus call service list '{"name":"dnsmasq"}'
ubus call service list '{"name":"sysntpd"}'
logread -e dnsmasq | tail -n 30
```

Expected result: expected interfaces are `UP`; bridge VLAN membership matches
the network plan; the default route exists; `dnsmasq` and the configured NTP
service are running; and logs contain no restart loop.

Recovery path: work upward from power/link, switch PVID/tagging, client address,
gateway/route, then firewall. Use physical `lan5` recovery if management access
was lost. Do not flatten VLANs as a diagnostic shortcut.

## 4. Validate DNS and time

Run on: Admin laptop in PowerShell.

```powershell
Resolve-DnsName homepage.home.local -Server 192.168.10.1 -DnsOnly
Resolve-DnsName example.com -Server 192.168.10.1 -DnsOnly
w32tm /stripchart /computer:192.168.10.1 /dataonly /samples:5
Push-Location .\main
powershell -NoProfile -File scripts/validation/validate-home-local-dns.ps1
Pop-Location
```

Expected result: the local name returns the service-matrix address, the public
name resolves through the router, five time samples return without timeout, and
the validation script reports source/live agreement. The exact public address
and time offset vary; success is a valid answer and a stable, small offset.

Recovery path:

1. If both names fail, check client DHCP DNS assignment and router `dnsmasq`.
2. If only the local name fails, compare OpenWrt domain records with the service
   matrix and run the source-only validator.
3. If only public names fail, query the router's configured upstreams from the
   router and inspect AdGuard state; retain the documented router fallback.
4. If time fails, verify router upstream synchronization before debugging HA,
   MQTT TLS, certificates, or cameras. Never disable certificate validation to
   conceal bad time.

## 5. Validate compute and storage hosts

Run on: Proxmox shell.

```sh
pveversion -v
qm list
pct list
pvesm status
systemctl --failed --no-pager
```

Expected result: required VMs/CTs are running, intended stopped rollback
artifacts remain stopped, all required storage is `active`, and there are no
unexpected failed units.

Run on: Home Assistant Terminal & SSH add-on.

```sh
ha core check
ha core info
ha mounts info
ha backups list
```

Expected result: configuration is valid, Core reports `running`, required
network mounts are connected, and at least one recent restorable backup is
listed.

Run on: docker-host over SSH.

```sh
systemctl --failed --no-pager
docker info --format '{{.ServerVersion}}'
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
ss -lntup
findmnt -t nfs,nfs4
tailscale status
tailscale ip -4
```

Expected result: no unexplained failed units, required containers are
`Up`/healthy, listeners match the service matrix, OMV mounts required by live
writers exist, and Tailscale is connected. `tailscale status` is evidence of
peers, not proof that routes or ACLs are safe; test those separately below.

Run on: Frigate CT over SSH.

```sh
cd /opt/frigate
docker compose config --quiet
docker compose ps
findmnt -t nfs,nfs4
docker compose logs --tail=80 frigate
```

Expected result: Compose validates, Frigate is running, its required recording
mount is present, and recent logs contain no restart, authentication, or storage
write loop.

Run on: OMV over SSH.

```sh
findmnt
cat /proc/mdstat
exportfs -v
systemctl --failed --no-pager
```

Expected result: intended data filesystems are mounted, any configured array is
healthy, only documented NFS clients/options are exported, and no unexpected
unit is failed. If this build does not use Linux MD, record `/proc/mdstat` as
`not applicable` rather than inventing an array.

Recovery path: stop dependent writers before repairing a missing storage mount.
Use local console access for a failed host network. Restore a guest or dataset
only into the isolated target defined in Phase 10, validate it, and then make a
separate promotion decision.

## 6. Run the aggregate health check

Run on: Proxmox shell from the repository checkout.

```sh
bash main/scripts/monitoring/health_check.sh
bash main/scripts/monitoring/health_check.sh --json | jq .
```

Expected result: the staged core check exits `0`; human output ends in `ALL OK`;
JSON parses and reports `summary.fail` as `0`. The script accepts HTTP `200`,
`302`, or `401` for a reachable protected UI.

Only include hardware and services that have actually advanced out of parked
state.

Run on: Proxmox shell from the repository checkout.

```sh
bash main/scripts/monitoring/health_check.sh --full
```

Expected result: all deployed camera/printer/VentSys checks pass. Failures for
documented parked devices do not represent a live outage, but they also cannot
be counted as acceptance. Record them as `NOT DEPLOYED` and do not use the full
mode's exit code as a core-service gate until the inventory is deployed.

Recovery path: re-run the one failed protocol check from the same source. Then
test power/link, route, listener, firewall, application health, and auth in that
order. Do not restart every service in response to a single failed probe.

## 7. Prove allowed and denied access paths

Test protocol ports, not just ping, and compare every result with the
[access matrix](../../reference/access-matrix.md).

Run on: approved Tailscale client in PowerShell.

```powershell
tailscale status
Test-NetConnection 192.168.20.101 -Port 8123
Test-NetConnection 192.168.40.50 -Port 443
Test-NetConnection 192.168.60.10 -Port 3000
Test-NetConnection 192.168.60.10 -Port 8086
Test-NetConnection 192.168.10.1 -Port 443
```

Expected result: the three approved host paths succeed. InfluxDB `8086` and
router management `443` fail unless a later, documented matrix decision
explicitly allows that exact source and target.

Run on: an intentionally unapproved Guest/DMZ client in PowerShell.

```powershell
Test-NetConnection 192.168.10.1 -Port 443
Test-NetConnection 192.168.20.101 -Port 8123
Test-NetConnection 192.168.40.50 -Port 443
Test-NetConnection 192.168.30.20 -Port 8971
```

Expected result: all internal/admin paths report
`TcpTestSucceeded : False`. Confirm the same client can still reach the public
internet so a local connectivity failure cannot create a false pass.

Recovery path: if an intended-denied path succeeds, treat it as a security
failure. Capture source, destination, port, and matching firewall counter; remove
or narrow the responsible OpenWrt, Tailscale, UFW, or `DOCKER-USER` rule; then
repeat both the denied test and an adjacent allowed test.

## 8. Tier 1 acceptance and recovery drills

Run each drill from the stated source. A UI screenshot is supplemental evidence,
not a substitute for the command result and recovery proof.

### 8.1 AdGuard Home

Positive path:

Run on: docker-host over SSH.

```sh
cd /opt/stacks/adguard-home
docker compose config --quiet
docker compose ps
ss -lntup | grep -E '192\.168\.20\.102:53|:8080'
```

Expected result: config exits silently with `0`, the container is `Up`, DNS is
bound to the intended host addresses, and the admin listener is present.

Run on: OpenWrt router over SSH.

```sh
nslookup example.com 192.168.20.102
```

Expected result: a public answer returns through AdGuard. An arbitrary address
is acceptable; timeout or `SERVFAIL` is not.

Controlled fallback drill, during a maintenance window:

Run on: docker-host over SSH.

```sh
cd /opt/stacks/adguard-home
docker compose stop
```

Expected result: Compose reports `Stopped` for AdGuard and returns `0`; if it
does not stop cleanly, abort the fallback assertion and diagnose the stack.

Run on: Admin laptop in PowerShell while AdGuard is stopped.

```powershell
Resolve-DnsName example.com -Server 192.168.10.1 -DnsOnly
Test-NetConnection 192.168.20.102 -Port 53
```

Expected result: router DNS still returns a public answer through its documented
fallback, while direct AdGuard port 53 fails.

Run on: docker-host over SSH.

```sh
cd /opt/stacks/adguard-home
docker compose start
docker compose ps
```

Expected result: the container returns `Up`; repeat the router and direct query.

Troubleshooting path: if DNS fails, check port ownership, container logs,
upstream reachability, OpenWrt forwarding choice, then source-scoped firewall
counters. If fallback itself fails, restore the last known-good router DNS
configuration through the Phase 01 recovery path before changing AdGuard data.

### 8.2 Immich

Positive path:

Run on: docker-host over SSH.

```sh
findmnt --target /mnt/omv/immich
cd /opt/stacks/immich
docker compose config --quiet
docker compose ps
docker compose exec -T database sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:2283/
```

Expected result: the target resolves to the intended OMV NFS export, config
exits `0`, required containers are `Up`, PostgreSQL reports `accepting
connections`, and HTTP returns `200` or a documented redirect.

In the UI, upload one disposable photo, open it, confirm its metadata, move it
to trash, restore it, and then permanently delete only that disposable item.
Record the asset name and time; do not use irreplaceable media for acceptance.

Mount-loss recovery drill, without writing to a fallback directory:

Run on: docker-host over SSH.

```sh
cd /opt/stacks/immich
docker compose stop immich-server
findmnt --target /mnt/omv/immich
docker compose start immich-server
docker compose ps
```

Expected result: the writer is stopped before mount diagnosis and is restarted
only because `findmnt` confirms the correct remote filesystem. If the mount is
absent or local, leave the writer stopped, repair/remount NFS, and verify the
remote source before restart.

Troubleshooting path: mount and free space first, then PostgreSQL/Redis health,
server logs, listener/firewall, and browser/auth. Restore database and media as
a matched backup set into an isolated target; never point a restored database
at the live media tree for a trial.

### 8.3 Homepage

Positive path:

Run on: docker-host over SSH.

```sh
cd /opt/stacks/homepage
docker compose config --quiet
docker compose ps
curl -fsS http://127.0.0.1:3001/api/services >/dev/null
curl -fsS http://127.0.0.1:3001/images/portal-background.svg >/dev/null
```

Expected result: config exits `0`, required containers are `Up`, and both local
requests exit `0` without bypassing TLS on the user-facing endpoint.

Run on: Admin laptop in PowerShell with `Home Local CA` trusted.

```powershell
Invoke-WebRequest https://192.168.20.102/api/services -UseBasicParsing
Invoke-WebRequest https://192.168.20.102/images/portal-background.svg -UseBasicParsing
```

Expected result: both requests return `200` with no certificate warning. Check
one desktop and one mobile viewport, every tab, one ordinary link, one preview,
and Reload/Open tab/Close.

Rollback drill:

Run on: docker-host over SSH.

```sh
cd /opt/stacks/homepage
docker compose stop preview-proxy
curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3001/
docker compose start preview-proxy
docker compose ps
```

Expected result: the internal rollback endpoint remains available while the TLS
sidecar is stopped, and the sidecar returns `Up` afterward. This proves recovery
availability; it does not authorize exposing port `3001` more broadly.

Troubleshooting path: validate YAML/Compose, check container logs, use
`/api/revalidate` after config changes, test raw `3001`, then test certificate,
proxy, and source firewall separately. Restore the last known-good config/assets
backup if only the generated page is broken.

### 8.4 Dozzle

Positive and security path:

Run on: docker-host over SSH.

```sh
cd /opt/stacks/dozzle
docker compose config --quiet
docker compose ps
docker inspect dozzle --format '{{range .Mounts}}{{println .Source .Destination .RW}}{{end}}'
curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8081/
```

Expected result: config exits `0`, the container is `Up`, the Docker socket line
ends in `false`, and HTTP returns `200` or a documented auth redirect.

Run on: an intentionally unapproved Guest/DMZ client in PowerShell.

```powershell
Test-NetConnection 192.168.20.102 -Port 8081
```

Expected result: `TcpTestSucceeded : False` while the same test from an approved
admin source succeeds.

Recovery drill:

Run on: docker-host over SSH.

```sh
cd /opt/stacks/dozzle
docker compose stop
docker compose up -d
docker compose logs --tail=30
```

Expected result: Dozzle returns `Up` and logs contain no socket permission or
restart loop. If its socket is writable or exposure is too broad, leave the
stack stopped until Compose and both host-firewall layers are corrected.

Troubleshooting path: inspect the container state/logs, verify the socket exists
and is mounted read-only, verify port `8081`, then compare UFW and
`DOCKER-USER` counters. Do not grant broader socket or network access to repair
an empty log view.

## 9. Verify monitoring and alert recovery

For every Tier 1 service, open its Uptime Kuma monitor and record the latest
successful probe. During the controlled stop drill above, confirm the monitor
changes to `Down` and the approved notification channel receives one alert;
after recovery, confirm `Up` and one recovery notification. Use one service at
a time to avoid alert floods.

If the service is unreachable but its monitor remains green, verify the monitor
source, URL/protocol, timeout, retry count, and whether a reverse proxy is
returning a generic success page. Monitoring is not accepted until it detects
the deliberately induced failure and recovery.

## 10. Close the acceptance record

Record:

- repository commit or working-tree identifier;
- router generated-artifact checksum after a clean compile;
- host/service versions without dumping environment secrets;
- command outputs and UI checks with ISO timestamps and source network;
- expected-denial results;
- backup identifier and isolated restore evidence;
- monitor failure/recovery event;
- rollback result and any remaining blocker.

Update the relevant `HANDOFF-*.md`, this suite's
[INSTALL-TO-DO.md](../INSTALL-TO-DO.md), and canonical matrix when live state
materially changes. Update the wiki only after canonical project documents are
correct.

## Completion checklist

- [ ] Router lint and both compile profiles pass without placeholder overrides.
- [ ] Source and live `home.local` DNS records agree.
- [ ] Physical, VLAN, IP, DNS, time, compute, and storage checks pass.
- [ ] Staged aggregate health reports zero failures.
- [ ] Every intended Tailscale path passes and every sampled denied path fails.
- [ ] AdGuard positive, fallback, monitor, and recovery checks pass.
- [ ] Immich mount, database, disposable-media, backup/restore, and recovery checks pass.
- [ ] Homepage HTTPS, responsive UI, rollback endpoint, monitor, and recovery checks pass.
- [ ] Dozzle read-only socket, source denial, monitor, and recovery checks pass.
- [ ] Every live component has a completed lifecycle/evidence row.
- [ ] No failure was concealed with a broad route, firewall bypass, disabled TLS verification, or fabricated placeholder.
