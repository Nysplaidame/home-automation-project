// Prepared query; replace reviewed bucket through Grafana's constant variable.
data = from(bucket: "${omv_bucket}")
  |> range(start: -2m)
  |> filter(fn: (r) => r._measurement == "omv_health" and r.source == "omvnas" and r.schema == "omv-health/1.0")

data
  |> filter(fn: (r) => r._field == "omv_snapshot_available" or r._field == "omv_snapshot_valid" or r._field == "omv_snapshot_fresh" or r._field == "omv_snapshot_age_seconds")
  |> group(columns: [])
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
  |> map(fn: (r) => ({_time: r._time, _value:
    if not exists r.omv_snapshot_available or not exists r.omv_snapshot_valid or not exists r.omv_snapshot_fresh then 0.0
    else if r.omv_snapshot_available != 1.0 then 4.0
    else if r.omv_snapshot_valid != 1.0 then 3.0
    else if r.omv_snapshot_fresh != 1.0 then 2.0
    else if not exists r.omv_snapshot_age_seconds then 0.0
    else if r.omv_snapshot_age_seconds < 0.0 or r.omv_snapshot_age_seconds + float(v: int(v: now()) - int(v: r._time)) / 1000000000.0 > 600.0 then 2.0
    else 1.0}))
  |> yield(name: "snapshot_state")
