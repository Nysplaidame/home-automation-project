---
title: July 2026 Audit Scope and Baseline
created: 2026-07-09
modified: 2026-07-09
type: audit-evidence
status: active
---

# Audit Scope and Baseline

## Repository baseline

| Item | Recorded value |
|---|---|
| Active checkout | `E:\home-automation-project` |
| Branch | `main` |
| Commit | `b8db1c1b588bbe586ac0c367673e828c84984a64` |
| Commit subject | `Add Mermaid viewer and align HomeIoT routing` |
| Baseline worktree | Clean and equal to `origin/main` |
| Tracked files | 530 |
| Non-`.git` worktree files at first count | 19,083 |
| Generated exhaustive inventory count | 19,122, including the new audit generator and partial first-pass output |
| Tracked/relevant inventory at generation | 532 |
| Closing exhaustive inventory | 23,156 files after audit evidence, ignored Mermaid dependencies/build output, generated audit bytecode, and the expanded post-baseline overlay |
| Closing tracked/relevant inventory | 576 artifacts; ignored generated/vendor trees remain separately hashed in the exhaustive ledger |
| Host timezone | Europe/London |

The audit was originally planned against commit `3eb6995` plus a dirty overlay.
The operator then explicitly requested that the entire overlay be committed and
pushed. Commit `b8db1c1` is therefore the immutable discovery baseline and
contains that former overlay plus the router validator alignment required for
the renamed `HomeIoT` interface/zone.

## Local tooling

| Tool | Version / state |
|---|---|
| Git | 2.55.0.windows.2 |
| Python | 3.13.13 |
| PowerShell | 7.6.1 |
| OpenSSH | OpenSSH_for_Windows_9.5p1 / LibreSSL 3.8.2 |
| Node.js | Not on the normal PATH at baseline; bundled-runtime check pending |
| GitHub CLI | Not installed; not required for read-only audit discovery |

## Authorized discovery boundary

- Repository, Git history, wiki, archives, generated/vendor artifacts, and
  physical-design assets.
- OpenWrt router, managed switch, upstream-router dependencies, Tailscale and
  dormant WireGuard intent.
- Proxmox, all active and rollback guests, HA, Frigate/CCTV, local AI/voice,
  docker-host applications, monitoring, OMV/storage, backups, clients, and
  pending physical integrations.
- Existing credentials may be used for read-only evidence. Secret values must
  not enter this evidence pack.

## Safety boundary

The following remain unexecuted until separately approved: service or host
restarts, firewall/ACL or route mutations, certificate/trust changes, switch or
upstream-router changes, production mount interruption, restore into a
production identity, camera outage, MQTT interruption, DNS outage, and any
physical VentSys actuation. Their test cards may be written during discovery.

If discovery reveals an apparent active compromise, imminent data-loss
condition, or unsafe physical state, work stops and the operator is notified
before containment or remediation.

## Sanitization

Raw commands are selected to avoid secret output. When a configuration must be
compared, the audit records field presence, redacted structure, hashes, counts,
versions, or allowlisted values. Raw sensitive captures are not committed.

## Post-baseline overlay

After the clean baseline was frozen, the worktree gained a Mermaid Viewer
dependency/build/packaging overlay plus this audit pack. During final
housekeeping, concurrent work added a docker-host stack template and a service-
matrix row. The overlay is not proven deployed and is not treated as baseline
truth. Both tracked-file modifications and relevant untracked/ignored files are
enumerated in the closing inventories; ignored dependency/build content is
hashed but not proposed for Git by the audit.
