---
title: Roadmap assessment - 2026-09-16
type: assessment
status: current
created: 2026-09-16
---

# Roadmap assessment - September 16

## Scope and conclusion

Assessment of canonical roadmap, task list, live inventory, installation coverage,
app READMEs and latest dated handoff evidence. This is not a fresh whole-estate
runtime audit. Recent thread evidence includes live Proxmox/archive and dashboard
checks September14-16. Other service claims rely on their cited dated records.

The project has a working service foundation, substantially stronger recovery
proof and a usable diagnostic app. Most integrated household products remain
local prototypes. Do not express this as one completion percentage: live,
written, tested and physically commissioned are different milestones.

## Product phases

| Phase | Current position | Remaining release work |
|---|---|---|
| 0 Evidence contract | Local versioned schema, fixtures and offline Windows/Proxmox adapters; real diagnostic imports proven | Authenticated live adapters, hosting and production acceptance for the workbench |
| 1 Today at Home | Local read-only prototype | Real garden/stock/meals/training data, source freshness and deployed mobile daily flow |
| 2A Troubleshooting | Separate live27-route app; Homepage preview, readable UI, fresh Proxmox import and Windows collector | Cross-service dependency graph and bounded incident history; manual-only routes still need evidence |
| 2B Recovery board | Local prototype plus growing real recovery records | Curated evidence integration, deployed board and offline emergency pack; full guest restore proof |
| 3 Cooking/Recomp | Local fixture-based prototype | Representative Grocy inventory, recipe/unit mapping, bounded read-only pilot; explicit write design for later logging |
| 4 Workshop inventory | Evaluation stage | Choose record owner/application, one-zone pilot, labels, exports and restore proof |
| 5 VentSys | Software/configuration and command-free prototype; no physical acceptance | Hardware, assembly, calibration, TLS adoption, restart behavior and end-to-end safety tests |
| Later capabilities | Individually parked | Prioritize only against a concrete user need; do not deploy all candidates |

The six service candidates remain Paperless-ngx, Actual Budget, Scrypted,
Portainer, local registry mirror and Node-RED. Their parked state is intentional.

## Foundations and recent gains

- Core router/Proxmox/HA/Docker/NAS/monitoring and household services are deployed.
  This does not mean every integration has current functional acceptance.
- Homepage carries troubleshooting and a consistently styled direct Vaultwarden
  link. Vault framing protection is retained. Local hosts entries preserve Mullvad
  DNS/filtering. Vault onboarding/2FA/recovery decisions remain separate.
- All11 canonical Mermaid diagrams were simplified and published.
- Dedicated Proxmox SSH now works. Required capacity/mount/backup-age checks and
  actual dashboard browser import passed. Five September15 archives passed their
  respective VMA or decompression/tar checks; VM102 restore is planned, not executed.
- GardenKeeper backup error propagation was repaired and tested; isolated DB/API
  recovery passed. Upload/worker/full workflow recovery and source provenance remain.
- Hub coordinated multi-store checkpoint/isolated restore passed; it is one-off.
  Recurring coordinated coverage is still needed.
- Ten executable images were preserved; all six GardenKeeper/Hub application images
  also rebuilt offline from preserved source/dependencies according to September16
  records. No production application image replacement is implied.
- Watchtower-to-ntfy report delivery and update-count formatting were repaired.
  Phone receipt and the next corrected scheduled report still need acceptance.
- Installation coverage is42 entries:36 Written,6 Candidate. This is documentation
  coverage, not proof of a blank-hardware rebuild.

## Priority gaps

1. Recovery: isolated guest boot/application test, recurring coordinated Hub backup,
   GardenKeeper uploads and integration/full-system recovery. Archive readability
   does not establish application consistency or disaster recovery.
2. Storage/update operations: fresh OMV SMART evidence; CT114 package path and
   security-update status need a fresh bounded diagnosis. The last recorded failure
   must not be presented as a new September16 measurement. Docker root capacity
   needs attention during recovery builds (latest build record12GB free).
3. Monitoring: end-user phone delivery and next scheduled count; separate independent
   observer/alert behavior from dashboards merely being reachable.
4. Product integration: choose/develop one small read-only live slice before growing
   the application list. Today at Home has the clearest daily household outcome;
   recovery readiness has the most reusable evidence already available.
5. Hardware: cameras/Zyxel deliberately disconnected; P1S uncommissioned; VentSys
   unbuilt. Hive application acceptance remains unresolved in the inventory.
6. Security: coordinated credential hardening, remaining Fail2ban/update work and
   the documented direct8094 IPv6 exception need their own bounded treatment.

## Roadmap accuracy

The product roadmap still showed Proxmox evidence as a blocker and all Phase2
work as local only; corrected in this assessment. The workbench remains local,
while the separate troubleshooting app is live. Do not merge their status claims.

Older TO-DO rows still list Watchtower delivery and SearXNG recovery as wholly
unresolved even though later records close portions. The install coverage table
still lists Proxmox/access and coordinated Hub recovery gaps already addressed.
The live inventory begins with dated September7/10 failures that are superseded
later. Historical records can stay, but current action rows need scoped updates.
Hardware quantities/segments and the older 'Immediate next actions' list also
need reconciliation before procurement or physical deployment.

At review, remote fetch succeeded and the branch was one commit ahead of origin;
uncommitted router/documentation work also exists. Preserve that separate work.
This assessment does not certify those changes or merge/deploy them.

## Recommended sequence

1. Complete the isolated monitoring VM102 restore drill already documented.
2. Turn proven component recovery into repeatable operations: coordinated backup,
   missing uploads, storage-health evidence and notification receipt.
3. Prepare a bounded live read-only product release, preferably Today at Home in
   the existing Hub after placement/adapter contracts are decided; alternatively
   publish recovery readiness from curated evidence first if operational visibility
   is the immediate priority.
4. Pilot accurate Grocy stock and one workshop zone with the owner.
5. Resume hardware commissioning when equipment and physical acceptance are ready.

Agent work can cover test plans, adapters against fixtures, read-only diagnosis,
runbook reconciliation and bounded software implementation. Owner participation
is needed for physical commissioning, representative household inventory, phone
receipt, vault account/recovery choices and purchase/deployment preferences.

## Sources

- [Product roadmap](../procedures/household-workshop-operations-roadmap.md)
- [Task list](../../TO-DO.md)
- [Current live state](../reference/current-live-state.md)
- [Current handoff](../../HANDOFF-2026-07-27-portal-services.md)
- [Installation coverage](../install/INSTALL-TO-DO.md)
- [Workbench scope](../../apps/home-operations-workbench/README.md)
- [Troubleshooting scope](../../apps/troubleshooting-dashboard/README.md)
