---
title: July 2026 Static Test Record
created: 2026-07-10
modified: 2026-07-10
type: audit-evidence
status: discovery-frozen
---

# Static Test Record

All commands in this record were local, non-deploying checks. A pass means only
that the stated test passed; it does not establish deployed correctness.

## Repository-wide results

| Area | Result | Evidence / limit |
|---|---|---|
| Project verification suite | Pass | `main/_verify.ps1` completed successfully. |
| Router lint | Pass | Source structure and validator rules passed. |
| Router first-flight preview | Pass | Safe preview generated without deployment. |
| Router full preview | Pass | Safe full intent compilation generated without deployment. |
| Router strict compilation | Expected fail / deployment blocked | 35 unresolved MAC-address or deployment placeholders remain. |
| PowerShell parsing | Pass | Every tracked `.ps1` parsed without a syntax error. |
| Shell parsing | Pass | Every tracked shell script passed `bash -n` using Git for Windows Bash. |
| Transfer Portal tests | Pass | 35 `pytest` tests passed. Live service correctness is separate and failed. |
| VentSys contract checks | Pass | 13 mode-script contracts and dashboard initialization checks passed. |
| HA configuration | Pass | Sanitized live `ha core check` passed. |
| ESPHome production-intent YAML | Pass with warnings | 27 intended files validated with ESPHome 2026.5.3. |
| ESPHome `_dev` YAML | Expected unresolved | Development templates exited 2 and are not deployable artifacts. |
| Compose parsing | Pass | 15 baseline Compose files and 27 services parsed. A post-baseline Mermaid package adds one Compose file/service and is re-inventoried at close. |
| Git whitespace check | Pass | `git diff --check` found no whitespace errors in the overlay. |

## ESPHome hardware warnings

- GPIO4 and GPIO5 are strapping pins in the base, array, pipe, and garage
  sensor configurations.
- GPIO9 is warned on the booth, FDM, and SLA airflow configurations.
- The booth-fan configuration does not pin the ESP32 framework.
- These are build-valid configurations, not electrically certified designs.
  Bench validation, boot-state observation, and fail-safe verification are
  required before physical acceptance.

## Compose and container-source findings

The corrected baseline static inventory found 27 services across 15 active
Compose files: 13 use floating or logical tags, nine use version tags, three
are local builds, and only two are digest-pinned. Twenty-one have no health
check, four mount the Docker socket (Dozzle, Homepage, Telegraf, and
Watchtower), and none declare a resource limit. Live comparison found source
drift in Immich, ntfy, and Watchtower; Bambuddy and Household Hub lack
equivalent canonical Compose templates.

The post-baseline Mermaid Viewer overlay adds a build-only Nginx service. Its
baseline browser test failed because `app.js` referenced a missing local
Mermaid module. The overlay now supplies a local dependency, build script,
Docker packaging, and `dist/`; it is intentionally recorded as an overlay and
has not been proven deployed.

Concurrent housekeeping later added a second docker-host deployment template
and service-matrix entry. Closing Compose inventory therefore contains 29
service definitions across 17 files: 13 floating/logical tags, 10 version tags,
four local builds, and two digest pins; 23 lack health checks and all 29 lack
resource limits. The two Mermaid definitions are alternative build/deployment
representations, not evidence of two live services.

## Documentation and link checks

- The tracked/relevant inventory initially classified 532 artifacts: 470
  validated, 57 were present binary/generated assets, and five documentation
files failed link validation.
- Broken-link counts were: prior audit TODO ledger 2, `wiki/CLAUDE.md` 4,
  `wiki/log.md` 5, `wiki/pages/concepts/rag-vs-wiki-pattern.md` 1, and
  `wiki/pages/sources/llm-wiki-idea-file.md` 7.
- Thirty-eight executable code fences under `main/docs/install` lack the
  required `Run on:` label; 26 are in the OLED guide.
- Active documentation still contains stale VirtualBox paths and old
  `iot_sensors` identifiers.
- The placeholder scan identified 164 explicit placeholder lines. Many are
  deliberate templates, but the Bambuddy P1S serial placeholder is a real
  deployment blocker.
- The generated TODO ledger contains 412 mechanically classified checklist
  rows. Mechanical state is not accepted as proof of live completion.
- Closing inventory contains 576 tracked/relevant artifacts: 501 pass, 70 are
  present binary/format-specific assets, and five retain the inherited link
  failures listed above. The audit's own links pass.

## Secret scanning

The redacted scanner covered current tracked text and the complete Git
history. Vendor bundles create many false positives, so only manually
corroborated results are findings. The material result is that
`.obsidian/plugins/obsidian-local-rest-api/data.json` is tracked, contains a
non-empty API credential plus private-key material, and appears in four
historical commits. Values are excluded from this pack.

The closing scan also inspected non-generated ignored runtime files. It found
expected credential material in ESPHome/VentSys runtime files and the router
deployment key. The router key ACL is restricted to its owner, SYSTEM, and
Administrators. The ESPHome secrets file, VentSys runtime config, and an old
ignored dashboard copy inherit ACLs that permit ordinary local users to read
and authenticated users to modify them. No values were opened or recorded.

## Tool limitations

- Node.js was not on the normal baseline PATH. A post-baseline Mermaid
  `node_modules` tree exists in ignored content, but the dependency runtime was
  not treated as a clean baseline prerequisite.
- Browser testing covered current desktop and a 390x844 mobile viewport, but
  not every supported browser/OS combination.
- Static validation cannot prove switch persistence, camera electrical
  safety, tailnet control-plane policy, restore correctness, or outage
  behaviour.
