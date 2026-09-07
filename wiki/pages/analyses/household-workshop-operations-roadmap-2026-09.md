---
title: "Household, Workshop and Operations Product Roadmap"
category: analysis
tags: [roadmap, household, workshop, diagnostics, resilience, ventsys]
created: 2026-09-05
updated: 2026-09-06
sources: [project-readme, project-todo]
status: active
---

# Analysis: Household, Workshop and Operations Product Roadmap

**Query:** Add the selected household, workshop, diagnostic, resilience and
VentSys feature ideas to the project roadmap.
**Date:** 2026-09-05

## Findings

The proposed [[household-workshop-operations-roadmap|canonical roadmap]] puts
a small, read-only evidence contract first. That prevents a daily household
screen or diagnostic view from hiding unavailable sources, treating stale data
as current, or placing service credentials in a browser.

The first product work is a “Today at Home” view which deep-links to existing
owners: GardenKeeper for garden work, Grocy for stock and shopping, Mealie for
recipes, Recomp Tracker for training, and the operational stack for incidents.
It is not a new source of truth and has no mutation controls in its first
release. [[entities/household-hub]], [[entities/home-assistant]]

The staged [[entities/troubleshooting-dashboard]] gains a later dependency
view and recovery-evidence board only after it has accepted a real Proxmox
snapshot. They remain read-only: a common host, NFS mount or DNS path is an
evidence-backed possible dependency, not an automatic diagnosis or a
remediation trigger.

Food workflows start only with representative inventory. Recipe suggestions
can make expiry data useful, but a recipe selection must not silently alter
Grocy inventory, import a recipe or create a Recomp entry. The corresponding
read/write confirmation boundaries remain with their owning applications.

Workshop inventory is a separate evaluation. It begins with one cabinet or
Gridfinity zone and supports locations, parts, images, documentation links and
QR labels. Filament/AMS integration waits for accepted P1S and Bambuddy paths.
VentSys commissioning is likewise hardware-gated and will record bench and
installation evidence without adding an alternate safety-control path.

The roadmap also retains later candidates for performance evidence,
configuration drift review, garden-to-kitchen handoffs, maintenance scheduling,
storage forecasting, document management, job receipts and power continuity.
Each is independently gated so it cannot bypass service placement, backup,
access or safety review.

## Implementation update — 2026-09-06

[[entities/home-operations-workbench]] now implements a local, fixture-driven
proof of concept for the selected phases. It normalizes schema 1.0 evidence,
keeps unknown and planned-offline states visible, identifies only *possible*
shared dependencies, and treats backup, integrity, and restore evidence as
separate facts. It also presents meal availability and a visual-only VentSys
commissioning checklist.

The workbench is not deployed and makes no network request to household
systems. It has no credentials, storage, Home Assistant or MQTT control, and
does not write to Grocy, Mealie, GardenKeeper, Recomp, or Household Hub. The
local test suite and desktop/mobile browser smoke checks passed; a live release
still requires an adapter contract, service placement, authentication and
recovery acceptance.

## Open questions

- [x] Define the Phase 0 schema and fixture set for the local proof of concept.
- [ ] Decide the live adapter and placement model before any authenticated collection.
- [ ] Complete the Troubleshooting Dashboard's real Proxmox backup-snapshot acceptance.
- [ ] Seed and validate a small Grocy stock pilot before recipe suggestions.
- [ ] Evaluate HomeBox against a purpose-built workshop app with one real workshop zone.
- [ ] Keep VentSys commissioning behind physical hardware and existing safety acceptance.

## Sources used

[[sources/project-readme]], [[sources/project-todo]],
[[entities/household-hub]], [[entities/home-assistant]],
[[entities/troubleshooting-dashboard]], [[entities/docker-host]],
[[entities/ventsys]], [[entities/home-operations-workbench]]
