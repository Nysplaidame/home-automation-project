# VentSys Tapo P110 Smart Plugs — HA Integration Config
# Devices: .71 (FDM), .72 (SLA), .77 (AMS-HT), .78 (eSUN dryer)
# Hardware: Tapo P110 — ESP32 internally BUT TP-Link locked firmware
#
# APPROACH: HA tplink integration (local polling, no cloud required)
# The P110 supports: on/off control, real-time wattage, voltage, current,
# daily/monthly kWh — this covers your electricity monitoring requirement.
#
# NO ESPHOME: Do not attempt to flash ESPHome. P110 v1/v2 both have
# hardware and firmware countermeasures. Local API via tplink integration
# gives equivalent functionality without the risk.
#
# SETUP (one-time per plug):
# 1. Add to HomeIoT WiFi via Tapo app — note the assigned IP
# 2. Go to DHCP reservations (configs/openwrt/dhcp-config.conf) and add
#    static reservations for each plug MAC → canonical IP below
# 3. In HA: Settings → Devices & Services → Add Integration → TP-Link Kasa
#    HA will auto-discover any Tapo devices on reachable VLANs.
#    If not discovered, use manual IP entry.
# 4. Each plug creates entities for switch, power, voltage, current, energy
#
# STATIC IPs (update dhcp-config.conf with MACs after first connection):
#   192.168.50.71 — plug-fdm      (FDM printer)
#   192.168.50.72 — plug-sla      (SLA printer)
#   192.168.50.77 — plug-ams-ht   (AMS humidity/temp unit)
#   192.168.50.78 — plug-esun-dryer (eSUN filament dryer)
#
# HA ENTITY IDs (auto-generated after integration setup):
#   switch.plug_fdm / sensor.plug_fdm_current_consumption etc.
#   Rename to these in HA device settings for consistency with automations.
#
# MQTT BRIDGE (optional — only if automations need MQTT topics):
# HA can forward tplink entity states to MQTT using an automation:
#
#   alias: "Forward FDM plug state to MQTT"
#   trigger:
#     - platform: state
#       entity_id: switch.plug_fdm
#   action:
#     - service: mqtt.publish
#       data:
#         topic: "ventsys/plug/fdm/state"
#         payload: "{{ states('switch.plug_fdm') }}"
#         retain: true
#
# Repeat for each plug if MQTT topic parity with Avatar plugs is needed.
# The ventsys_ha_package.yaml switch entities already reference these plugs —
# confirm entity IDs match after HA adoption and update if needed (F-35).
#
# ENERGY MONITORING IN GRAFANA:
# The tplink integration creates sensor.plug_fdm_current_consumption (W)
# and sensor.plug_fdm_today_energy (kWh). HA's InfluxDB integration
# (monitoring_vm_setup_guide.md Phase 8) will automatically push these
# to InfluxDB → Grafana energy dashboard.
