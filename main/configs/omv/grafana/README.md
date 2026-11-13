# Prepared OMV dashboard queries

These Flux sources are review artifacts outside Grafana's provisioned dashboard
directory. No dashboard or datasource is installed. They use the proposed
`omv_health`/`omv_health_unit` measurements from the dedicated OMV-local consumer;
they do not describe an existing bucket or replace the current NAS shell.

Supply a reviewed constant Grafana variable `omv_bucket` and an accepted InfluxDB
Flux datasource before binding panels. Do not use an admin token for shipping
or dashboard reads. Allow only the chosen bucket name; no interpolated user
query text, wildcards, regex sources or multi-value bucket selections.

| Query | Binding | Interpretation |
|---|---|---|
| [[queries/snapshot-state.flux]] | Snapshot evidence stat |0 unknown/incomplete;1 fresh evidence;2 not current (old/future);3 invalid;4 file unavailable |
| [[queries/current-resources.flux]] | Current resource table, or field-filtered stats | Latest collection only; observation age at query time must stay within600 seconds |
| [[queries/producer-state.flux]] | Independent producer/timer status table |0 unknown;1 timer active;2 timer not active;3 unit failed;4 producer collecting;5 producer idle (result not certified) |

For snapshot state, label1 **Fresh evidence**, not **NAS healthy**. Use grey for
unknown/no data, green only for specifically observed healthy status/fresh
evidence, amber for warnings/not current and red for observed failures. Producer
idle is grey: a successful one-shot normally becomes inactive and inactivity
alone does not prove success. Timer active likewise does not prove collection.

`current-resources.flux` joins resource points to the most recent snapshot flags
by exact ingestion time **after** selecting the newest flags. It also adds
elapsed ingestion time to observation age. It cannot select an older healthy
generation after a newer stale/invalid/partial generation. Unknown disk state
can appear as0, but its previous temperature and missing filesystem capacity
do not carry forward. Do not add `fill(0)`, a long lookback, independent `last()`
per field, last-good fallbacks or cached success transformations.

All three queries use a fixed two-minute delivery window independent of the
dashboard time picker. No rows means **No current delivery / unknown**, never
zero healthy. Alert on no data, datasource/query failure and producer failure
separately. A producer failure must alert even if a retained snapshot still meets
its age limit. For unit3, investigate; for timer2, investigate the stopped
schedule. Missing/denied D-Bus observations or units are unknown and require
attention. Snapshot0/2/3/4 and silence require attention without inferring a
storage failure. Disk/RAID/service codes remain0 unknown,1 healthy,2 warning,
3 failed; missing numeric values remain absent.

The delivery contract requires exactly one consumer for this source/schema,
one common ingestion timestamp per collection, stable fixed source tags and
accepted clock synchronization. The parser rehearsal verifies the timestamp
invariant; real shipping must verify it again and detect duplicate writers.
If ingestion splits timestamps or processes replay/backfill, these queries must
not be accepted as current-state views. A few seconds of observed desktop/VM
clock difference during testing was handled with a fixed synthetic test clock;
that does not certify production clocks.

[[../system/tests/verify_omv_flux.py]] runs the exact source transformations in
the existing Flux engine with synthetic arrays replacing bucket access. It
uses the existing monitoring container credential only inside that container,
does not print it and reads/writes no buckets. Run from the canonical root:

```powershell
& C:/Users/Admin/miniconda3/python.exe -B main/configs/omv/system/tests/verify_omv_flux.py --ssh monitoring-lan
```

The19 cases cover current readings, newer stale/invalid/absent/partial evidence,
unknown disk, resources without flags, silence/wrong source,
observation-age expiry and exact ceiling, missing age, idle/failed/running
producer, missing unit, stopped timer and unit silence (32 query executions).
This verifies query semantics and compatibility, not real OMV D-Bus access,
authenticated delivery, Grafana rendering/alerts or full NAS workflow health.
Canonical acceptance/rollback:
[[../../../docs/procedures/omv-health-collector-preparation]].
