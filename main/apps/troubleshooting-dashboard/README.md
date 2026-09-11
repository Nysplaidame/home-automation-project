# Troubleshooting Dashboard POC

Read-only, dependency-free dashboard for turning a visible symptom into an
ordered diagnostic sequence. The catalog now has **27 routes** in five areas:

- Network and access: portal, Internet/Wi-Fi, DNS, trusted HTTPS and remote access.
- Hosts and storage: Proxmox guests, shared Docker resources, NAS and two backup layers.
- Home and devices: HA, automations, cameras, P1S, local AI/voice, VentSys and phone relay.
- Monitoring and maintenance: missing graphs, notifications and package updates.
- Applications and data: Immich, media libraries, downloads/VPN, sync, household APIs and vault.

Use search or the area selector; category groups keep the list manageable.
The [original written walkthroughs](../../docs/troubleshooting/diagnostic-walkthroughs.md)
and [22 extended routes](../../docs/troubleshooting/extended-app-routes.md) remain
available in the local vault if the dashboard's own Docker host is down.
Extended offline routes are generated from `additional-routes.js` with
`node main/apps/troubleshooting-dashboard/scripts/export-routes.mjs` from the
repository root. Update that source and regenerate rather than editing both.

The catalog describes potential failures, not a fresh audit of every service.
Shared host/listener passes never stand in for application or data acceptance.
The existing collectors cover only some signals; route-specific missing evidence
requires the manual checks and operator notes. Checking Collected never changes
an imported status. No new probes, credentials or remediation controls were added.

## Data boundary

The POC does not probe the network or execute commands. Load the JSON produced
on the Proxmox host:

```sh
main/scripts/monitoring/health_check.sh --json > health.json
```

Or from a Windows management workstation:

```powershell
main\scripts\monitoring\health_check.ps1 -Full -Json > health.json
```

The file is parsed in the browser and is not uploaded. Unknown or skipped
checks stay `Needs evidence`; they are never treated as healthy.

The Windows collector includes the observed endpoint or HTTP result beside each
status. The Proxmox collector supplies the guest-mount and per-guest backup
freshness checks that cannot be established from the management workstation.
For a backup incident, use the Proxmox JSON snapshot rather than treating the
missing Windows signals as a failure or a pass.

### Evidence age and recorded device state

The deployed 2026-09-10 update requires an explicit timezone and a snapshot no
older than 36 hours before using checks to assess a symptom. The review window
is a conservative common UI default, not a service uptime guarantee or proof
of backup integrity. Missing, ambiguous, invalid, future or stale timestamps
show `Needs evidence`; the original pass/fail observations remain visible and
are included in incident reports. Age is rechecked every minute while open.

The updated Windows source emits an ISO timestamp with its UTC offset; the
Proxmox source emits UTC with `Z`. Older installed collectors still omit the
timezone. Recollect using the updated collector, or establish the actual
collection timezone before preparing a compatible import; never infer it
from the browser timezone. Updating these source files does not deploy them.

Only the built-in example selector enables example mode. The UI and copied
report identify examples as non-live evidence; an imported JSON `example`
field cannot bypass age checks. Loading or clearing a snapshot resets the
collected-step checkboxes while retaining operator notes.

Camera and P1S investigations display the dated September7 disconnected /
uncommissioned baseline as context. This does not convert a failed check to
a pass, and does not suppress Frigate, storage, Bambuddy or MQTT failures.
Confirm current device state before using that recorded context.

This update is deployed to management port8094 and passed live desktop/mobile
checks with a fresh Windows snapshot (12 pass, one disconnected camera fail).
The Windows collector runs from the canonical checkout; no matching Windows
scheduled collector was found. Proxmox still denies the workstation SSH key,
so its installed collector has not been updated. The existing Proxmox evidence
acceptance and DNS/Homepage promotion gates remain open.

Deployment rollback files are in
`/opt/backups/troubleshooting-evidence-20260910/` on VM103, with the old image
retained as `troubleshooting-dashboard:rollback-20260910`. The stack still
publishes only `192.168.20.102:8094`, and its bridge has IPv6 disabled. A
pre-existing IPv6 DOCKER-USER Tailscale RETURN rule for8094 needs reconciliation
before any IPv6 publication; this update did not change firewall rules.

### Proxmox snapshot acceptance

The remaining acceptance gate requires a fresh read-only export from the
existing Proxmox host collector. On the Proxmox host, use its installed
`/usr/local/sbin/home-automation-health-check --json` command and copy the
result to the management workstation. Do not run a backup, restore, restart,
or configuration change for this evidence collection.

Validate the copied file before importing it into the staged dashboard:

```powershell
python main\scripts\monitoring\validate_proxmox_snapshot.py .\proxmox-health.json --require-pass
```

Acceptance also requires a snapshot no older than 36 hours and a valid timezone.
For a legacy local timestamp, add `--timestamp-offset +01:00` only if that was
the Proxmox collector's actual offset when collected. Missing, stale, ambiguous
or future-dated evidence cannot pass. Integrity and restore proof remain separate.

The validator accepts only a `Proxmox host` snapshot with the CT 111/114
capacity evidence, the CT 111 recording-mount source, and fresh archives for
VMs 100/102/103 and CTs 111/114. It reports statuses only and never prints
collector detail. A non-passing result is evidence to investigate; it is not a
reason to change the dashboard's `Needs evidence` state.

The interface highlights the first failed or missing evidence signal and names
the host on which each displayed command must be run. These are instructions
only: copying a command never runs it.

## Local verification

```powershell
cd main/apps/troubleshooting-dashboard
npm run check
docker compose config
```

Serve the directory with any static server for browser review. The staged
container binds only `192.168.20.102:8094`, uses reserved explicit bridge
`10.240.32.0/24`, and requires the tracked management-only `DOCKER-USER`
policy. It has no DNS, Homepage, LAN, monitoring or Tailscale exposure.

## Deliberate v1 exclusions

- no arbitrary shell input or command execution;
- no automatic restart, firewall, restore or remediation controls;
- no credentials, tokens or embedded authenticated monitoring APIs;
- no persistence beyond the current browser tab;
- no claim that a missing signal is healthy.

## Staged live state

- [x] Five diagnostic sequences reviewed with explicit execution hosts.
- [x] Staged deployment on management-only port `8094`.
- [x] Desktop/mobile acceptance using a real 13/13 Windows snapshot.
- [x] Stop/start rollback proof and post-rollback access revalidation.
- [ ] Real Proxmox snapshot acceptance for mount and backup-freshness evidence.
- [ ] Explicit approval for any DNS name or Homepage placement.

The pre-change live firewall and audit scripts are retained on VM 103 under
`/opt/backups/troubleshooting-dashboard-20260825T1518Z/`.

## Readability update (2026-09-10)

The interface uses a numbered choose/add/check/review journey, 18px body text,
16px supporting evidence and wrapped commands. Evidence follows the checks
instead of squeezing them into a three-column layout. Each check expands to
show its execution host, command, expected result and interpretation; the
first is open initially. Search and area groups keep problem choices manageable on phones.

The upload area includes the Windows snapshot command, explains that failed
checks can still be imported, and names the separate Proxmox collection gate.
Files stay in the browser; gathering evidence remains an operator-run step.


## Extended route deployment (2026-09-11)

All 27 routes are deployed on the existing management-only port8094. Verification
passed 17 model tests, local/live desktop-mobile checks selecting every route,
search/category/no-match behavior, and live asset parity. The app remains
import-only; these guided routes do not add network probes or prove that the
manual-only signals passed. Rollback sources and image ID are retained under
`/opt/backups/troubleshooting-routes-20260911/`, with image tag
`troubleshooting-dashboard:routes-rollback-20260911`.
