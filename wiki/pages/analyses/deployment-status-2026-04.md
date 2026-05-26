---
title: "Analysis: Project Deployment Status (April 2026)"
category: analysis
tags: [status, deployment, phases]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Analysis: Project Deployment Status (April 2026)

**Query:** What is the current state of the project — what's done, what's pending, what's blocked?
**Date:** 2026-04-07
**Sources Used:** [[sources/project-readme]], [[sources/project-todo]], [[sources/hardware-bom]]

---

## Summary

All software, configs, and documentation are complete. The project is blocked at physical deployment: the router has not been switched over to OpenWrt VLAN mode. Nothing that depends on network segmentation (Proxmox, HA, Frigate, VentSys) can be deployed until the router is live.

---

## Phase-by-Phase Status

| Phase | Status | Blocker |
|---|---|---|
| 1 — Network | ✅ Configs complete / ⏳ Not deployed | Must flash GL-MT6000 with phases 1–8 |
| 2 — Core infra (Proxmox, HA, Frigate) | ⏳ Pending | Router must be live first |
| 3 — VentSys | ⏳ Hardware not purchased | Router + HA needed; then hardware |
| 4 — Storage (NAS) | ⏳ Hardware not purchased | Now superseded by OMV NAS direction |
| 5 — CCTV | ⏳ Camera models TBD | Router + Frigate VM needed; then cameras |
| 6 — Security hardening (TLS, HTTPS) | ⏳ Not started | All above must be deployed first |

---

## Immediate Next Actions (in order)

1. Deploy [[entities/gl-mt6000]] — run `router_setup_complete.md` phases 1–8
2. Run `network_testing_guide.md` — validate all 14 pass/fail criteria
3. Install Proxmox on [[entities/minix-neo-z350]] — run `proxmox_setup_guide.md`
4. Run `configs/proxmox/vm-setup.sh` — creates VMs 100 + 101
5. Note VM MAC addresses → fill into `dhcp-config.conf`
6. Deploy [[entities/home-assistant]] via `ha_vm_setup_guide.md`; copy VentSys packages + dashboard
7. Deploy [[entities/frigate]] + [[entities/bambuddy]] via `frigate_vm_setup_guide.md`

---

## Hardware Still to Purchase

| Item | For | Est. Cost |
|---|---|---|
| OMV-capable NAS hardware + storage | [[entities/openmediavault-nas]] | TBD |
| 8-port PoE+ switch | Phase 5 CCTV | ~£80 |
| 4× PoE cameras (model TBD) | Phase 5 CCTV | ~£240 |
| 4+ ESP32 DevKit boards | [[entities/ventsys]] sensors | ~£50 |
| BME680, DS18B20, MQ-135, MQ-2, SDP610 sensors | [[entities/ventsys]] | ~£80 |
| MG90S servos + IRLZ44N MOSFET | [[entities/ventsys]] | ~£40 |
| PLA+ and PLA-HT filament | [[concepts/printairpipe]] | ~£50 |

---

## Follow-up Questions

- [ ] Which PoE camera models are compatible with Frigate (H.265, RTSP, sub-stream support)?
- [ ] Is the hardware failsafe relay for VentSys fan going to be implemented before or after initial VentSys deployment?
- [ ] Will MQTT TLS migration happen before or after initial VentSys bring-up?
