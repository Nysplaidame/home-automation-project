# October 2 code audit — independent verification

Verified on 2026-10-02 against the audit at
`.claude/worktrees/eloquent-fermi-be507b/main/docs/audits/2026-10-code-audit/README.md`.
The requested path omitted `main/`. The audit worktree HEAD is
`ab81a70cfb96b50a4b0aef38113d49e517169710`; canonical checkout HEAD is
`2596ddd6212130537ec67f5f3445ce4a4a2b7676`. Both have working-tree state, so
HEAD alone is not a source snapshot. This review inspected current file contents.

This is a source verification, not a new live-host security assessment. No live
hosts were contacted, no production configuration was changed, and no exploit
was run. References below are relative to canonical `main/` unless stated otherwise.
The original audit is preserved. **Do not use its severity table as an inventory
of current production defects.** It mixes historical templates, staged features,
existing accepted risks, and code that has already been hardened locally.

## Critical and High finding dispositions

| ID | Verification | Evidence and qualification |
|---|---|---|
| C1 | Confirmed in audit worktree; fixed in canonical source | Old `apps/transferportal/transferportal/root_helper.py` accepts arbitrary intermediate rsync arguments. Current `_validate_rsync_command` allowlists options and requires exact source/destination endpoints of one portal; active mounts are required. Tests cover denied options. |
| C2 | Confirmed in audit worktree; fixed in canonical source | Old helper accepts arbitrary output paths. Current `_validated_output_path` restricts direct children of the compiled log directory and rejects symlinks; runner uses `O_NOFOLLOW` for logs and atomic status replacement. This is not a proof against every filesystem race. |
| C3 | Confirmed in audit worktree; fixed in canonical source | Old helper loads caller-selected config. Current privileged operations use compiled `ROOT_POLICY = AppConfig()` rather than caller policy. |
| C4 | Old trust boundary confirmed; current impact claim stale | Installer still gives the service group write access to app config (`0660`). That no longer changes current helper policy. Application config remains mutable by design; do not equate this with root-policy control. |
| C5 | Source fact confirmed; production-critical classification unsupported | All 13 automations in `configs/home-assistant/automations.yaml` have `initial_state: false`. They start disabled. `docs/reference/current-live-state.md` says most VentSys hardware remains gated; this is a commissioning blocker, not evidence of a newly broken commissioned safety system. Removing the flags alone would enable an incomplete safety chain. |
| C6 | Integration gap confirmed; wording too absolute | Bundle HA sensors subscribe to enclosure-level temperature/smoke/IAQ topics, while the modular air firmware publishes array/pipe prefixes. No active `configs/esphome` pressure-difference publisher was found. This prevents the intended firmware path from supplying those entities. MQTT topics can have other publishers; static source cannot establish that nothing ever populates them. Contract validator does not cover the full sensor chain. |
| C7 | Confirmed conditional deployment hazard | `ventsys/ventsys_bundle_updated/ventsys_combined.json` contains repeating simulated temperature injects connected to actuator/state flows. Its opening comment already warns against production deployment. Current-state docs list Node-RED as decision-gated. No live deployment was established. |
| H1 | Confirmed historical-template compile defect | Bundle `ventsys_valve_controller.yaml` puts a YAML-style `#` comment inside a C++ lambda. This is not a valid ordinary C++ comment/directive. Active per-device firmware lives under `configs/esphome/`. No ESPHome compile was performed. |
| H2 | Confirmed mapping defect in same historical template | `write(c / 100.0f)` sends zero to the servo midpoint rather than the -1 endpoint. Actual valve angle requires calibration; “half open” cannot be inferred from PWM alone. Active branch firmware uses `(x / 100.0) * 2.0 - 1.0`. |
| H3 | Commissioning gap confirmed; unconditional no-op claim unproven | Bundle plug definitions are commented out, but the comments explicitly permit MQTT discovery to create the entities. Actions still call `switch.turn_off`. Static inspection cannot establish actual entity absence or whether a failed action aborts later notification. There is no feedback check proving the notification's “power cut” claim. |
| H4 | Conditional hazard confirmed; inactive by default | Startup automation calls the sealed script after 30 seconds with no failsafe condition; sealed turns fans off and closes paths. However C5 disables this startup automation too. It does not run unconditionally on restart in the supplied configuration. Address the startup safety policy before enabling it. |
| H5 | Default firmware/script mismatch confirmed; “never” overstated | Canonical Nerdiy candidates default to 30 closed/60 open; HA scripts command 0/50. MQTT clamps against configurable endpoint entities, not immutable constants. Default open 50 is intermediate and leaves PWM enabled; closed command clamps to 30 and endpoint shutdown works. Do not claim the servo never powers down. No physical calibration acceptance was established. |
| H6 | Confirmed dormant flow/firmware contract mismatch | Combined and optional arbitration flows use values up to 100, while mode scripts use 50 as calibrated open. Active branch number range still permits 100; the risk is real if those flows are deployed. Overtravel is hardware-dependent, not proven physical damage. |
| H7 | Confirmed in audit worktree; fixed in canonical source | Current `path_safety._posix` normalizes `..` and resolves symlinks on POSIX before mount/prefix checks. Windows uses lexical POSIX normalization; Linux-only symlink coverage is skipped locally. |
| H8 | Confirmed source serialization defect remains | `_mount_unit` interpolates paths into systemd unit fields without escaping newline or `%`; path validation does not reject these characters. Creating a matching directory on an allowed filesystem is a prerequisite. Unit injection is established; arbitrary command execution was not demonstrated. |
| H9 | Fixed in canonical source | `submit_job` and Retry use UUID-specific filenames. Helper status reads also check stored PID ownership. Per-portal stale terminal status no longer describes current source. |
| H10 | Rejected as deployment finding, including original worktree | Raw firewall source contains TEMP rules, but both worktree and canonical `tools/router-deploy/compile.py` call `_strip_temp_firewall_rules` unconditionally. Local check removed 3 rules with no executable TEMP rules remaining. Manually executing raw source is a different path. |
| H11 | Excess source access confirmed; live effect unverified | Raw firewall still allows `.30.20` to NAS SSH/SMB/NFS ports. `configs/omv/nfs-exports.json` retires the direct Frigate client; current recordings use the Proxmox mount/bind path. This is a stale/wider-than-needed rule, not proof of an active NAS export or successful connection. |
| H12 | Confirmed documented residual risk | Four writable exports use `no_root_squash,sec=sys`, with explicit client addresses and writer contracts. Frigate itself uses root squashing. Dedicated writer identity migration is already recorded as open. Do not remove these options without proving backup/restore ownership compatibility. This inventory is dated July 11, not a new live export observation. |
| H13 | Socket trust boundary confirmed; unauthenticated host-root claim not demonstrated | Homepage, Dozzle, Telegraf and Watchtower mount the Docker socket. Filesystem `:ro` does not filter Docker API verbs. Container compromise could exercise permitted socket operations. Merely reaching Homepage is not itself a root exploit; an app/API injection or container compromise is required. |
| H14 | Confirmed source race | `Cancel-RollbackWatchdog` only touches a cancel marker and checks the echoed response. It does not check the rollback result or synchronize with a watchdog that passed the cancel check. Subsequent success can describe a rolled-back deployment. |
| H15 | Reproduced false positive | `test.ps1` runs `ip ... || true` and matches `br-lan\.10`; the missing-device stderr contains the same name. Local regex check against `Device br-lan.10 does not exist` returned True. SSH capture combines stdout/stderr. “Always passes” is too broad: this particular missing-interface diagnostic passes. |

TransferPortal's service manual explicitly says repository hardening is not live
until deployed and revalidated. The fixes above are **source fixes**, not evidence
that OMV's installed helper has them. Verifying the installed helper and its
root-owned import path is the highest-priority operational follow-up.

## Medium findings

| Claim | Verification |
|---|---|
| Retry replays stored command and promotes previews | Stale in canonical source: preview retries refused; only failed/interrupted jobs retry; current portal and options rebuild the command. |
| Move silently copies | Stale in canonical source: `/jobs/move` returns 409 and Retry refuses move mode. |
| SHA-256 password/no throttling | Confirmed optional SHA-256 comparison and no app-level throttling in inspected login route. Password can alternatively come from environment plaintext; the claim that SHA-256 is always the storage format is overstated. No upstream rate-limit proof. |
| Known session secret fallback | Fixed in canonical source: `_session_secret` requires >=32 characters and rejects `dev-only-change-me`; regression tests passed. |
| HTTP/session Secure flag | App uses SessionMiddleware without `https_only`; confirmed source setting. Actual front-door transport was not checked live. |
| No CSRF tokens | Confirmed in inspected forms/routes. SameSite defaults mitigate many cross-site requests; absence of tokens alone is not a demonstrated exploit. |
| Wrong MQTT CA key | Bundle template uses `ca_certificate`; active branch uses `certificate_authority`. Source mismatch confirmed; no installed ESPHome schema validation run. |
| Valve boot/retained state | Active branch has initial position zero, publishes its number state on connect, and no physical feedback validation. It does not literally hard-code zero in that publisher. Blanket all-valve assertion is wrong: main-valve firmware has physical feedback paths. Firmware target/physical shaft disagreement remains a real commissioning risk. |
| Raw rather than clamped retained payload | Confirmed in historical valve template and active branch MQTT callback (`return x`). Actual out-of-range behavior of `number.set` was not tested on ESPHome. |
| Old MQTT platform in tuning package | Syntax present under historical `ventsys_addons_bundle`; no current HA validation/deployment evidence. Treat as a legacy compatibility concern. |
| Llama shared state/system-role external titles | Confirmed entity-wide `_assistant_state`, with no conversation/user key in that state; `_assistant_state_prompt` puts external result titles in injected system context. Cross-user mix and instruction-priority risk are supported by source, not an end-to-end home-control exploit proof. |
| Mealie import SSRF | `ImportRecipeUrlTool` validates with `cv.url` and forwards the URL to Mealie. Local missing destination restrictions confirmed. Fetch is performed by Mealie; its version, SSRF defenses, redirects and reachable networks were not verified. Therefore internal-host SSRF is conditional. |
| Grafana/Kuma Tailscale policies disagree | Both current rules allow docker-host `.20.102`; current access docs describe host/proxy routing. Monitoring container firewall also accepts tailnet source space. Different allowlists alone do not establish a dropped current flow. Reject “one likely drops it” without route/SNAT evidence. |
| WAN to vpn_clients | Broad accept rule present. Reachability depends on routing and packet path; presence is unnecessary breadth, not proof of accessible internal services. |
| Broad monitoring SSH/SNMP | Confirmed zone-wide source/destination rules, without host-scoped IP limits on the cited rules. |
| llm-host IPv6 gap | Script only configures iptables, with no ip6tables counterpart. Actual IPv6 listeners/reachability are unverified. |
| ntfy behind-proxy | `behind-proxy: true` present. Homepage has a real proxy route, so “no proxy” is false for that route. Raw-listener spoofing/exposure requires runtime and ntfy trust behavior checks. |
| Router DNS/public fallback | Forwarding to AdGuard plus public resolvers confirmed; no strict ordering in inspected dnsmasq block. Claim that bypass occurs only when AdGuard is down is too narrow. Router-origin DNS is distinct from inter-zone client internet forwarding. Tunnelling was not tested. |
| first-flight placeholders | Intentional partial stubbing, not sufficient by itself to call a defect. Current compiler separately refuses missing WAN credentials unless explicit offline `--allow-placeholders` is supplied. Recovery tests exercise this requirement. |
| Secret replacement escaping | General `content.replace` still present. Current code rejects quote/CR/LF/NUL in WAN values, but other keys lack equivalent checks; shell-sensitive characters require context-specific handling. Broad unsanitized-replacement finding is partly valid, not equally applicable to every secret. No real secret was printed or used in an exploit. |
| Rollback stops under set -e | Confirmed restart sequence can exit before later restarts/result marker. Failure recovery reliability remains open. |
| health_check JSON omissions/totals | Storage checks are inside `JSON_MODE == 0`; JSON summary uses pass+fail and omits warn, while text total includes warn. Confirmed static inconsistency. No Proxmox execution performed. |
| Week1 validation false failure/security alarm | Confirmed `grep -c ... || echo 0` can output two zeros on no matches; failed `generate_report` terminates under `set -e` before final report; router-origin `ping -I` tests OUTPUT behavior rather than IoT client's forwarding isolation. |
| Screensaver invalid-token retry | `auth_invalid` does not suppress onclose reconnect; reconnect scheduled every 10 seconds. Retry behavior supported; HA IP-ban outcome depends on configured threshold. |
| Valve animation overwrites HA state | Confirmed `animateValveTo` interval writes slider/visual for default 2 seconds; `applyValveState` does not cancel that interval. Visual corruption, not an extra physical MQTT command. |

## Low findings and unsupported global assurances

- **Confirmed source concerns:** PID existence alone can keep a stale/reused PID
  active when no valid status resolves it; TransferPortal login has no explicit
  session clear before setting user; mount setup precedes app portal persistence,
  with no compensating rollback at that boundary. Import-time `app=create_app()`
  can duplicate initialization when another caller explicitly calls the factory;
  “twice at startup” depends on how the app is launched.
- **Mermaid query links:** fixed in canonical `apps/mermaid-viewer/dist/app.js`:
  `init()` reads `?diagram=` and validates it against the diagram list. The audit
  excluded `dist/` although it is the selected release artifact. The remaining
  unescaped-data/root-nginx claims were not independently proved against the
  current build; an `innerHTML` assignment of rendered SVG alone is not an XSS proof.
- **Confirmed Llama malformed tool calls:** `_extract_tool_inputs` invokes
  `tool_call.get` without checking that the item is a dict.
- **Confirmed Mealie list-response bug:** `payload.get(...)` executes before
  testing whether payload is a list. `quote(slug)` preserves `/`; traversal impact
  depends on aiohttp/upstream normalization and authorization and is not proved.
- **Confirmed firmware/script facts:** branch fallback AP uses OTA password;
  `ventsys_mode_fire_safe` turns main fan on without setting its percentage.
  Whether `on` restores sufficient speed depends on firmware/fan state.
- **GardenKeeper:** tracked `env.example` still has Ollama `11434`; actual Compose
  uses host-only `.env`. This is a stale rebuild example, not proof of live runtime
  routing. Bridge self-call failure was not reproduced.
- **Fail2ban:** whole-subnet exemptions confirmed in docker-host and llm-host
  jail templates. **Images:** some templates are unpinned, but current GardenKeeper
  Postgres/Redis are digest-pinned and have healthchecks; the global wording needs
  a counted inventory.
- **Confirmed router tooling:** missing command can reuse LASTEXITCODE=0 (local
  benign reproduction); `system.uci` is generated but not applied by deploy.ps1;
  DNS-name matching can confuse `nas.home.local` with `omv-nas.home.local`;
  Influx exporter passes token in curl header argv (token value was not read).
- **Confirmed preview exposure:** screensaver preview server root resolves to
  `main/`, which includes `tools/router-deploy/keys`; it serves arbitrary readable
  paths there on loopback. It does not serve the entire wrapper. No key was read.
- **Confirmed dashboard concerns:** pending calls lack disconnect rejection,
  socket JSON parse is unguarded, failsafe state schedules repeated wake timeouts,
  nonnumeric/unavailable readings leave numeric display unchanged, and primary and
  fallback temperature/pressure events write the same display without priority.
- **Not independently established:** blanket LAN blockage for all named services,
  current Grafana Frigate query against a retired VM, the broad DNS-UFW claim,
  unauthenticated HA→Frigate API as an unintended policy defect, and every image's
  healthcheck/pinning state. These need exact current artifact/runtime checks;
  do not treat them as verified just because adjacent findings are valid.
- **“Checked OK” limitations:** contract validator passes, but validates mode
  commands and command-free initialization, not full firmware sensor publication,
  physical actuator endpoints, power-cut acceptance, or live safety behavior.
  “No real secrets,” “no XSS,” and “no defects” across entire components cannot be
  certified from this targeted review or from the original stated coverage gaps.

## Validation performed

- Canonical TransferPortal: `python -m pytest tests -q` from its app directory,
  using an existing external dependency directory for `itsdangerous`: **55 passed,
  2 skipped**. Symlink-dependent checks skipped because symlinks are unavailable
  on this test host; no native OMV integration run.
- Router compiler: `python -m unittest test_compile_recovery -q`: **4 passed**.
- `python main/tools/validate_ventsys_contract.py`: **passed** for 13 mode scripts
  and command-free dashboard initialization.
- Benign PowerShell demonstrations: missing-VLAN diagnostic matches check regex;
  missing executable with prior LASTEXITCODE=0 reports ExitCode=0.
- Compiler transformation: **3 TEMP rules removed**, no executable TEMP rules left.

## Recommended follow-up

1. Read-only compare the deployed OMV helper/import ownership with hardened
   canonical source, then plan a bounded deployment and Linux acceptance tests.
2. Fix systemd path serialization and router watchdog/check correctness in source.
3. Before enabling VentSys safety automations, reconcile sensor publication,
   endpoint contracts, verified power cutoff and startup/failsafe policy. Preserve
   commissioning gates until hardware acceptance; do not simply enable everything.
4. Review socket privilege, NAS writer identities, shared LLM state and external
   content injection with explicit deployment context.

This review did not authorize or perform any of those production changes.

## Remediation update — 2026-10-02

The owner subsequently authorized source repairs and stale-document updates.
The verification above describes the pre-repair state; this section supersedes
its follow-up list for the changes listed here. No production deployment was made. The dashboard bridge is still a draft under
`docs/procedures/ventsys-card-page-bridge-contract.md`; the accepted live page
remains offline and command-free. Replacing it requires bridge acceptance.

### Repaired source

- TransferPortal: literal systemd path serialization/specifier escaping and control-character
  rejection; isolated Python root-helper imports (`-I`); installer protects both
  virtualenv directory names. Writes require a same-origin browser header or an
  explicitly configured proxy origin; malformed origins are rejected. Login
  failures are throttled per client and successful login resets session state.
- Router: atomic watchdog/cancellation ownership prevents a reported successful
  cancellation after rollback starts; restart failures are recorded while every
  service restart is attempted. Missing executables fail closed, VLAN tests use
  explicit success markers, DNS matching is exact, and secret/MAC inputs are
  validated before shell/config generation.
- HA integrations: Llama transient state is scoped to each concurrent turn,
  malformed tool calls are rejected, and external recipe context is presented
  as untrusted user data. Mealie accepts list responses, escapes entire slug
  path components, and rejects private/local or mixed-DNS recipe import URLs.
- VentSys: legacy template C++/servo mapping and MQTT CA fields corrected;
  primary temperature/smoke/IAQ topics match array_1 publishers; MQTT tuning
  entities use current domain structure. Legacy Node-RED simulated injects and
  fabricated actuator feedback removed, valve commands bounded to 0–50. Startup
  sealing checks failsafe again after its delay; fire-safe requests full fan
  percentage and notifications describe requested actions, not proved outcomes.
- Dashboard/screensaver: real actuator updates stop animations, disconnects
  reject pending requests, malformed frames are ignored, primary sensor values
  outrank fallback values and unavailable pairs clear numeric displays. Failed
  authentication stops reconnect loops and failsafe wake scheduling is bounded.
- Operational tools: storage checks execute in JSON health mode and collection
  failure is reported; warning totals included. Network validation preserves
  final reports and no longer treats router-origin pings as client isolation
  evidence. Preview serves dashboard files and two explicit vendor assets only,
  excluding router keys. Browser output has narrow ignore rules. GardenKeeper's
  obsolete Ollama example is disabled pending a compatible adapter.

### Verification after repairs

- TransferPortal: **62 passed, 2 skipped** (host lacks symlink support).
- Router compiler: **6 passed**; PowerShell safety tests passed. Actual rendered
  watchdog/cancel/restart scripts passed Linux shell parsing and mocked race/
  restart failure tests in a temporary directory on OMV, without config writes.
- HA integration offline behavioral tests: **4 passed** (malformed tools,
  concurrent state isolation, context role and private/mixed DNS rejection).
- Node behavioral tests passed for animation interruption and auth failure.
- Final Playwright dashboard/screensaver rendering, behavior and preview
  exposure checks: **7 passed**. All Python/PowerShell/Node checks above were
  rerun after final source refinements. Four changed shell scripts passed Linux
  syntax checks; storage threshold and collection-failure accounting passed.
- VentSys validator checks 13 mode scripts, command-free initialization and
  primary sensor publication contracts; explicitly reports unproved hardware
  and secondary/differential sensor acceptance. Storage JSON exercised with
  mocked Proxmox data, including an over-threshold store.

### Live inspection and remaining gates

Read-only OMV inspection found TransferPortal active, no rsync/job-runner process
observed, root-owned application/helper paths, and a nonempty configured session
secret (value not read). Both its installed helper and Python site-package copy
lack canonical ROOT_POLICY hardening; its wrapper lacks `-I`. **The live root
helper risk remains until an accepted deployment.** See the service manual's
matched stopped checkpoint, isolated VM restore/preview/copy and helper-denial
requirements. These were subsequently completed as recorded below.

VentSys's 13 disabled automations remain deliberate commissioning gates. No
physical endpoint calibration, printer power cutoff, differential-pressure
publisher or secondary-array safety aggregation was accepted in this work.
The tracked Nerdiy endpoint defaults (30/60) still differ from the documented
latest bench values (35/0); changing them without physical calibration would
not establish correct movement. Keep the firmware deployment gate open.

Docker socket access, NAS no_root_squash/writer migration, HTTP transport and
legacy password hashing require deployment/architecture decisions. Mealie URL
preflight cannot pin DNS or validate redirects fetched by another process; the
upstream fetcher must enforce those boundaries too. IPv6, broad image-pinning
claims and the audit's unproved service/network claims are not certified here.
Do not describe this remediation as complete live security acceptance.

## Subsequent read-only recheck — 2026-10-02

The requested audit path again omitted `main/`; the actual worktree README now
opens with a historical-snapshot warning linking to this report. A targeted
recheck of current file contents confirmed the old helper's permissive rsync
options, caller-selected policy and output paths, and the corresponding canonical
allowlist, compiled policy, output-path guards and systemd path serialization.
Both worktree and canonical router compilers strip TEMP firewall rules, so H10
remains rejected for the compiler deployment path. The 13 disabled VentSys
automations remain commissioning gates; canonical startup also checks failsafe
after its delay. Current service/current-state docs still record the unhardened
installed TransferPortal helper. That live claim was not freshly probed here.

Checks run in this recheck:

- TransferPortal helper/path-safety tests: **24 passed, 2 skipped**.
- Router compiler recovery tests: **6 passed**; PowerShell deploy safety checks
  passed.
- Offline HA audit-repair tests: **4 passed**; dashboard Node behavior checks
  passed.
- VentSys contract validator passed software checks and explicitly retained
  pressure-difference, secondary-array, physical endpoint and power-cut gates.
- The full TransferPortal suite could not collect because this Python environment
  lacks `itsdangerous`. Earlier full-suite results above were not reproduced in
  this recheck. The two focused skips are symlink-dependent Windows checks.

This was a targeted source recheck, not exhaustive re-certification of every
audit claim. No live hosts were contacted or source/deployed configuration changed.

## Recovery acceptance — 2026-10-02 (checkpoint at22:18 BST)

The owner authorized the checkpoint/isolated restore/copy exercise. Matched
stopped checkpoint `20261002T211810Z` is retained on the mounted OMV data disk:
`/srv/dev-disk-by-uuid-fdb92af7-371c-4793-8d98-ff47e961498d/backups/transferportal-checkpoints/20261002T211810Z/`.
The directory is root-only; archive and manifest are mode600, with original
permissions/ACLs preserved inside the archive. Included app/venv, configuration
and protected credentials, stopped database and sidecars if present, logs,
helper, sudoers, service and portal mount definitions. No transfer data is
included. Archive SHA-256:
`adc422398b6e183b4bf4966b7c552f4dff40560961030edf85c899eb4e49dea7`.
Production had no active DB jobs or rsync/helper runners, was stopped for capture,
and resumed immediately after it. SQLite integrity passed: nine jobs and30
audit records.

Disposable VM9108 was cloned from the stopped no-NIC VM9102 and used guest-agent
commands only. No physical/network NIC, routes or NAS mounts were present during
acceptance; inherited Docker bridges were removed in this disposable guest.
Production mount/service units and environment were preserved as checkpoint
material but never activated. The service was masked; tests started an
unprivileged loopback-only app with fresh test credentials/configuration and
real sudo helper. Every portal used a64MiB tmpfs fixture.

Both saved production and repaired generations restored all nine historical jobs
and30 audit records unchanged, passed real dry-run and copy jobs (IDs10/11 in
separate restored test databases), kept source hashes unchanged and retained a
destination-only file. The two-file fixture includes a1MiB nested binary.
Repaired helper denied `--delete`, `--remove-source-files`, `--rsync-path=sh`
and an `/etc/` source. No historical job was replayed.

The first repaired-generation test exposed a new regression in the earlier
source fix: outer quotes in What=/Where= were treated literally by systemd.
Corrected to literal path values with escaped percent specifiers and rejection
of control characters, backslashes and edge whitespace. A repeated full
restore/copy passed, followed by real bind mounts from paths containing spaces,
percent signs and embedded quotes. This supersedes the earlier quoting test;
62 local tests still pass, with two Windows symlink skips. See systemd's parser
implementation: https://github.com/systemd/systemd/blob/v257/src/core/load-fragment.c.

The initial guest-command quoting error executed a setup tail on the hypervisor;
the isolation assertion stopped it before restore or transfer. Guest commands
now use shell-safe argument quoting and bounded base64 chunks. No production
configuration changed. The accidentally created host script was removed.

Selected evidence: [[2026-10-02-transferportal-recovery-evidence.json]], also
retained as protected `acceptance.json` beside the checkpoint. VM9108 and temporary
transfer media were removed; the pre-existing VM9102 was left untouched. Scripts
are in `tools/transferportal-recovery/`. **The recovery gate is complete; live
hardening is still undeployed.** Refresh idle-state/checkpoint freshness before
a later maintenance update; this proof does not certify real NAS mount options,
production throughput or destructive operations.

## Full local suite reproduction — 2026-10-04

The canonical TransferPortal suite now reproduces **62 passed,2 skipped** using
the existing external `audit-python` dependency directory and the installed
Miniconda Python, with bytecode/cache output disabled. This resolves the earlier
local collection limitation caused by missing `itsdangerous`; it does not change
the earlier recorded run or certify the live installation. The two skips remain
Windows symlink-dependent checks. Test initialization uses a temporary SQLite
database/configuration and test-only session credentials, with cleanup afterward.
No live host was contacted by this suite, no service paths or credentials were
used and no app/helper deployment was made.
