---
title: July 2026 Claim and Roadmap Traceability
created: 2026-07-10
modified: 2026-07-10
type: audit-evidence
status: discovery-frozen
---

# Claim and Roadmap Traceability

The generated TODO and roadmap ledgers enumerate every checklist row. This
ledger records the material claims whose disposition changes operational or
security decisions.

| Claim | Documentation/source | Live/observed evidence | Disposition |
|---|---|---|---|
| HA still needs HTTPS enabled | `TO-DO.md` open item | HA serves native HTTPS with a local-CA certificate | Contradicted; task is stale |
| Frigate is not Tailscale-advertised | Service/access matrices | Docker host advertises `192.168.30.20/32`; tailnet approval not visible | Contradicted locally; control plane blocked |
| Frigate has no user path until cameras arrive | Access matrix | One camera and desktop/mobile CCTV views are live | Contradicted |
| Frigate OMV cutover is pending | `START-HERE.md` and service matrix | Current recordings are written to OMV NFS | Contradicted; old CT recordings remain |
| Frigate uses `CCTV/` on OMV | Storage documentation | Current mount uses md0 `frigate`; legacy `CCTV` export persists | Contradicted |
| Cameras/MQTT are disabled | Shared-iGPU decision context | One camera and Frigate MQTT TLS are live; object detection is disabled | Partially obsolete |
| Docker app-data backup is unproved | Older task/documentation state | Current daily job and recent dumps exist for four apps | Verified for four apps only |
| Docker application data is covered | General backup narrative | Household Hub, Bambuddy, and Immich lack app-level coverage | Contradicted |
| HA automatic backup includes add-ons | Backup strategy | Live automatic selection excludes add-ons | Contradicted |
| HA native HTTPS health is broken | Older host-side health assumptions | Current host health uses HTTPS and passes | Obsolete, but health scope remains incomplete |
| Estate health is all green | Proxmox five-minute health output | Immich and Transfer Portal are failed; CT 111 is near full; Kuma has three down | Contradicted / false-green |
| VLAN 50 is renamed HomeIoT | Current router source and recent commit | Live UCI/firewall still uses `iot_sensors` internally | Source/live split; deployment blocked |
| Router full tests represent live correctness | Router test naming | New-name tests fail while old-name live checks pass | Contradicted by identifier drift |
| Transfer Portal is deployed | Install/operations docs | Unit is enabled but cannot bind obsolete IP and restart-loops | Failed deployment |
| OMV configuration is backed up | Backup design intent and `/export/configs` alias | Export alias source is deleted; direct configs directory is empty | Contradicted |
| NFS exports are canonical and minimal | Service/storage docs | Duplicate, legacy, deleted-source, and `no_root_squash` exports remain | Contradicted |
| Monitoring covers local AI | Monitoring narrative | Retired Ollama is monitored; active llama.cpp chat API is not | Contradicted |
| HA monitor is healthy | Monitoring intent | Kuma probes stale HTTP and reports HA down while native HTTPS works | Contradicted |
| Watchtower is monitor-only and source-aligned | Canonical Compose/docs | Live Watchtower Compose differs; behaviour was not mutated/tested | Unexplained drift |
| Every deployed Docker service is reproducible | Rebuild intent | Household Hub/GardenKeeper live source lacks Git provenance; Bambuddy/Household Hub lack canonical stacks | Contradicted |
| AI cannot directly control safety-critical logic | Durable architecture rule | No direct safety path was found, but prompt-injection/authorization negative tests were not run | Design verified; behaviour blocked |
| Voice tool routing is deterministic and safe | Custom component intent | Logs show misrouting and an unconfirmed bounded recipe-import write attempt | Contradicted |
| Fail2ban coverage is current | Security documentation references | No complete live estate-wide Fail2ban map or negative test was produced | Unverified |
| Managed switch config is persisted | Installation intent | Login unavailable; VLAN/PVID/trunk/PoE/startup config not read | Blocked |
| Certificates are consistently trusted | Certificate/access docs | HA works; router/PVE/switch are untrusted; Frigate differs between Chrome and Schannel | Contradicted |
| Restore readiness follows from fresh archives | Backup/status documentation | Fresh archives exist, but no representative isolated restore was run | Contradicted methodology |
| VentSys is operationally certifiable | Design and build source | Hardware is absent; only source contracts and ESPHome validation passed | Blocked physical acceptance |
| Current browser viewer is functional | Mermaid Viewer baseline | Baseline hangs on a missing module; post-baseline overlay supplies a local build but is not deployed | Baseline contradicted; overlay pending validation |
| Physical resilience is addressed | Architecture/roadmap | No proved UPS topology, shutdown policy, power-cycle result, or common-mode test | Omitted / blocked |
| Sonarr is part of the governed estate | Live HA app list | Started and boot-auto but absent from canonical service/access/backup docs | Unexplained live component |

## Disposition rules

- `Verified` requires current observation or a reproducible test.
- `Contradicted` means the canonical claim must be repaired after discovery is
  frozen; it does not authorize rewriting history.
- `Planned` or `blocked` is not a pass.
- Historical documents remain historical and should gain context rather than
  being rewritten to pretend the old state never existed.
