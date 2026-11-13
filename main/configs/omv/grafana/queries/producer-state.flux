// Independent producer/timer state, never inferred from a retained snapshot.
data = from(bucket: "${omv_bucket}")
  |> range(start: -2m)
  |> filter(fn: (r) => r._measurement == "omv_health_unit" and r.source == "omvnas")

data
  |> filter(fn: (r) => r.name == "omv-health-snapshot.service" or r.name == "omv-health-snapshot.timer")
  |> filter(fn: (r) => r._field == "active_code" or r._field == "load_code")
  |> group(columns: ["name"])
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
  |> map(fn: (r) => ({_time: r._time, name: r.name, _value:
    if not exists r.load_code or not exists r.active_code then 0.0
    else if r.load_code != 0 then 0.0
    else if r.active_code == 3 then 3.0
    else if r.name == "omv-health-snapshot.timer" then (if r.active_code == 0 then 1.0 else 2.0)
    else if r.active_code == 4 then 4.0
    else if r.active_code == 2 then 5.0
    else 0.0}))
  |> yield(name: "producer_state")
