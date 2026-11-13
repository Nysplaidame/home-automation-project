# VentSys authenticated dashboard — 2026-10-18

**Latest: frontend `20261019-5` / backend `20261019-command-repair-1`.** Owner
physical testing exposed failures missed by earlier UI/mock checks. Running
firmware logs proved intake command topics were crossed; corrected in dashboard
and all modes. E2 HA host corrected `.51`→`.52`, native entity/coverage recovered.
Modes support explicitly reviewed available-controller subsets; matching targets
can be resent without claiming movement. Software/HA validation passed; physical
retest is still outstanding. Earlier acceptance below is software/UI evidence only.


October 19 correction release `20261019-1` is deployed and verified through
the signed-in HA frontend. Registry MACs prove that current FDM uses
the legacy SLA native entity ID and current SLA uses the legacy FDM ID.
The release corrects read/confirmation mappings, keeps correct MQTT topics,
recognizes the accepted 30–60 firmware endpoints and reports incomplete setup
as setup/status notes. It does not change firmware. See the current runbook
below for the private checkpoint and acceptance and recovery.

Release `20261019-1` is deployed and accepted in the real HA frontend at
`/dashboard-ventsys/0`. It is a direct authenticated custom card, with no iframe
bridge or public token. The dedicated old dashboard token was revoked and
independently rejected with HTTP 401. Old local HTML/wrapper URLs redirect to HA.

The card now uses native controller reports, reviewed requests with bounded
confirmation, explicit missing/stale states, corrected sensor units and a
scrolling phone layout. Software range is 0–100; both live 360 boards still
advertise firmware limits of 30–60. No physical actuation or calibration was
performed. VentSys remains under testing.

Current runbook, source/test commands, acceptance and recovery:
[[../docs/procedures/ventsys-dashboard]]. Historical findings and remaining
hardware/control work: [[../docs/audits/2026-10-18-ventsys-dashboard]].

The former draft card/page message bridge is superseded for this dashboard.
It must not be restored as the authenticated control path.

Backend revision `20261019-arbitration-1` now routes dashboard/manual mode/helper
commands through a shared normal dispatcher and gives the fire-response script
preemption. Eight arbitration tests and an isolated HA no-MQTT probe passed;
production loaded idle, no physical commands sent. See the runbook for paired
backend artifacts/rollback and direct-MQTT/native-control limits.

Frontend `20261019-2` is now live: dispatcher-aware control availability,
immediate unverified interruption on failsafe/fire/backend takeover, and explicit
alarm/failsafe/fire headings. Four new browser regressions; 24 browser tests pass.
Signed-in live release verified connected/ready without commands; backend remains
`20261019-arbitration-1`. Recovery details are in the runbook.

Frontend `20261019-3` is live: schematic Environment table with Ambient/FDM/SLA
columns, plus System log title and actual session events. 26 browser tests and
contract/drift checks passed; desktop/mobile screenshots reviewed, signed-in HA
labels/version/no-command state verified. Backend remains unchanged.

Frontend `20261019-4` is live. Standard layout/configuration retained; separate
`/dashboard-ventsys/touch` provides touch menus and original-style PrintAirPipe
header/clock plus bottom status strip. Two overlong main-duct highlights trimmed;
System log entries enlarged. 30 browser tests passed including 800×480/1024×600.
Signed-in HA popup/view/config/hash acceptance passed without commands. Physical
screen acceptance remains separate; see the runbook for URLs and rollback.

Frontend `20261019-6` adds saturated red/green valve endpoint colours (including
30/60 intake endpoints) and aligned y800 frame bottoms for log/enclosures/booth.
34 browser tests passed; backend command repair remains unchanged. Visual-only
release; physical response verification remains separate.

October20 frontend `20261019-7`: Environment glow and equal enclosure tops
live verified; six touch tests passed. Mode redesign pending semantic clarification,
see service manual. No backend/actuator commands in this cosmetic deployment.


October20 current frontend `20261020-3`: grouped independent modes, strength
popup with shared maximum, one value confirmation, no physical-position field,
larger labels, bidirectional mode-report mismatch warnings. Backend operating
package/dispatcher guards deployed; 38 Python,39 browser,24 model tests plus
live config/template/UI checks passed. No actuation. E2 still unavailable with
host discrepancy; ntfy deployment/delivery and hardware commissioning remain open.
See service manual for semantics, generation order, evidence and recovery.

Prepared October27 source20261027-1 adds explicit valve-only Setup/test option.
Not live: browser webview attachment blocks authenticated script/resource reload.
39 Python,42 browser,24 model checks passed; fixture preview saved outside vault.
Prepared release and rollback copies are in the HA private checkpoint documented
in the service manual. Current active resource/packages remain20261020-3.


Current live release20261027-1: Setup/test activated through signed-in HA after
panel access recovered. Configuration/scripts/resource/hashes and actual valve
review/cancel verified. No actuator commands sent. Normal mode guards unchanged;
Setup tests available valves only and never fans or operating intent helpers.
