---
title: "MINIX NEO Z350-0dB"
category: entity
tags: [hardware, compute, proxmox, minipc]
created: 2026-04-07
updated: 2026-08-25
sources: [project-readme, hardware-bom]
status: superseded
---

# MINIX NEO Z350-0dB

**Type:** device — compute hardware (Mini PC)
**Status:** Superseded early hardware plan; not the production host
**Related:** [[entities/minisforum-m1-pro-125h]], [[entities/proxmox]]

## Overview

This was the compute platform described by the early BOM and April wiki ingest.
It is not the production Proxmox host. The live system uses a
[[entities/minisforum-m1-pro-125h]]; retain this page only to explain historical
source references.

## Key Properties

- CPU: Intel i3-N350
- RAM: 16GB DDR4 (BOM lists 32GB — verify actual on receipt)
- Storage: 512GB M.2 PCIe Gen3 SSD
- Form factor: fanless / passively cooled
- OS: Proxmox VE (bare metal)
- Network: single NIC (`enp1s0`), connected to GL-MT6000 `lan1` as a VLAN trunk

The specifications below describe the superseded candidate, not live state:

- CPU: Intel i3-N350
- Form factor: fanless / passively cooled
- Earlier storage/RAM claims were never accepted as production evidence.

## Change Log

- 2026-04-07: Page created from README + BOM ingest
- 2026-08-25: Marked superseded after reconciliation with the production MINISFORUM host.
