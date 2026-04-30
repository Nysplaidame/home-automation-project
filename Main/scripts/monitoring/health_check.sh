#!/bin/bash
# System Health Monitor
# Run from: Proxmox host (192.168.10.10) or management laptop on VLAN 10
# Purpose: Single-command check of all critical system components
# Usage:
#   ./health_check.sh           — full check, human-readable output
#   ./health_check.sh --json    — JSON output for automation
#   ./health_check.sh --watch   — repeat every 60s (Ctrl+C to stop)

set -u

# ── CONFIG ───────────────────────────────────────────────────────────────────
PROXMOX_IP="192.168.10.10"
HA_IP="192.168.20.101"
HA_PORT="8123"
FRIGATE_IP="192.168.30.20"
FRIGATE_PORT="8971"  # N-1 fix: Frigate 0.14+ UI/API moved from port 5000 to 8971
BAMBUDDY_IP="192.168.20.102"
BAMBUDDY_PORT="8000"
P1S_IP="192.168.35.200"   # VLAN 35 (Printers) — see docs/decisions/02-printer-vlan-architecture.md
# C9 fix: P1S check changed from check_port (TCP to 8883) to check_ping.
# The printer's MQTT port 8883 is a TLS-authenticated broker — it does not
# respond to unauthenticated TCP probes in a way that reliably confirms health.
# Ping is a better liveness check here; if the printer is powered on and
# network-connected, ping will succeed. MQTT connectivity is confirmed
# indirectly via Bambuddy (which would show HTTP errors if the broker is down).
NAS_IP="192.168.40.50"
MQTT_IP="192.168.20.101"
# N-3 fix: MQTT_PORT updated to 8883 (TLS). Port 1883 is closed post-TLS migration.
# Mosquitto only listens on 8883 after completing ventsys_tls_implementation_guide.md Phase 4.
MQTT_PORT="8883"

FAN_CTRL_IP="192.168.50.21"   # legacy var — now superseded by VENTSYS_BOARDS loop; kept for reference
VALVE_CTRL_IP="192.168.50.56" # legacy var — was .82 (old pre-canonical); now .56 (ventsys-sla-print-valve)
ESPHOME_PORT="6053"

# ── VENTSYS DEVICE REGISTRY (C8/F-30 fix) ───────────────────────────────────
# All 17 ESP32 boards. Format: "IP:key:Label"  # A5-1 fix: was 16 (same miss as R-1 in dhcp-config.conf)
# key is used as the JSON field name (lowercase, underscores).
# Smart plugs are checked by ping (no ESPHome API port — commercial units).
VENTSYS_BOARDS=(
    "192.168.50.21:main_fan:Main Fan"
    "192.168.50.22:booth_fan:Booth Fan"
    "192.168.50.31:fdm_sensor:FDM Sensor Array"
    "192.168.50.32:sla_sensor:SLA Sensor Array"
    "192.168.50.33:booth_sensor:Booth Sensor Array"
    "192.168.50.34:garage_sensor:Garage Ambient Sensor"
    "192.168.50.41:fdm_airflow:FDM Airflow Sensor"
    "192.168.50.42:sla_airflow:SLA Airflow Sensor"
    "192.168.50.43:booth_airflow:Booth Airflow Sensor"
    "192.168.50.51:main_valve_1:Main Valve 1"
    "192.168.50.52:main_valve_2:Main Valve 2"
    "192.168.50.53:fdm_branch_valve:FDM Branch Valve"
    "192.168.50.54:sla_branch_valve:SLA Branch Valve"
    "192.168.50.55:fdm_print_valve:FDM Printer Valve"
    "192.168.50.56:sla_print_valve:SLA Printer Valve"
    "192.168.50.61:fdm_360_valve:FDM 360 Valve"
    "192.168.50.62:sla_360_valve:SLA 360 Valve"
)
# Smart plugs — checked by ping (not ESPHome port — commercial units)
VENTSYS_PLUGS=(
    "192.168.50.71:plug_fdm_printer:Plug FDM Printer"
    "192.168.50.72:plug_sla_printer:Plug SLA Printer"
    "192.168.50.73:plug_uv_1:Plug UV-1 (ventsys-plug-uv-1)"  # A4-5 fix
    "192.168.50.74:plug_uv_2:Plug UV-2 (ventsys-plug-uv-2)"  # A4-5 fix
    "192.168.50.75:plug_wash_cure:Plug Wash/Cure"
    "192.168.50.76:plug_ultrasonic:Plug Ultrasonic (ventsys-plug-ultrasonic)"
    "192.168.50.77:plug_ams_ht:Plug AMS-HT"
    "192.168.50.78:plug_esun_dryer:Plug eSUN Dryer"
)

ROUTER_IP="192.168.10.1"
INTERNET_TARGET="1.1.1.1"

TIMEOUT=3   # seconds per check

JSON_MODE=0
WATCH_MODE=0

for arg in "$@"; do
    case "$arg" in
        --json)  JSON_MODE=1 ;;
        --watch) WATCH_MODE=1 ;;
    esac
done

# ── HELPERS ──────────────────────────────────────────────────────────────────
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass=0
fail=0
warn=0

check_ping() {
    local label="$1"
    local ip="$2"
    if ping -c 1 -W "$TIMEOUT" "$ip" >/dev/null 2>&1; then
        [ "$JSON_MODE" -eq 0 ] && printf "  ${GREEN}✓${NC} %s (%s)\n" "$label" "$ip"
        pass=$((pass+1))
        echo "pass"
    else
        [ "$JSON_MODE" -eq 0 ] && printf "  ${RED}✗${NC} %s (%s) — unreachable\n" "$label" "$ip"
        fail=$((fail+1))
        echo "fail"
    fi
}

check_port() {
    local label="$1"
    local ip="$2"
    local port="$3"
    if nc -z -w "$TIMEOUT" "$ip" "$port" 2>/dev/null; then
        [ "$JSON_MODE" -eq 0 ] && printf "  ${GREEN}✓${NC} %s (%s:%s)\n" "$label" "$ip" "$port"
        pass=$((pass+1))
        echo "pass"
    else
        [ "$JSON_MODE" -eq 0 ] && printf "  ${RED}✗${NC} %s (%s:%s) — port closed\n" "$label" "$ip" "$port"
        fail=$((fail+1))
        echo "fail"
    fi
}

check_http() {
    local label="$1"
    local url="$2"
    local code
    code=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null || echo "000")
    if [ "$code" = "200" ] || [ "$code" = "302" ] || [ "$code" = "401" ]; then
        [ "$JSON_MODE" -eq 0 ] && printf "  ${GREEN}✓${NC} %s — HTTP %s\n" "$label" "$code"
        pass=$((pass+1))
        echo "pass"
    else
        [ "$JSON_MODE" -eq 0 ] && printf "  ${RED}✗${NC} %s — HTTP %s\n" "$label" "$code"
        fail=$((fail+1))
        echo "fail"
    fi
}

# ── MAIN CHECK ───────────────────────────────────────────────────────────────
run_checks() {
    pass=0; fail=0; warn=0
    local ts
    ts=$(date '+%Y-%m-%d %H:%M:%S')

    if [ "$JSON_MODE" -eq 0 ]; then
        echo ""
        echo "═══════════════════════════════════════════════════"
        echo " System Health Check — $ts"
        echo "═══════════════════════════════════════════════════"
    fi

    # ── NETWORK LAYER ──
    [ "$JSON_MODE" -eq 0 ] && echo ""
    [ "$JSON_MODE" -eq 0 ] && echo "Network:"
    r_router=$(check_ping "Router" "$ROUTER_IP")
    r_internet=$(check_ping "Internet" "$INTERNET_TARGET")

    # ── CORE SERVICES ──
    [ "$JSON_MODE" -eq 0 ] && echo ""
    [ "$JSON_MODE" -eq 0 ] && echo "Core Services:"
    r_ha_ping=$(check_ping "Home Assistant VM" "$HA_IP")
    r_ha_http=$(check_http "Home Assistant UI" "http://${HA_IP}:${HA_PORT}")
    r_frigate_ping=$(check_ping "Frigate VM" "$FRIGATE_IP")
    r_frigate_http=$(check_http "Frigate UI" "http://${FRIGATE_IP}:${FRIGATE_PORT}")
    r_bambuddy=$(check_http "Bambuddy UI" "http://${BAMBUDDY_IP}:${BAMBUDDY_PORT}")
    r_nas=$(check_ping "NAS" "$NAS_IP")
    # C9 fix: was check_port "$P1S_IP" "$P1S_PORT" (TCP connect to 8883).
    # The P1S printer's MQTT port 8883 is the Bambu Lab printer-side MQTT broker
    # which only accepts authenticated connections from Bambu cloud clients —
    # a raw TCP connect returns a TLS handshake, not an open port, causing false
    # failures. Ping is the correct liveness check for a commercial device.
    r_p1s=$(check_ping "P1S Printer" "$P1S_IP")
    r_mqtt=$(check_port "MQTT Broker" "$MQTT_IP" "$MQTT_PORT")

    # ── VENTSYS ESP32 BOARDS ──
    [ "$JSON_MODE" -eq 0 ] && echo ""
    [ "$JSON_MODE" -eq 0 ] && echo "VentSys ESP32 Boards (ESPHome API port ${ESPHOME_PORT}):"
    declare -A ventsys_results
    for entry in "${VENTSYS_BOARDS[@]}"; do
        ip="${entry%%:*}"; rest="${entry#*:}"; key="${rest%%:*}"; label="${rest##*:}"
        ventsys_results["$key"]=$(check_port "$label" "$ip" "$ESPHOME_PORT")
    done

    # ── VENTSYS SMART PLUGS ──
    [ "$JSON_MODE" -eq 0 ] && echo ""
    [ "$JSON_MODE" -eq 0 ] && echo "VentSys Smart Plugs (ping):"
    declare -A plug_results
    for entry in "${VENTSYS_PLUGS[@]}"; do
        ip="${entry%%:*}"; rest="${entry#*:}"; key="${rest%%:*}"; label="${rest##*:}"
        plug_results["$key"]=$(check_ping "$label" "$ip")
    done

    # ── PROXMOX VMs (only if running on Proxmox host) ──
    if command -v qm >/dev/null 2>&1; then
        [ "$JSON_MODE" -eq 0 ] && echo ""
        [ "$JSON_MODE" -eq 0 ] && echo "Proxmox VMs:"
        for vmid in 100 101; do
            status=$(qm status "$vmid" 2>/dev/null | awk '{print $2}' || echo "unknown")
            name=$(qm config "$vmid" 2>/dev/null | grep "^name:" | awk '{print $2}' || echo "vm-$vmid")
            if [ "$status" = "running" ]; then
                [ "$JSON_MODE" -eq 0 ] && printf "  ${GREEN}✓${NC} VM %s (%s) — running\n" "$vmid" "$name"
                pass=$((pass+1))
            else
                [ "$JSON_MODE" -eq 0 ] && printf "  ${RED}✗${NC} VM %s (%s) — %s\n" "$vmid" "$name" "$status"
                fail=$((fail+1))
            fi
        done

        # Proxmox disk usage
        [ "$JSON_MODE" -eq 0 ] && echo ""
        [ "$JSON_MODE" -eq 0 ] && echo "Proxmox Storage:"
        pvesm status 2>/dev/null | awk 'NR>1 {
            used=$4; total=$3
            if (total > 0) {
                pct = int(used/total*100)
                status = (pct > 85) ? "WARN" : "OK"
                printf "  %s  %-20s %d%%\n", (pct>85?"✗":"✓"), $1, pct
            }
        }' || true
    fi

    # ── SUMMARY ──
    [ "$JSON_MODE" -eq 0 ] && echo ""
    [ "$JSON_MODE" -eq 0 ] && echo "───────────────────────────────────────────────────"
    total=$((pass+fail+warn))
    if [ "$JSON_MODE" -eq 0 ]; then
        if [ "$fail" -eq 0 ]; then
            printf " ${GREEN}ALL OK${NC}  %d/%d checks passed\n" "$pass" "$total"
        else
            printf " ${RED}ISSUES${NC}  %d passed, %d failed (of %d)\n" "$pass" "$fail" "$total"
        fi
        echo "═══════════════════════════════════════════════════"
        echo ""
    else
        # JSON output
        # FIX #18: r_bambuddy and r_p1s were computed and shown in human-readable
        # mode but silently absent from JSON output. Both fields added here so
        # automated consumers (dashboards, alerting scripts) see the full picture.
        # Build ventsys_boards JSON object
        ventsys_json="{"
        first_vs=1
        for entry in "${VENTSYS_BOARDS[@]}"; do
            rest="${entry#*:}"; key="${rest%%:*}"
            [ "$first_vs" -eq 0 ] && ventsys_json+=","
            ventsys_json+="\"${key}\":\"${ventsys_results[$key]:-unknown}\""
            first_vs=0
        done
        ventsys_json+="}"

        # Build plugs JSON object
        plugs_json="{"
        first_pl=1
        for entry in "${VENTSYS_PLUGS[@]}"; do
            rest="${entry#*:}"; key="${rest%%:*}"
            [ "$first_pl" -eq 0 ] && plugs_json+=","
            plugs_json+="\"${key}\":\"${plug_results[$key]:-unknown}\""
            first_pl=0
        done
        plugs_json+="}"

        cat <<EOF
{
  "timestamp": "$ts",
  "summary": {"pass": $pass, "fail": $fail, "total": $((pass+fail))},
  "checks": {
    "router": "$r_router",
    "internet": "$r_internet",
    "ha_ping": "$r_ha_ping",
    "ha_http": "$r_ha_http",
    "frigate_ping": "$r_frigate_ping",
    "frigate_http": "$r_frigate_http",
    "bambuddy": "$r_bambuddy",
    "p1s": "$r_p1s",
    "nas": "$r_nas",
    "mqtt": "$r_mqtt",
    "ventsys_boards": $ventsys_json,
    "ventsys_plugs": $plugs_json
  }
}
EOF
    fi
}

# ── ENTRY POINT ──────────────────────────────────────────────────────────────
if [ "$WATCH_MODE" -eq 1 ]; then
    while true; do
        run_checks
        sleep 60
    done
else
    run_checks
fi
