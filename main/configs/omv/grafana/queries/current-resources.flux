// Select the latest collection BEFORE applying freshness. Never fall back.
data = from(bucket: "${omv_bucket}")
  |> range(start: -2m)
  |> filter(fn: (r) => r._measurement == "omv_health" and r.source == "omvnas" and r.schema == "omv-health/1.0")

latest = data
  |> filter(fn: (r) => r._field == "omv_snapshot_available" or r._field == "omv_snapshot_valid" or r._field == "omv_snapshot_fresh" or r._field == "omv_snapshot_age_seconds")
  |> group(columns: [])
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
  |> sort(columns: ["_time"], desc: true)
  |> limit(n: 1)
  |> map(fn: (r) => ({_time: r._time, gateOk:
    if not exists r.omv_snapshot_available or not exists r.omv_snapshot_valid or not exists r.omv_snapshot_fresh or not exists r.omv_snapshot_age_seconds then 0.0
    else if r.omv_snapshot_available == 1.0 and r.omv_snapshot_valid == 1.0 and r.omv_snapshot_fresh == 1.0 and r.omv_snapshot_age_seconds >= 0.0 and r.omv_snapshot_age_seconds + float(v: int(v: now()) - int(v: r._time)) / 1000000000.0 <= 600.0 then 1.0
    else 0.0}))

resources = data
  |> filter(fn: (r) => r._field == "omv_disk_status" or r._field == "omv_disk_temperature_celsius" or r._field == "omv_disk_attribute_count" or r._field == "omv_raid_status" or r._field == "omv_raid_degraded_members" or r._field == "omv_filesystem_observed" or r._field == "omv_filesystem_bytes" or r._field == "omv_service_status" or r._field == "omv_host_load" or r._field == "omv_host_memory_bytes" or r._field == "omv_storage_observed" or r._field == "omv_raid_observed" or r._field == "omv_disk_identity_missing")
  |> group(columns: [])

join(tables: {resources: resources, gate: latest}, on: ["_time"], method: "inner")
  |> filter(fn: (r) => r.gateOk == 1.0)
  |> drop(columns: ["gateOk"])
  |> yield(name: "current_resources")
