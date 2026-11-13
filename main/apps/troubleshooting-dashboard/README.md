# Troubleshooting Dashboard

## Live Resource Health and connection tests — October11

### Certificate checks, bundles and timeline extension

The console now also supports `tls TARGET` for Homepage (`docker`), Home
Assistant, Frigate and Vaultwarden (`vault`). Public certificate inspection
uses the endpoint's fixed address, port and SNI hostname, then verifies chain,
hostname and validity with system roots plus the Home Local CA. A certificate
due within30days is a warning. Root-owned public trust copy:
`/etc/troubleshooting-api/ca.crt` (directory0755, file0644), copied from
`/opt/stacks/homepage/tls/ca.crt`; refresh this copy during CA rotation.
No private certificate key is copied or made readable to the service account.
Missing/unreadable trust store yields **unknown**, never a trusted result.

Live October11 checks found the Home Local CA lacks the key-usage extension
required by Python3.13 strict validation (verification code92). The page retains
that strict failure and separately verifies a legacy compatibility profile.
Only code92 triggers that additional profile; chain trust, hostname and dates
remain mandatory. A successful compatibility check yields **warning**, never a
strict pass. Wrong hostname, expiry and unknown CA remain failures. Four live
HTTPS targets passed compatibility verification with this warning. Plan a CA
replacement/distribution exercise in the certificate maintenance procedure;
rotating trust across clients and services is separate operational work.
TLS uses up to three bounded handshakes; other probes retain their previous
timeouts, concurrency and rate limits.

Nine named diagnostic bundles cover all37 investigations. The current route
suggests a relevant bundle; review its3–4 listed commands, then Run bundle.
Checks run sequentially, retain individual outcomes and continue after a
diagnostic failure. Transport/service/rate-limit failure stops the sequence.
Stop after current check cancels pending work. Bundles test supporting network
paths, not credentials, recording, backup validity or device operation.
Imported route assessments remain independent.

The **Incident timeline** retains summaries of monitor-state transitions,
successful ntfy acceptance, viewer stale/unavailable/recovery observations and
operator-requested diagnostics. This is shared operational evidence visible to
the existing Homepage audience. It does not retain user notes/imports or the
full console transcript. Summaries are capped800 characters and are retained for
up to30days /1,000 events. The API returns the newest100 with filters and copy
support in the UI. Historical incidents before deployment are not reconstructed.
Repeated observations are deduplicated; older publications cannot invent a
recovery. Every event links to Infrastructure Fleet and Central Logs with a
fixed±10minute time range; dashboard coverage may be incomplete for that host.

SQLite state: `/var/lib/troubleshooting-api/events.sqlite3` plus normal WAL/SHM
companions, owned by `troubleshooting-api` under its0700 state directory.
`event_history.py` lives beside `diagnostic_api.py` and as root-owned0644
`/usr/local/sbin/event_history.py` for the forced receiver. The API service's
strict filesystem sandbox permits writes only to its runtime and state paths.
The receiver records publication transitions after atomically accepting metrics;
history failure cannot reject the metrics file. The API records diagnostic
summaries and has a minute observer for viewer freshness. History failure is
explicit in the UI, and successful probes still return their result if storing
a summary fails. The primary monitor and ntfy delivery remain independent.

Deployment additions: install the shared history module to both paths, update
the API unit and receiver, install the updated Proxmox reader (it exports only
accepted-notification timestamps), provision the public CA copy, then restart
the API and rebuild the selected app container. Schema creation is automatic;
runtime database files stay outside the vault. Tests use temporary databases
and disposable certificate keys and never write the production history.

Validation:28 backend tests (API boundaries, history retention/deduplication,
real local TLS for trusted/near-expiry/expired/wrong-name/unknown-CA/legacy cases)
passed. `npm run test:extensions` exercises live TLS and bundle results, route
suggestions, cancellation, continued checks after failure, history links/filter,
history-unavailable handling and desktop/mobile layout. Existing guided and
Homepage integration checks remain required.

Selected extension rollback: VM103
`/opt/backups/troubleshooting-tls-history-20261011/` contains prior app, API unit
and receiver; image `troubleshooting-dashboard:rollback-tls-history-20261011`.
The prior Proxmox reader is
`/etc/troubleshooting-publish/reader-before-tls-history-20261011.py`.
Restore these selected files, reload/restart the API and recreate its container;
the earlier Resource Health and connection console continue working. Preserve
the event database for recovery; do not delete historical evidence to roll back
the UI. No primary-monitor or guest changes are part of this release.

Homepage's **Monitoring > Resource Health** card opens
`https://homepage.home.local/portal-preview/troubleshooting/#resource-health`.
The existing troubleshooting entry opens the same application. No new VM, CT,
DNS record or network listener is required. Resource Health lists host and guest
usable memory, guest CPU, root-disk use, memory/IO pressure, cumulative OOM
counters, stopped guests, thin-pool use, incidents, coverage and delivery state.
The monitor snapshot is refreshed every minute and is stale after five minutes.
Unavailable/stale evidence cannot establish current health. Grafana and ntfy
links are navigation; this extension does not add an InfluxDB history writer.

The console accepts `ping TARGET`, `dns TARGET`, `tcp TARGET PORT` and
`http TARGET` and `tls TARGET`. Buttons offer the same checks. Nine targets and their ports are
defined in `diagnostic_api.py`; HTTP URLs are fixed, bodies are omitted and
redirects are blocked. No arbitrary addresses, shell operators or user-selected
URLs are accepted. Checks run **from VM103**, not from the user's device. This
may legitimately produce different firewall/DNS results from a manual check on
the stated execution host. Windows TCP checks in guided routes have a separate
**Test TCP from VM103** button; results do not change imported route assessments.
Copy results exports the last20 checks; Copy incident report includes current
monitor summary and the connection transcript. Notes and full transcripts remain tab-local; bounded check summaries are retained in the shared timeline.

### Runtime and trust boundary

- Existing Nginx container: IPv4 management8094 and Homepage's fixed HTTPS
  reverse proxy. CSP permits only same-origin connections. Existing audience
  and IPv6 publication restrictions remain in force.
- VM103 `troubleshooting-api.service`: unprivileged `troubleshooting-api` user,
  Python standard library,128MiB memory cap,32 tasks; only a Unix socket at
  `/run/troubleshooting-api/api.sock`, mounted read-only into Nginx. Runtime
  directory survives service restarts so the Docker bind remains valid.
- POST checks require an approved exact Origin, JSON and the custom
  `X-Diagnostic-Request` header. No CORS is enabled. Two simultaneous jobs and
  twenty checks/minute globally; non-TLS checks have4–7second timeouts and
 6000-character maximum output. The allowed Homepage audience can run these
  non-mutating probes; there is no new login or administrative console.
- VM103 cannot SSH into Proxmox under current VLAN policy. That restriction
  remains unchanged. Proxmox's independent `troubleshooting-publish.timer`
  publishes metrics every60seconds through existing management→VM103 SSH.
  It runs `monitor_reader.py`, then `monitor_publish.py`; failures never affect
  `resource-pressure-monitor.timer` or its ntfy alerts.
- Dedicated Proxmox key: `/etc/troubleshooting-publish/key`,0600; verified
  host key: `/etc/troubleshooting-publish/known_hosts`. VM103 authorized key is
  source-restricted to192.168.10.10 with `restrict` and forced
  `/usr/bin/python3 /usr/local/sbin/troubleshooting-monitor-receive.py`.
  Its locked service account has no general SSH key or password login.
- Receiver validates a≤200KB JSON snapshot and atomically replaces only
  `/var/lib/troubleshooting-api/resources.json`,0600, and records bounded history. It cannot execute the SSH
  caller's requested command. No ntfy token, monitor config or private key is
  sent to the browser. API credentials are unnecessary.

### Operations, validation and rollback

On VM103: `systemctl status troubleshooting-api.service` and
`runuser -u troubleshooting-api -- python3 /opt/stacks/troubleshooting-dashboard/diagnostic_api.py --status`.
The latter is read-only: no probes, schema creation, pruning or writes. It reports
snapshot/publication age, CA readability and event-database availability/count.
The existing watchdog also checks this supported status. On Proxmox:
`systemctl status troubleshooting-publish.timer troubleshooting-publish.service`.
Inspect journals for errors. Publication failures appear as stale UI evidence;
the existing hourly Codex watchdog now also checks publication timer/service,
API health, snapshot timestamp and publication-file age. It reports viewer
failures separately from primary collection failures and suppresses unchanged
reports. The primary monitor and alerts still operate without the desktop.

Restore/install sequence (run from the host-specific source directory; transfer
public keys only through the existing authenticated administration connection):

1. VM103: create the locked system account with home
   `/var/lib/troubleshooting-api`, shell `/bin/sh`, and0700 home/`.ssh`.
   Install `diagnostic_api.py` and `event_history.py` into `/opt/stacks/troubleshooting-dashboard/`;
   install `monitor_receive.py` as
   `/usr/local/sbin/troubleshooting-monitor-receive.py` root-owned0755 and
   `troubleshooting-api.service` into `/etc/systemd/system/`0644. Also install the shared history module as root-owned0644 `/usr/local/sbin/event_history.py` and the public CA copy described above.
2. Proxmox: create0700 `/etc/troubleshooting-publish/`; generate
   `ssh-keygen -t ed25519 -N '' -C troubleshooting-resource-publisher -f
   /etc/troubleshooting-publish/key` if absent. Provision its public key on
   VM103 in the service account's0600 authorized_keys using the exact forced
   command and source restriction above. Do not overwrite unrelated keys.
3. Copy VM103's **previously verified** SSH host key into
   `/etc/troubleshooting-publish/known_hosts`,0600. Install `monitor_reader.py`
   and `monitor_publish.py` as root-owned0755
   `/usr/local/sbin/troubleshooting-monitor-reader.py` and
   `/usr/local/sbin/troubleshooting-monitor-publish.py`. Install publisher units
   into `/etc/systemd/system/`0644. Run `systemctl daemon-reload`,
   `systemctl start troubleshooting-publish.service`, then
   `systemctl enable --now troubleshooting-publish.timer`.
4. VM103: `systemctl daemon-reload` and
   `systemctl enable --now troubleshooting-api.service`; verify
   `curl --fail --unix-socket /run/troubleshooting-api/api.sock
   http://localhost/api/resources`. Rebuild the existing app with
   `docker compose build --pull=false` and
   `docker compose up -d --no-deps troubleshooting-dashboard`.
5. Apply the selected Homepage card and `connect-src 'self'` change to its
   troubleshooting location. Render its template with
   `envsubst '${DOCKER_HOST_TAILSCALE_IP}'`, run `nginx -t`, then `nginx -s reload`
   inside `homepage-preview-proxy`. Keep other live proxy changes intact.
   API service restarts should leave the existing container's socket working.

Tests: `npm run check`; on Linux `npm run test:api`; set `POC_URL` to the live
HTTPS or management URL and run `npm run test:live` plus `npm run test:browser`.
October11:20 model tests,10 API tests, existing guided desktop/mobile smoke and
new HTTPS live tools smoke passed. Success, invalid command, origin/header
denial, rate limit, timeout, stale/unavailable evidence and keyboard/mobile
behavior are covered. Live ping/TCP/HTTP passed; diagnostics use the host's
unprivileged ping datagram support, without adding NET_RAW capability.

Selected rollback: VM103 `/opt/backups/troubleshooting-live-tools-20261011/`
contains the previous app source, Homepage proxy and services YAML; previous
image is `troubleshooting-dashboard:rollback-live-tools-20261011`. Stop/disable
the new API and Proxmox publisher units; restore the selected app files and
recreate its container with the prior Compose/image. Remove the Resource Health
card and revert only this CSP change in the live Homepage template, then run
Nginx validation/reload. Avoid replacing a later Homepage configuration wholesale.
The original monitor, alert timer, guest allocations and camera state are
independent and require no rollback.

Read-only, dependency-free dashboard for turning a visible symptom into an
ordered diagnostic sequence. The catalog now has **37 routes** in five areas:

- Network and access: portal, Internet/Wi-Fi, DNS, trusted HTTPS and remote access.
- Hosts and storage: Proxmox guests, shared Docker resources, NAS and two backup layers.
- Home and devices: HA, automations, cameras, P1S, local AI/voice, VentSys and phone relay.
- Monitoring and maintenance: missing graphs, notifications and package updates.
- Applications and data: Immich, media libraries, downloads/VPN, sync, household APIs and vault.

Use search or the area selector; category groups keep the list manageable.
Search matches all words across route titles, check labels and guidance, so
terms such as `SMB permission`, `Clear Bed`, `crypto.randomUUID` and
`address already in use` lead to the relevant investigation. Selecting a
route updates `#route=<id>`; Copy route link shares only that investigation,
without notes, imported evidence or query parameters. In-page help links do
not change the selected route. Incident reports include the stable route ID.
The [original written walkthroughs](../../docs/troubleshooting/diagnostic-walkthroughs.md)
and [32 extended routes](../../docs/troubleshooting/extended-app-routes.md) remain
available in the local vault if the dashboard's own Docker host is down.
Extended offline routes are generated from `additional-routes.js` with
`node main/apps/troubleshooting-dashboard/scripts/export-routes.mjs` from the
repository root. Update that source and regenerate rather than editing both.

The catalog describes potential failures, not a fresh audit of every service.
Shared host/listener passes never stand in for application or data acceptance.
The existing collectors cover only some signals; route-specific missing evidence
requires the manual checks and operator notes. Checking Collected never changes
an imported status. The October11 extension adds separate live resource evidence and bounded connection checks; these never alter imported route statuses.

## Data boundary

The guide imports files locally. The separate live tools use a same-origin backend for named, allowlisted checks. Load the JSON produced
on the Proxmox host:

```sh
main/scripts/monitoring/health_check.sh --json > health.json
```

Or from a Windows management workstation:

```powershell
main\scripts\monitoring\health_check.ps1 -Full -Json > health.json
```

The file is parsed in the browser and is not uploaded. Unknown or skipped
checks stay `Needs evidence`; they are never treated as healthy.

The Windows collector includes the observed endpoint or HTTP result beside each
status. The Proxmox collector supplies the guest-mount and per-guest backup
freshness checks that cannot be established from the management workstation.
For a backup incident, use the Proxmox JSON snapshot rather than treating the
missing Windows signals as a failure or a pass.

### Evidence age and recorded device state

The deployed 2026-09-10 update requires an explicit timezone and a snapshot no
older than 36 hours before using checks to assess a symptom. The review window
is a conservative common UI default, not a service uptime guarantee or proof
of backup integrity. Missing, ambiguous, invalid, future or stale timestamps
show `Needs evidence`; the original pass/fail observations remain visible and
are included in incident reports. Age is rechecked every minute while open.

The updated Windows source emits an ISO timestamp with its UTC offset; the
Proxmox source emits UTC with `Z`. Older installed collectors still omit the
timezone. Recollect using the updated collector, or establish the actual
collection timezone before preparing a compatible import; never infer it
from the browser timezone. Updating these source files does not deploy them.

Only the built-in example selector enables example mode. The UI and copied
report identify examples as non-live evidence; an imported JSON `example`
field cannot bypass age checks. Loading or clearing a snapshot resets the
collected-step checkboxes while retaining operator notes.

Camera investigations retain their dated disconnected baseline. P1S guidance
now records its commissioned state and implicit FTPS port 990. This does not convert a failed check to
a pass, and does not suppress Frigate, storage, Bambuddy or MQTT failures.
Confirm current device state before using that recorded context.

This update is deployed to management port8094 and passed live desktop/mobile
checks with a fresh Windows snapshot (12 pass, one disconnected camera fail).
The Windows collector runs from the canonical checkout; no matching Windows
scheduled collector was found. The September10 Proxmox SSH gap was closed on
September14; a dedicated snapshot collector is installed and September15 real
evidence import passed. Homepage placement was approved on 2026-09-11.

Deployment rollback files are in
`/opt/backups/troubleshooting-evidence-20260910/` on VM103, with the old image
retained as `troubleshooting-dashboard:rollback-20260910`. The stack still
publishes only `192.168.20.102:8094`, and its bridge has IPv6 disabled. A
pre-existing IPv6 DOCKER-USER Tailscale RETURN rule for8094 needs reconciliation
before any IPv6 publication; this update did not change firewall rules.

### Proxmox snapshot acceptance

The remaining acceptance gate requires a fresh read-only export from the
existing Proxmox host collector. On the Proxmox host, use its installed
`/usr/local/sbin/home-automation-health-check --json` command and copy the
result to the management workstation. Do not run a backup, restore, restart,
or configuration change for this evidence collection.

Validate the copied file before importing it into the staged dashboard:

```powershell
python main\scripts\monitoring\validate_proxmox_snapshot.py .\proxmox-health.json --require-pass
```

Acceptance also requires a snapshot no older than 36 hours and a valid timezone.
For a legacy local timestamp, add `--timestamp-offset +01:00` only if that was
the Proxmox collector's actual offset when collected. Missing, stale, ambiguous
or future-dated evidence cannot pass. Integrity and restore proof remain separate.

The validator accepts only a `Proxmox host` snapshot with the CT 111/114
capacity evidence, the CT 111 recording-mount source, and fresh archives for
VMs 100/102/103 and CTs 111/114. It reports statuses only and never prints
collector detail. A non-passing result is evidence to investigate; it is not a
reason to change the dashboard's `Needs evidence` state.

The interface highlights the first failed or missing evidence signal and names
the host on which each displayed command must be run. These are instructions
only: copying a command never runs it.

## Local verification

```powershell
cd main/apps/troubleshooting-dashboard
npm run check
docker compose config
```

Serve the directory with any static server for browser review. The staged
container binds only `192.168.20.102:8094`, uses reserved explicit bridge
`10.240.32.0/24`, and requires the tracked management-only `DOCKER-USER`
policy for direct access. The owner-approved Homepage HTTPS path now also
serves existing Homepage clients; no separate DNS alias was added.

October2 read-only inspection reconfirms the IPv4-only8094 bind and IPv6-disabled
bridge. The pre-existing IPv6 Tailscale RETURN is still live; a tested local
source change now stages explicit8094 denial. Failed Windows/monitoring probes
are not complete firewall-denial proof. Do not reload the whole host ruleset;
follow the [[../../docs/procedures/troubleshooting-dashboard-ipv6-publication-guard|bounded reconciliation and rollback procedure]].

## Deliberate v1 exclusions

- no arbitrary shell input or shell execution;
- no automatic restart, firewall, restore or remediation controls;
- no credentials, tokens or embedded authenticated monitoring APIs;
- no persistence of user notes/imports/connection transcripts beyond the current browser tab;
- no claim that a missing signal is healthy.

## Staged live state

- [x] Five diagnostic sequences reviewed with explicit execution hosts.
- [x] Staged deployment on management-only port `8094`.
- [x] Desktop/mobile acceptance using a real 13/13 Windows snapshot.
- [x] Stop/start rollback proof and post-rollback access revalidation.
- [x] Real Proxmox snapshot acceptance for mount and backup-freshness evidence
  (September15 live browser import; archive restore remains separate).
- [x] Owner-approved Homepage placement (2026-09-11); no new DNS alias.

The pre-change live firewall and audit scripts are retained on VM 103 under
`/opt/backups/troubleshooting-dashboard-20260825T1518Z/`.

## Readability update (2026-09-10)

The interface uses a numbered choose/add/check/review journey, 18px body text,
16px supporting evidence and wrapped commands. Evidence follows the checks
instead of squeezing them into a three-column layout. Each check expands to
show its execution host, command, expected result and interpretation; the
first is open initially. Search and area groups keep problem choices manageable on phones.

The upload area includes the Windows snapshot command, explains that failed
checks can still be imported, and names the separate Proxmox collection gate.
Files stay in the browser; gathering evidence remains an operator-run step.


## Extended route deployment (2026-09-11)

### Recurring-incident expansion (2026-09-30)

Ten focused routes extend the catalog from 27 to 37: standalone Homepage
navigation, escaping proxy redirects, competing Serve/Nginx ports, DNS after
reboot, Windows SMB identity/permissions, NAS transfer/extraction pauses,
Bambuddy queue gates/uploads, stale frontend/browser API failures, ESPHome
identity mismatch and Docker build-network failure. The generated offline
companion now contains 32 extended routes plus the original five walkthroughs.

Sources reviewed include the current mobile Homepage incident and these
available Codex conversations: **Fix persistent network drive access**,
**Fix slow 7zip NAS extraction**, **Troubleshoot Orca printer connection** and
**Fix workout save UUID error**. Canonical access/service manuals and current
live state supply the deployed contracts. These are diagnostic ideas grounded
in past observations, not claims that all faults are present now. The NAS-speed
conversation proposed causes without measuring a definitive root cause; its
new route keeps those causes as hypotheses. The September weak printer signal
is likewise a historical observation requiring fresh confirmation.

P1S guidance no longer treats the commissioned printer as planned/offline and
uses implicit FTPS `990`, not legacy plain FTP `21`. Responses request browser
cache revalidation (`Cache-Control: no-cache`) so the diagnostic guide itself
does not silently retain an old route catalog. No collectors, service controls,
credentials, network permissions or browser-data persistence were added.

Rollback: the prior stack sources and image ID are at
`/opt/backups/troubleshooting-routes-20260930/` on VM103; the prior image is
tagged `troubleshooting-dashboard:rollback-20260930`. Restore its source files
or tag that image as the existing Compose image and recreate only this stack.
Keep the direct Management-only publication and existing Homepage HTTPS route.

Deployment verification passed: 20 model tests, all 37 local browser route
selections, ten new live mobile routes at 390x844 without horizontal overflow,
live desktop review at 1440x1000, multiword/exact-error search, deep links,
help-anchor route retention, note retention and route-link copying. A healthy
example still leaves manual-only evidence unknown. Browser console showed no
errors. Compose/Nginx validation and certificate-verified Homepage HTTPS
returned 200 with the intended CSP and cache policy. Existing direct 8094
binding was retained; rollback image was saved, not exercised in this pass.

All 27 routes are deployed on the existing management-only port8094. Verification
passed 17 model tests, local/live desktop-mobile checks selecting every route,
search/category/no-match behavior, and live asset parity. The app remains
import-only; these guided routes do not add network probes or prove that the
manual-only signals passed. Rollback sources and image ID are retained under
`/opt/backups/troubleshooting-routes-20260911/`, with image tag
`troubleshooting-dashboard:routes-rollback-20260911`.


## Expanded Windows evidence (2026-09-11)

`health_check.ps1 -Full -Json` now produces21 checks (the default remains12).
Additional evidence covers the router's exact local DNS A answer and public DNS
resolution, trusted Homepage/vault HTTPS, Proxmox8006, workstation-to-cache3142,
Immich's API listener and Open WebUI's health endpoint. A known DNS timeout or
server error fails; unsupported/tool errors stay unknown. No SSH access, auth,
message sending, uploads or service changes are performed by these probes.

HTTP probes read headers without following redirects. Existing core checks
remain reachability-only and say so; the two explicit trust checks use normal
certificate validation. HTTP401 proves a responding listener, never a successful
login. Workstation cache reachability does not prove the affected guest's path.
Application jobs, model readiness, data integrity and restores remain manual.
The photos and AI routes reuse the collector's specific listener signals while
retaining the deeper missing-evidence gates. Proxmox collector installation is
historically unchanged at that point; September14 dedicated collector deployment
and September15 evidence acceptance close that SSH/evidence gap.

Run offline collector contract tests with
`pwsh -NoProfile -File main/scripts/monitoring/tests/test_health_check.ps1`.
They load function definitions only and mock transport/DNS; they do not probe
real endpoints. Keep live JSON outside the repository and omit private data
when sharing incident evidence.


## Homepage troubleshooting preview (2026-09-11)

Owner approved and deployed Tools > Troubleshooting > Troubleshooting Dashboard,
using the existing card style, Preview and Open tab controls. The fixed URL is
`https://homepage.home.local/portal-preview/troubleshooting/`; Nginx proxies only
to `http://192.168.20.102:8094/`. No new DNS alias, listener or firewall rule.
The existing Homepage audience can now access the dashboard through HTTPS;
the direct 8094 management boundary is unchanged. The proxy retains the app's
CSP restrictions, including `connect-src 'self'`, with explicit Homepage frame
ancestors. Direct access still disallows framing. Evidence stays browser-local.

Live Nginx validation and desktop/mobile preview checks passed: all 27 routes
loaded, Open tab points to the fixed URL, and the 390px viewport has no horizontal
overflow in either Homepage or its frame. Browser checks used an explicit local
hostname mapping and ignored TLS errors. A separate curl check returned HTTP200
with certificate validation and revocation checking disabled; this does not
resolve the workstation's existing DNS/revocation issues. Subsequent local-name
verification and September15 Proxmox evidence acceptance are recorded below.


## Proxmox evidence captured (2026-09-14)

Dedicated workstation SSH now works. The real September14 snapshot passed all
eight required mount/capacity/backup-age checks and dashboard model validation.
September15 live browser smoke imported fresh real Proxmox JSON successfully
and passed desktop/mobile checks; the earlier file-picker blocker is closed.
Run `/usr/local/sbin/home-automation-dashboard-snapshot --json` on Proxmox for
fresh evidence; its existing scheduled monitor is unchanged. Fresh archives
do not establish integrity or restore acceptance. See the current handoff.
