---
title: Audit Findings
created: 2026-06-21
modified: 2026-06-21
type: audit-findings
status: open
---

# Audit Findings

## Critical

### F-001 — Live credential and private key committed to Git

- **Evidence:** `.obsidian/plugins/obsidian-local-rest-api/data.json` is tracked, contains an API key and private-key material, and appears in multiple historical commits.
- **Affected:** repository confidentiality, local REST API, any trust based on the paired certificate/key.
- **Action:** disable/rotate the API key and certificate/key pair first; remove the file from tracking and ignore it; purge it from all Git history and remote copies; audit access logs and collaborators/clones.
- **Validation:** old credentials fail, new credentials work only on intended interfaces, secret scan and full-history scan pass.
- **Dependencies:** coordinated credential rotation and history rewrite.

## High

### F-002 — CT 114 backup failed and left a snapshot lock

- **Evidence:** 2026-06-21 backup log reports `No space left on device`; CT 114 has `snapshot-delete` lock and `vzdump` snapshot. Proxmox root is 79% used with about 20 GiB free. The surviving CT 114 archive is from 2026-06-20.
- **Affected:** llm-host backup freshness, future scheduled backups, host storage safety.
- **Action:** follow Proxmox-supported stale snapshot/lock recovery after confirming no task is active; provide sufficient backup capacity; rerun backup; monitor job result.
- **Validation:** no lock/snapshot remains, fresh archive exists, `zstd -t` passes, sandbox restore boots.
- **Dependencies:** maintenance window and storage decision.

### F-003 — Live VentSys safety scripts conflict with source

- **Evidence:** live package ramps valves over about two seconds to `100`; source uses one direct command and calibrated maximum `50`. The fire-safe path is affected.
- **Affected:** all future physical valves, fire response timing, dashboard/script contract.
- **Action:** block hardware adoption, choose the accepted calibration/timing design, deploy one canonical package, and remove stale copies.
- **Validation:** HA config check, source/live hash equality, MQTT capture, dry test entities, then physical endpoint/timing tests.
- **Dependencies:** safety decision and physical test window.

### F-004 — Four documented ESP8266 smart-plug configurations cannot validate

- **Evidence:** `ventsys_plug_uv1.yaml`, `ventsys_plug_uv2.yaml`, `ventsys_plug_wash_cure.yaml`, and `ventsys_plug_ultrasonic.yaml` fail ESPHome 2026.5.3 validation because `mqtt.certificate_authority` is ESP32-only.
- **Affected:** TLS migration, UV/wash-cure/ultrasonic controls, rebuild claims.
- **Action:** select a supported ESP8266 security/transport design or different hardware before flashing.
- **Validation:** ESPHome config and compile pass; broker authentication and certificate behaviour are tested on isolated hardware.
- **Dependencies:** security design decision.

## Medium

### F-005 — HA source/live drift defeats repository-as-source-of-truth

Live `configuration.yaml` is a small UI-oriented config while source contains additional HTTP, recorder, URL, logging, and security settings. Automations match by lines, but VentSys scripts do not. Reconcile deliberately rather than copying either side blindly.

### F-006 — Backup retention is infeasible on current local storage

The new archive must coexist with the retained archive until pruning; current free space was insufficient for CT 114. Capacity modelling must include worst-case compressed size, temporary snapshot overhead, and safety margin.

### F-007 — Canonical navigation contains stale targets

The wrapper README links an archived/nonexistent current handoff. `PROJECT-INDEX.md` and the main README refer to nonexistent `configs/esphome/printairpipe-controller.yaml`. The wiki also has unresolved entity/concept links. See inventory failures and static link results.

### F-008 — `health_check.sh` produces false failures

It is documented for Proxmox or a management laptop, but depends on Linux `ping`/`nc`; the Git Bash laptop run produced five false negatives. On Proxmox it treats intentionally stopped rollback VM 101 as failure and omits live CTs 111/114.

### F-009 — `_verify.ps1` targets an obsolete path

The script writes to `D:\Other computers\NOT A COMPUTER\...\_check.txt` instead of the active checkout and is not a meaningful system validator.

### F-010 — Container reproducibility and health coverage are weak

Many stacks use `latest`, `main`, or unpinned logical tags; most lack Compose health checks. Dozzle, Homepage, Telegraf, and Watchtower mount the Docker socket, increasing consequence if compromised. This is not an immediate outage but weakens deterministic recovery and least privilege.

### F-011 — Router DNS alias contradicts the service matrix

`router.home.local` resolves to `192.168.1.1` from management, while the canonical matrix records `192.168.10.1`.

### F-012 — Dashboard regression coverage is incomplete and currently blocked

Existing Playwright coverage tests only the solar screensaver. No automated test proves dashboard load cannot publish zeroes after script reordering, entity unavailability is safe, or mobile layouts remain usable. The current code order avoids the known initialization publish path, but the TODO correctly notes it is fragile.

### F-013 — Roadmap vendor verification could not be completed

Official documentation browsing returned HTTP 403 twice. Installed versions and local validators were used, but externally version-sensitive roadmap decisions require a later vendor-doc pass.

### F-014 — Monitoring roadmap contradicts itself

The document says centralized alert routing is “planned but not yet deployed” while later live-state sections and current records say ntfy routing exists. Status prose needs one canonical current-state reference.

### F-015 — ESPHome warnings predict near-term breakage

Three airflow configurations use `Light On/Off`, which ESPHome says becomes an error in 2026.7.0. Several ESP8266 configurations do not declare `min_auth_mode` and currently permit the weaker default.

## Low

### F-016 — Frigate CT has a failed RPC mount unit

The Frigate container is healthy, but `run-rpc_pipefs.mount` is failed. Determine whether it is harmless residue or a future NFS dependency before NAS cutover.

### F-017 — Documentation-only file uses a firmware extension

`configs/esphome/ventsys_main_fan.yaml` intentionally contains comments only and directs operators elsewhere. Tooling reasonably treats it as a broken ESPHome configuration. Rename it to Markdown or make it a valid package/redirect pattern.

