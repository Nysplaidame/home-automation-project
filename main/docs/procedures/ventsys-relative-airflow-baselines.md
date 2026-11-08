# VentSys relative airflow baseline plan

Status: planned commissioning tests, after installation and valve travel acceptance.
No anemometer is assumed. Readings are relative sensor signals, not calibrated
volume flow or proof of sufficient extraction.

## Core matrix

Test each of the nine configurations below at **physical fan steps 1, 2, 3,
4, 5, 6, 7, 8, 9 and 10**: 90 configuration/speed baselines. Do not assume
speed step is proportional to airflow, or that HA 10% corresponds to step 1.
Record the actual controller step and any verified HA command mapping.

O = physically verified open endpoint; C = physically verified closed endpoint.
These are endpoint states, not literal servo-number percentages. Existing mode
scripts use generic 0/50 targets and do not establish physical endpoints; use
the accepted per-board calibration. Set every valve explicitly for each test,
since subsystem scripts leave other branches and main valves unchanged.

| ID | Configuration | FDM branch | FDM print | FDM 360 | SLA branch | SLA print | SLA 360 | Fan steps |
|---|---|---|---|---|---|---|---|---|
| F-P | FDM print only | O | O | C | C | C | C | 1–10 |
| F-E | FDM enclosure only | O | C | O | C | C | C | 1–10 |
| F-U | FDM purge only | O | O | O | C | C | C | 1–10 |
| S-P | SLA print only | C | C | C | O | O | C | 1–10 |
| S-E | SLA enclosure only | C | C | C | O | C | O | 1–10 |
| S-U | SLA purge only | C | C | C | O | O | O | 1–10 |
| B-P | Both print paths | O | O | C | O | O | C | 1–10 |
| B-E | Both enclosure paths | O | C | O | O | C | O | 1–10 |
| B-U | Both purge paths | O | O | O | O | O | O | 1–10 |

For each row, open every main/trunk valve required between its active branches
and the outlet. Close/isolate the unused booth path; keep the booth fan off.
Record **MAIN-1 and MAIN-2 physical states** in the baseline key. Confirm their
routing against the final installed duct layout before testing: the existing
scripts open MAIN-1 for SLA, and both main valves for booth/all-purge, but do
not define a complete trunk-state matrix for all combinations. Do not infer it
from the mode name or leave it inherited from a previous test.

## Additional configurations when used

- M-PE: FDM print + SLA enclosure (FDM O/O/C; SLA O/C/O), steps 1–10.
- M-EP: FDM enclosure + SLA print (FDM O/C/O; SLA O/O/C), steps 1–10.
- Booth only: both enclosure branches closed, required booth/trunk route open;
  steps 1–10, with booth fan held at one recorded fixed setting.
- Booth + both print; booth + both enclosure; booth + both purge: reuse B-P,
  B-E and B-U, open the booth route, steps 1–10, same fixed booth-fan setting.

Each additional row adds ten baselines. If the booth fan setting changes, it is
another independent matrix dimension; do not merge the results. Partial valve
positions are separate configurations and can be added after endpoint tests.

## Fan-off reference and measurement method

Capture a fan-off reference for each tested valve configuration, including
booth fan off. This records sensor offset/background drafts; it is not assumed
to be exactly zero. Do not run the fan against an all-closed duct as a baseline.

1. Use the final ductwork, normal enclosure lids/doors, clean installed filters,
   fixed room/window conditions and no printing/spray activity. Record these
   conditions and sensor/firmware identity so later comparisons are meaningful.
2. Confirm the physical valve states, set the physical fan step, wait initially
   60 seconds, and extend settling until the readings are reasonably stable.
3. Record all installed branch airflow signals simultaneously for 120 seconds.
   Store median, spread (for example 10th/90th percentiles), valid sample count,
   faults and any available pressure readings. Preserve raw sensor units.
4. Repeat each point three times, including a descending-speed pass to reveal
   repeatability differences. Ninety core baselines means 270 measurement
   windows; split the work into sessions while keeping conditions consistent.
5. Keep inactive-branch readings too: they establish the normal background or
   leakage pattern. A missing/faulted reading invalidates that sensor's result.

Use the same sensor/configuration/speed baseline for future comparisons. For a
stable nonzero airflow signal, a relative index can be calculated as
100 × (current signal − fan-off reference) / (baseline median − fan-off reference).
This is a **sensor-signal index**, not percentage volume flow. Near-zero
denominators or noisy low-speed readings are unsuitable for that index; retain
raw ranges and mark those points below useful measurement resolution. Establish
alert thresholds from repeated measurements rather than choosing an arbitrary
percentage now. Never sum unlike branch signals as if they were calibrated flow.

## Acceptance still required

- Verify final MAIN-1/MAIN-2 routing and physical endpoints before executing.
- Verify the ten physical fan steps and controller mapping.
- Complete the core matrix and relevant mixed/booth rows.
- Repeat after duct/valve/filter/sensor changes; maintain a clean-filter reference
  separately from aged-filter observations.

This baseline plan does not certify fire response, extraction adequacy or safety
commissioning. Canonical controls: [[ventsys-board-power-controls]].
