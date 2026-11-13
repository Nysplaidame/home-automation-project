# OMV host-local health collector preparation

## Status — October 2, 2026

The source at [[../../configs/omv/system/omv-health-snapshot.py]] and six isolated
tests are prepared. A one-off read-only run through the existing `omv-lan`
management key produced valid `omv-health/1.0` JSON. No executable, service,
timer, Telegraf/Alloy configuration, credential, firewall rule or Grafana panel
was installed or changed. The existing SMART Kuma heartbeat remains independent.

At21:30 BST the snapshot observed five disks, SMART passed for all, temperature
30–42 C, and no reported pending/uncorrectable/reallocated sectors. One disk had
lifetime CRC count1; another returned smartctl bitmask32 (historical attribute
threshold flag). Both are warnings, not proof of a new failing SMART health
result or counter increase. Match `identityHash` across observations rather
than relying on `/dev/sdX` names. md0 had zero degraded members, active array
state and idle sync action; the earlier morning consistency check is historical.
Both expected data UUID mounts and root capacity were observed. SMB, NFS,
smartmontools and mdmonitor were active; daemon state is not client-workflow proof.

Bitmask handling follows the upstream [smartctl manual](https://raw.githubusercontent.com/smartmontools/smartmontools/master/smartmontools/smartctl.8.in):
lower command/open/data error bits yield unknown; failed overall health yields
failed; attribute/history/error-log/self-test-log bits remain visible warnings.
Standby is unknown, not a fabricated successful observation.

## Collection contract

- Linux Python standard library only, JSON on stdout. No network client, token
  file, raw logs, environment dump, write operation or retained runtime state.
- Host: load averages and MemTotal/MemAvailable bytes. These are observations,
  not a CPU-percent history or a complete host dashboard.
- Disks: bounded lsblk physical-disk inventory, then
  `smartctl -d ata -n standby,2,2 -j -i -H -A` for known SATA transport. Explicit
  ATA type avoids autodetection wake-ups; an unsupported power check also exits
  unknown. Unreviewed USB/SAS/NVMe/eMMC transport is listed but not queried.
  No self-test, repair, power-state command or
  disk-waking fallback. Standby and unsupported devices remain unknown.
- SMART: overall result, temperature, smartctl bitmask/diagnostic flags and
  selected reallocated/pending/uncorrectable/CRC counters. Missing counters are
  null. WWN, or serial if WWN is absent, is hashed; raw identities are omitted.
  Hashes are stable pseudonyms, not credential protection or anonymization proof.
- RAID: read-only sysfs array state, degraded-member count and existing sync
  action/progress. A consistency check is distinct from degraded-array recovery.
- Filesystems: root plus the two canonical data UUID mountpoints. `findmnt`
  must match the exact target and expected UUID before `statvfs` capacity is
  reported; a missing NAS mount cannot silently report root-disk free space.
- Services: `systemctl is-active` for smbd, nfs-server, smartmontools and
  mdmonitor only. Unknown unit/output/command failures stay unknown.

Commands have20-second timeouts; stdout over512 KB is rejected, disks capped at32 and
arrays at8. Supported device names are SATA/SCSI sd*, NVMe namespaces and eMMC.
This is a bounded host contract, not general transport/SMART support. SMART requires
device access; the current one-off management session is root. No general SSH
access is proposed for Grafana. Tests run without disks, services or a network:

```powershell
python -m unittest discover -s main/configs/omv/system/tests -v
```

For another one-off read-only observation from the canonical checkout:

```powershell
$omvSource = Get-Content -Raw main/configs/omv/system/omv-health-snapshot.py
$omvSource | ssh -o BatchMode=yes -o ConnectTimeout=8 omv-lan 'python3 -'
```

If saving stdout, choose a new protected location outside the vault. It contains
internal mount/device evidence; do not publish raw SMART JSON or identity values.
The collector does not itself save, overwrite or rotate any file. Output must
not be labelled current after its observation timestamp ages.

## October 4 atomic producer preparation

The [[../../configs/omv/system/omv-health-publish.py|publisher]] and
[[../../configs/omv/system/omv-health-snapshot.service|service]]/
[[../../configs/omv/system/omv-health-snapshot.timer|timer]] templates are now
prepared locally. All11 Linux collector/publisher tests pass. Unit syntax was
verified under WSL with a temporary existing-group stand-in; this does not
validate OMV capabilities, device access or actual systemd execution. No files,
group, schedule, source executable or monitoring state were installed on OMV.

The root producer imports only the fixed immutable root-owned collector path
`/usr/local/libexec/home-automation/omv-health-snapshot.py`. Source ancestry must
be real root-owned directories without group/world write access. The output
directory `/var/lib/home-automation/omv-health` is likewise checked. The proposed
`omv-metrics` group must already exist before execution; its creation/membership
is part of deployment review. It gets read-only access to a0640 snapshot inside
a0750 state directory, not a password, root SSH credential or collector source.

The publisher validates schema, top-level fields, JSON finite numbers,512 KB
size and an offset-aware observation time no older than five minutes or more
than30 seconds in the future. It takes a nonblocking host-local lock, writes a
private temporary file, flushes data before making it group-readable, replaces
`snapshot.json` atomically and flushes the directory. A symlink or hardlink target
is refused. It retains one snapshot, no history. Failures before replacement
leave the previous bytes/timestamp unchanged; a directory-flush failure after
replacement can leave the complete new file but still fails the service. No
failure refreshes an old observation to a new successful timestamp.

Consumers must read **only `snapshot.json`**, preserve null/unknown values and
check `observedAt`; they must not glob temporary files or use mtime as evidence.
The proposed timer starts two minutes after boot and five minutes after the
previous run exits, with15-second scheduling accuracy and no persistent catch-up.
A proposed consumer age ceiling is ten minutes; alert on service failure
independently of age. Both cadence and age are review defaults, not accepted
live settings. A unit run times out at15 minutes, but the publisher rejects a
stale result rather than publishing it as fresh.

The unit has no network address families beyond local Unix sockets, a read-only
system filesystem, private temporary storage and a closed device policy with
five explicit current SATA nodes. Device names must be reconciled at deployment;
no wildcard access or new-device fallback is provided. Some SMART interfaces
require rw opens, so these device rules are not a hardware read-only guarantee:
immutable source and fixed read-only commands are essential boundaries. The
proposed capability set still needs live validation. If it denies SMART access,
unknown data must be detected rather than hidden or silently widening privileges.

Deployment review must explicitly provision the dedicated group, install both
root-owned scripts, ensure the state-directory parent ownership/modes satisfy
the checks, reconcile device nodes, run a **manual unit acceptance** and verify
non-root consumer reads plus denied writes/source edits. Only then accept the
timer, stale/failure behavior and rollback. Rollback disables the new timer,
waits for any active producer to exit and removes consumer access; it does not
stop NAS services or the existing SMART heartbeat. Shipping credentials, TLS,
schema/retention and Grafana remain separate unimplemented work.

## Local metrics conversion preparation — October 4, 2026

[[../../configs/omv/system/omv-health-metrics.py]] converts the published JSON
file to Prometheus text on stdout. It neither collects new observations nor
opens a listener, writes files, invokes commands or sends metrics. Default input
is `/var/lib/home-automation/omv-health/snapshot.json`; an optional single file
argument supports isolated fixtures. Seven adapter tests plus the existing
collector/publisher tests pass:18 total on Linux.

The adapter reads at most512 KB from a regular file, refuses a final symlink on
Linux and rejects duplicate JSON keys. Malformed structure, duplicate resource
identities or untrusted label values suppress all resource samples. Unknown
extra fields, raw device paths, serials, WWNs and notes are never exported.
At deployment, run this consumer without root and retain the producer's trusted
directory ancestry and file permissions; final-component checks alone do not
secure arbitrary input directories.

Always monitor `omv_snapshot_available`, `omv_snapshot_valid` and
`omv_snapshot_fresh`. A valid timestamp must include an offset. Fresh means age
from zero through600 seconds inclusive; future and older observations export
only snapshot signals and age. Missing/unreadable/oversized files report
available0; readable malformed files report available1, valid0. Exit0 permits
ingestion of these failure signals and is **not a health success indicator**.
The historical October2 fixture is stale on October4; its resource values must
not be presented as current.

All families are gauges. Disk/RAID/service status codes are0 unknown,1 healthy,
2 warning,3 failed. Inventory and filesystem observation are separate0/1
signals. Null, boolean and nonfinite numeric values are omitted; unknown disk,
RAID or mount state suppresses its numeric readings. Unknown inventory also
suppresses cached disk/RAID rows. Missing disk identities are counted explicitly
and have no per-disk series. Disk labels use32-character identity hashes;
array/service/dataset and attribute labels use bounded allowlists.

Host load/memory, observed filesystem bytes, degraded RAID members and SMART
temperature/attribute counts are exported only from fresh evidence. SMART
attribute counts remain lifetime observations; no new-fault delta, reset-safe
rate or backup/restore certification is inferred. Empty inventories are not
healthy. Removal and staleness alerts must use snapshot/inventory signals;
downstream retained last values must not remain green when readings disappear.

The format groups each family with one TYPE declaration before unique samples
and terminates output with a newline, following the official
[Prometheus text exposition contract](https://prometheus.io/docs/instrumenting/exposition_formats/).
Tests check this structure, stale/future boundaries, withheld unknown readings,
identity collisions/injection, bounded/BOM/duplicate-key files and CLI failure
signals without payload disclosure. The separate parser rehearsal below verifies
consumer format compatibility; deployed Telegraf configuration, shipping
credentials and dashboard changes remain open.

October4 verification also converted the saved October2 live snapshot through
the actual CLI: available1, valid1, fresh0 and age only, with no resource samples.
The repository audit covered938 files (119 Python,69 JSON,105 YAML,340 Markdown)
with no syntax or current Markdown-link failures. Existing advisory findings
remain:4 historical links,11 unresolved wiki links,20 missing tracked paths and
10 duplicate groups; zero generated candidates. These are not silently deleted
or reclassified as new adapter faults.

## Telegraf parser rehearsal — October 4, 2026

[[../../configs/omv/system/omv-health-telegraf-input.conf]] is a prepared input
fragment for a **dedicated OMV-local unprivileged consumer**, not the monitoring
VM's agent. It runs only the immutable metrics adapter against the fixed atomic
snapshot path, with a proposed60-second input interval and five-second timeout.
No outputs, credentials or listener are included. Do not merge this fragment
into the monitoring VM's live configuration: the command/file paths belong to
OMV and no remote collection access is provided.

The fragment explicitly selects Prometheus parser version2 and measurement
`omv_health`, with fixed `source=omvnas` and `schema=omv-health/1.0` tags. Resource
labels become tags; Prometheus metric names become fields. These mappings follow
the official [parser contract](https://docs.influxdata.com/telegraf/v1/data_formats/input/prometheus/)
and [exec input documentation](https://docs.influxdata.com/telegraf/v1/input-plugins/exec/).
This is a proposed new measurement contract, not an existing bucket/datasource
claim. Host tagging, destination bucket, permissions and retention still need
explicit acceptance with the eventual dedicated consumer.

The repeatable rehearsal is
[[../../configs/omv/system/tests/verify_telegraf_metrics.py]]. Run on Linux with
`python3 -B tests/verify_telegraf_metrics.py --telegraf /path/to/telegraf` from
the OMV `system/` source directory. The optional explicit
`--ssh monitoring-lan` instead uses the existing monitoring container's binary
in a separate `docker exec -i telegraf telegraf --test --config /dev/stdin`
process. All configuration travels on stdin and contains only the selected
input, synthetic renderer output and test-only hostname suppression. No live
configuration is read/replaced, no remote temporary files are created, and no
output destination is configured. Use **--test**, never --once: the official
[command contract](https://docs.influxdata.com/telegraf/v1/commands/) confirms
that test mode gathers inputs without running outputs.

The actual monitoring binary reports Telegraf1.38.3 (`HEAD@b8487989`). Five
rehearsals passed, comparing every field/value/tag combination with the adapter
output and rejecting extra/missing/duplicate samples:

| Synthetic input | Parsed samples | Result |
|---|---:|---|
| Fresh, including warning/unknown disk and missing mount readings |25| Exact match |
| Stale observation |4| Snapshot signals/age only |
| Future observation |4| Snapshot signals/age only |
| Malformed schema |3| Availability/validity/freshness only |
| Missing file representation |3| Availability/validity/freshness only |

No raw serial marker, unknown disk temperature or missing filesystem capacity
appeared in parsed samples. Parser timestamps are ingestion timestamps; snapshot
age/freshness remain essential even if downstream points look recent. The test
does not install Telegraf on OMV, execute the real consumer command there, verify
its permissions/cadence, send data to InfluxDB or accept dashboard behavior.
The ordinary18 Linux tests also remain passing.

## Current-state queries and independent failure preparation — October 4

[[../../configs/omv/grafana/README|Prepared query bindings]] defines three Flux
sources kept outside Grafana's provisioned dashboard directory. The snapshot
query selects the newest evidence before interpreting its flags. The resource
query joins readings only to that collection's exact ingestion timestamp and
ages the observation forward to query time. Missing fields, newer invalid/stale
evidence or omitted readings cannot select an older healthy generation. A
two-minute delivery window also turns missing shipping into no current data.
Do not fill missing values with0 or use last-good fallbacks in Grafana.

Nineteen synthetic cases (32 query executions) pass in the existing Flux engine
using [[../../configs/omv/system/tests/verify_omv_flux.py]]. Bucket access is
replaced by literal arrays; no bucket is read or written and no account/token
is created. Existing authentication stays within the monitoring container's
environment. The test uses a fixed synthetic clock, not a claim that production
clocks are synchronized. It verifies age expiry between polls, the exact600-second
ceiling, missing/partial flags, retained readings, unknown disk state, silence,
wrong source and independent unit states. The join uses
[Flux pivot](https://docs.influxdata.com/flux/v0/stdlib/universe/pivot/) and
[inner join](https://docs.influxdata.com/flux/v0/stdlib/universe/join/) semantics;
fixture sources use [array.from](https://docs.influxdata.com/flux/v0/stdlib/array/from/).

[[../../configs/omv/system/omv-health-systemd-input.conf]] prepares exact service
and timer patterns for the OMV-local consumer via the official
[systemd_units input](https://docs.influxdata.com/telegraf/v1/input-plugins/systemd_units/).
It avoids whole-host/wildcard collection and detailed process metrics. Both
input fragments parse as TOML. The monitoring binary exposes this plugin, but
actual OMV D-Bus permissions and metrics remain unaccepted. No D-Bus socket
mount, service account, installation or privileges were added.

The independent query preserves systemd integer field types and selects newest
states per unit despite changing active/load tags. A failed producer alerts
independently of a still-fresh prior snapshot. An inactive one-shot is **idle,
result unverified**, not failed and not healthy. A timer's active state proves
only scheduling. Missing/denied unit data, absent shipping and query errors must
raise unknown/no-data attention; do not map them to an operational service.

The Telegraf parser rehearsal additionally verifies one common ingestion
timestamp for all samples in a collection. Shipping acceptance must preserve
that invariant and use exactly one source/schema consumer; split timestamps,
duplicate writers and replay/backfill are not accepted by this current-state
query contract. No dashboard rendering or real end-to-end delivery is claimed.

## Manual acceptance and rollback checklist

Perform installation only in the separately accepted maintenance/deployment
scope. These are acceptance requirements, not commands executed by preparation:

1. Reconcile devices, source hashes, group/account ownership, protected paths,
   unit restrictions and clock synchronization. Install immutable producer,
   publisher and adapter source; accept a manual producer unit before scheduling.
2. As the dedicated non-root consumer, read only the atomic snapshot and run
   the adapter. Demonstrate denied snapshot writes, source edits and raw-device
   access. Test D-Bus **read-only** service/timer observations without permission
   to start/stop/change units. Treat any unavailable readings as unknown.
3. Accept a dedicated output config with a scoped write-only destination token,
   verified TLS, source-scoped egress and bounded retention. Keep the separate
   dashboard reader scoped to its accepted bucket. Check tags, field types,
   shared ingestion timestamp and absence of duplicate consumers at destination.
4. Using isolated fixtures/test delivery, verify stale/future/malformed/missing
   snapshots, producer failure with retained fresh data, stopped timer, omitted
   temperature/mount readings and complete shipping silence. Check alert routing
   and unknown/no-data rendering; do not deliberately fail the live NAS producer
   or disable existing SMART/Kuma polling for these tests.
5. Accept the timer and consumer together, compare fresh observations with OMV,
   then accept the reviewed dashboard queries/panels and rollback path. Observe
   at least two complete producer cycles and a consumer restart without replay.

Rollback stops/disables only the new snapshot timer and dedicated consumer,
waits for an in-flight publisher to finish, restores the prior NAS dashboard,
revokes the new scoped output token and removes the dedicated group's read
access after checking membership. Preserve root-only source/evidence for review;
do not delete arbitrary state paths or remove a shared account/group. Leave
SMB, NFS, existing backups and SMART/Kuma monitoring running. Restart acceptance
from manual production/delivery checks before enabling the new path again.

## Remaining deployment and dashboard work

Review a host-local narrowly privileged producer with root-owned immutable
source and a private atomic snapshot handoff to a dedicated unprivileged
Telegraf/Alloy consumer. Choose cadence, maximum observation age, null/standby
handling, device-access bounds, output permissions, retention and performance
budget before scheduling. Do not make Grafana poll OMV through general root SSH.

Metrics shipping still needs a least-privilege write-only destination credential,
reviewed TLS and source-scoped egress, measurement/tag schema, retention and
failure monitoring. Preserve unknown values rather than emitting fake zeros or
cached success. Validate counters by stable identity and keep lifetime CRC/past
threshold warnings separate from new changes. Logs and backup freshness are
separate contracts; this snapshot contains neither. No new metric bucket,
account, port or firewall rule is authorized by preparation.

Only replace the NAS dashboard shell after accepted scheduled collection,
authenticated delivery, stale/absent-data rendering and rollback. First deploy
to a reviewed local destination, verify service/device least privilege, compare
collected observations with OMV, then accept the shipping/dashboard change.
Rollback should stop the new producer/consumer and restore the prior dashboard
without disturbing SMART/Kuma polling or any NAS service. Full application,
SMB/NFS client and backup/restore acceptance remain independent.
