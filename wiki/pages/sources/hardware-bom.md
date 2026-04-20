---
title: "Hardware Bill of Materials"
category: source
tags: [hardware, bom, procurement, budget]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: Hardware Bill of Materials

**Original file:** `home-automation-safety/bill-of-materials/hardware/parts-list.md`
**Date ingested:** 2026-04-07
**Type:** hardware specification / procurement list

## Summary

Complete hardware BOM for the home automation project, organised by system. Total estimated cost £792–£1,328. As of Sep 2025, only the GL-MT6000 router and PrintAirPipe STL files (£29) had been purchased. Everything else was in procurement planning.

## Key Takeaways

- Core compute: MINIX NEO Z350-0dB (i3-N350, 32GB DDR4) — Proxmox host for all VMs
- Network: GL-MT6000 (✅ owned); 8-port PoE+ switch (⏳ needed for cameras)
- CCTV: 4× PoE cameras (H.265, 4MP, IR) — model TBD; CAT6 outdoor cable
- NAS: Pi 4 8GB + 2× 4TB USB 3.0 HDDs (RAID 1) + microSD
- Safety note: hardware failsafe relay recommended for VentSys fan circuit (software-only failsafe is insufficient for safety-critical systems)
- Budget: Phase 1 £240 (safety-critical), Phase 2 £320, Phase 3 £400, Phase 4 £240+
- All components require UL/CE certification; outdoor network components need IP54+ rating

## Entities Mentioned

[[entities/minix-neo-z350]], [[entities/gl-mt6000]], [[entities/raspberry-pi-nas]], [[entities/ventsys]], [[entities/frigate]]

## Concepts Mentioned

[[concepts/printairpipe]]

## Contradictions / Updates

BOM references 32GB RAM for MINIX; README says 16GB. Verify actual installed RAM when hardware is on hand.
