---
title: Obico ML API
description: Local Bambuddy print-failure detection on CT 114
tags: [install, local-ai, bambuddy, obico, 3d-printing]
---

# Obico ML API for Bambuddy

Run only Obico's `ml_api` component on CT 114 `llm-host`.  Bambuddy owns printer
control and supplies temporary camera snapshots; the ML service returns a
failure score.  This is LAN-only and does not require an Obico account.

The tracked stack and operator procedure are at
[`configs/local-ai/obico-ml-api`](../../../configs/local-ai/obico-ml-api/README.md).

## Acceptance boundary

1. CT 114 has 6 cores and 28 GiB RAM; the Docker service is limited to 2 CPUs
   and 5 GiB.
2. Only VM 103 `docker-host` can reach `192.168.20.104:3333`; no router or
   Tailscale exposure is added.
3. Bambuddy's External URL is `http://192.168.20.102:8000`, reachable by CT
   114, and its Test control succeeds.
4. A normal supervised print reaches `Safe` with an increasing frame count.
5. Start notification-only.  Pause and power-off responses require separate
   observed-print and physical-safety acceptance.
