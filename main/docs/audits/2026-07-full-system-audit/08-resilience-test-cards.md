---
title: July 2026 Resilience and Negative Test Cards
created: 2026-07-10
modified: 2026-07-10
type: audit-test-plan
status: approval-gated
---

# Resilience and Negative Test Cards

No card below was executed during discovery. Each requires a named operator,
rollback owner, fresh timestamped approval, current backup proof, monitoring
watch, and a log of temporary state. Stop immediately for unexpected cross-VLAN
reachability, data writes to a fallback path, safety-related actuation, loss of
the management path, or inability to start rollback within two minutes.

## RC-01 — VLAN allow and deny matrix

- **Approval / maximum outage:** Firewall test approval; 10 minutes.
- **Preconditions:** Saved OpenWrt config, console/recovery path, source/live
  identifier decision, test clients in Management/HomeAdmin/HomeIoT/Guest.
- **Actions / expected:** Probe every documented allow and representative deny,
  including HomeIoT MQTT TLS allow and external DNS/internet deny. No rule
  change is needed for observation; any temporary rule requires separate approval.
- **Operator / rollback owner:** Network operator / local-console operator.
- **Stop / rollback:** Stop on any unexpected allow or management loss; remove
  temporary rules atomically and restore saved packages.
- **Restoration evidence:** Rule hashes, client DHCP/DNS/MQTT state, all
  temporary handles absent, health baseline restored.

## RC-02 — DNS enforcement and bypass

- **Approval / maximum outage:** DNS test approval; 5 minutes.
- **Preconditions:** Current resolver health, local cache cleared only on test
  client, known internal/external names, packet capture location.
- **Actions / expected:** Verify approved resolver works; direct public DNS on
  UDP/TCP 53 and encrypted-DNS policy paths behave exactly as documented.
- **Operator / rollback owner:** Network operator / DNS operator.
- **Stop / rollback:** Stop if more than the test client loses resolution;
  restore client DNS and remove captures/routes.
- **Restoration evidence:** Normal resolver succeeds, bypass result recorded,
  no temporary client or router state remains.

## RC-03 — Tailscale denial and route withdrawal

- **Approval / maximum outage:** Tailnet policy and route approval; 10 minutes.
- **Preconditions:** Exported policy, owner/MFA present, second management path,
  exact four `/32` approvals recorded.
- **Actions / expected:** From authorized and unauthorized identities test each
  `/32`/port; withdraw one noncritical route and confirm only that route fails;
  restore approval and verify access.
- **Operator / rollback owner:** Tailnet owner / local network operator.
- **Stop / rollback:** Stop on broader loss or unexpected access; restore saved
  policy and route approval.
- **Restoration evidence:** Policy hash, approval screenshot/export, client
  route table and positive/negative results equal baseline.

## RC-04 — Dormant WireGuard fallback

- **Approval / maximum outage:** VPN fallback approval; 10 minutes.
- **Preconditions:** Current keys/endpoint ownership verified without exposing
  keys, narrow routes, Tailscale remains available as rollback.
- **Actions / expected:** Activate on a test client only, prove the intended
  management target and denies, then deactivate.
- **Operator / rollback owner:** Network operator / tailnet operator.
- **Stop / rollback:** Stop on route conflict or broad LAN access; remove test
  peer/routes and revoke the temporary peer if created.
- **Restoration evidence:** Client route table returns to baseline and no new
  peer/listener/firewall state remains.

## RC-05 — Certificate trust, expiry, and rollback

- **Approval / maximum outage:** Test endpoint may be isolated; production
  replacement needs fresh approval; 10 minutes per endpoint.
- **Preconditions:** Old certificate/key backup, CA chain, client matrix,
  alternate management path, synthetic short-expiry test endpoint.
- **Actions / expected:** Chrome, Schannel, mobile/PWA and scripted clients
  accept valid chains, reject wrong SAN/expired certs, and alert before expiry.
- **Operator / rollback owner:** PKI owner / service owner.
- **Stop / rollback:** Never replace production until synthetic tests pass;
  restore old pair and listener config on client failure.
- **Restoration evidence:** Fingerprints and client results recorded; no test CA
  or trust anchor remains installed.

## RC-06 — Monitoring and notification failure path

- **Approval / maximum outage:** Noncritical monitoring test; 10 minutes.
- **Preconditions:** Operator watching independent channel, test-only endpoint,
  alert routing/quiet-hours captured.
- **Actions / expected:** Fail a synthetic endpoint, then ntfy/primary monitor;
  verify detection, escalation, deduplication, recovery, and independent backstop.
- **Operator / rollback owner:** Monitoring owner / infrastructure operator.
- **Stop / rollback:** Stop if alert storm or production notification impact;
  re-enable test endpoints and delete test events.
- **Restoration evidence:** Recovery notifications received, monitor states
  green, test records tagged and temporary monitor removed.

## RC-07 — Noncritical container restart

- **Approval / maximum outage:** Service-owner approval; 10 minutes.
- **Preconditions:** Select stateless/noncritical container, config/digest and
  data backup captured, dependent clients idle.
- **Actions / expected:** Restart once; health transition, restart policy,
  dependency reconnection, log quality, and monitoring must behave as designed.
- **Operator / rollback owner:** Docker operator / app owner.
- **Stop / rollback:** Stop if dependencies cascade or data migrates; roll back
  to recorded image/config and restore app data if necessary.
- **Restoration evidence:** Original digest/config active, health stable, no
  unexpected restart count or orphaned container.

## RC-08 — Isolated VM and CT restore

**Disposition:** Not scheduled; unavailable resources. Retained as the unmet
certification gate and future reference.

- **Approval / maximum outage:** Restore approval; no production outage;
  30-minute initial gate per guest, extend only by approval.
- **Preconditions:** Latest active-guest Zstandard stream checks are complete;
  additionally inspect archive contents, provide spare storage and new guest IDs,
  bridge disconnected/no production NIC, MACs and secrets quarantined.
- **Actions / expected:** Inspect one archive per guest class; restore one VM
  and one CT, validate filesystem/config/application offline, then destroy.
- **Operator / rollback owner:** Proxmox operator / storage owner.
- **Stop / rollback:** Stop before attaching production networks or mounts;
  destroy guest/snapshot/volume and revoke test credentials.
- **Restoration evidence:** New IDs absent, volumes and snapshots removed,
  storage returned to baseline, restore log and elapsed RTO retained.

## RC-09 — Application and database restore

**Disposition:** Not scheduled; unavailable isolated resources. Retained as an
accepted residual-risk test card.

- **Approval / maximum outage:** Isolated restore approval; 30 minutes per
  representative dataset, no production NIC.
- **Preconditions:** Fresh dumps, isolated volumes/network, synthetic accounts,
  expected row/document/hash manifest.
- **Actions / expected:** Restore SQLite, PostgreSQL, CouchDB, Qdrant/config and
  media metadata; application-level read checks match manifests.
- **Operator / rollback owner:** App owners / Docker operator.
- **Stop / rollback:** Stop on any attempt to contact production services;
  remove containers, volumes, mounts, accounts and certificates.
- **Restoration evidence:** Object counts/hashes pass and all isolated state is
  enumerated then removed.

## RC-10 — MQTT interruption and replay in a test namespace

- **Approval / maximum outage:** Test namespace preferred; production broker
  interruption needs fresh approval; 10 minutes.
- **Preconditions:** Synthetic topics/clients, retained-message inventory,
  emergency logic proven independent, no physical actuators subscribed.
- **Actions / expected:** Interrupt synthetic client/broker path, publish
  retained/non-retained events, reconnect, and verify replay/idempotence.
- **Operator / rollback owner:** HA/MQTT owner / network operator.
- **Stop / rollback:** Stop on production topic or actuator activity; revoke
  test credentials and purge test retained topics.
- **Restoration evidence:** Test namespace empty, client list normal, no stale
  retained command, automations/entities at baseline.

## RC-11 — Home Assistant restart safety

- **Approval / maximum outage:** Fresh explicit HA restart approval; 10 minutes.
- **Preconditions:** Current HA and VM backups, config check, automation state
  inventory, manual controls and local access available.
- **Actions / expected:** Approved restart; physical/safety outputs remain
  fail-safe, integrations reconnect, newest conversation code activation is
  proved, and alerts recover.
- **Operator / rollback owner:** HA owner / Proxmox operator.
- **Stop / rollback:** Stop on unsafe output or failed boot; disable affected
  integration and restore known-good HA/VM state.
- **Restoration evidence:** Entity availability, automation trace, app states,
  MQTT sessions and client access equal baseline; temporary debug logging off.

## RC-12 — Camera outage and recovery

- **Approval / maximum outage:** Camera/PoE change approval; 15 minutes.
- **Preconditions:** One-camera maintenance notice, recording proof, no active
  incident, switch port identity confirmed, privacy rules captured.
- **Actions / expected:** Isolate test camera, verify HA/Frigate/monitor alert,
  no local storage fallback, restore and prove stream/recording continuity.
- **Operator / rollback owner:** CCTV owner / switch operator.
- **Stop / rollback:** Restore immediately if another camera/service is affected
  or switch identity is uncertain.
- **Restoration evidence:** New recording files, live stream, MQTT entities,
  alerts and switch port state normal; no temporary rule remains.

## RC-13 — Concurrent iGPU and memory load

- **Approval / maximum outage:** Camera/GPU window; 15 minutes.
- **Preconditions:** Temperature/memory/latency baselines, hard load limits,
  stop command ready, recording and voice owners present.
- **Actions / expected:** Generate bounded AI chat/embedding/voice load while
  Frigate processes the camera; extrapolate and later test six-camera target.
- **Operator / rollback owner:** AI owner / Proxmox operator.
- **Stop / rollback:** Stop at agreed temperature, available-memory, latency,
  dropped-frame, OOM or recording thresholds; terminate load only.
- **Restoration evidence:** GPU/process/memory stats return to baseline, no OOM,
  recordings continuous, all voice services healthy.

## RC-14 — Storage unavailability behaviour

- **Approval / maximum outage:** Production NFS interruption requires fresh
  explicit approval; 10 minutes per noncritical test. Use isolated namespace first.
- **Preconditions:** Current backups, mount dependency map, no active transfers,
  local fallback paths guarded read-only/marker-checked.
- **Actions / expected:** Withdraw an isolated NFS target; apps stop/degrade
  safely, alert, and do not write to local fallback. Production Immich/Frigate
  tests follow only after fixes.
- **Operator / rollback owner:** OMV owner / service owner.
- **Stop / rollback:** Restore NFS immediately on local writes, database errors,
  or unrelated client impact; do not force unmount production.
- **Restoration evidence:** Mount and markers correct, no fallback files, app
  health and data counts pass, temporary export/mount removed.

## RC-15 — Switch, upstream router, and power recovery

**Disposition:** Switch/upstream recovery may be revisited, but UPS-runtime and
automated-shutdown portions are not applicable because no UPS is planned.

- **Approval / maximum outage:** Fresh explicit physical/network approval;
  bounded 15 minutes initially.
- **Preconditions:** Running/startup exports, local consoles, UPS/load inventory,
  backups, outage notice, boot-order checklist.
- **Actions / expected:** Separately test switch power-cycle, upstream-router
  recovery, UPS alarm/runtime, and orderly shutdown/startup propagation.
- **Operator / rollback owner:** Physical network owner / infrastructure owner.
- **Stop / rollback:** Stop if running/startup config differs, storage cannot
  shut down cleanly, or outage exceeds bound; restore power/config and boot
  only the minimum management plane.
- **Restoration evidence:** Config hashes persist; VLAN/PoE/trunks, routes,
  storage, guests, clocks, monitoring and alerts return in documented order.

## RC-16 — VentSys physical acceptance

**Disposition:** Deferred until VentSys hardware and design maturity justify
formal physical acceptance.

- **Approval / maximum outage:** Fresh explicit physical actuation approval;
  time bound defined after hardware risk assessment.
- **Preconditions:** Hardware exists; schematic/BOM peer review, isolation,
  fusing, emergency stop, manual override and calibrated instruments available.
- **Actions / expected:** Cold boot, brownout, sensor open/short, Wi-Fi/MQTT/HA
  loss, retained-message replay, manual override and emergency-state tests.
- **Operator / rollback owner:** Qualified physical-system operator / safety owner.
- **Stop / rollback:** Emergency stop on unexpected actuator movement,
  temperature/current limit, loss of isolation or inability to override.
- **Restoration evidence:** De-energized/normal state verified physically,
  retained test commands purged, calibration and signed acceptance attached.
