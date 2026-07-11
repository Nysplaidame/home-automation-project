#!/bin/bash
# System Health Monitor
# Run from: Proxmox host (192.168.10.10).
# Windows management hosts use health_check.ps1 in this directory.
# Purpose: Single-command check of all critical system components
# Usage:
#   ./health_check.sh           — staged core check, human-readable output
#   ./health_check.sh --json    — JSON output for automation
#   ./health_check.sh --full    — include parked hardware/future-service checks
#   ./health_check.sh --watch   — repeat every 60s (Ctrl+C to stop)

set -u

# ── CONFIG ───────────────────────────────────────────────────────────────────
PROXMOX_IP="192.168.10.10"
HA_IP="192.168.20.101"
HA_PORT="8123"
FRIGATE_IP="192.168.30.20"
FRIGATE_PORT="8971"
DOCKER_HOST_IP="192.168.20.102"
BAMBUDDY_IP="$DOCKER_HOST_IP"
BAMBUDDY_PORT="8000"
IMMICH_URL="http://${DOCKER_HOST_IP}:2283/api/server/ping"
TRANSFER_PORTAL_URL="http://192.168.40.50:8088/"
LLM_HOST_IP="192.168.20.104"
LLAMACPP_URL="http://${LLM_HOST_IP}:8081/health"
OPENWEBUI_URL="http://${LLM_HOST_IP}:3002/health"
P1S_IP="192.168.35.200"   # VLAN 35 (Printers) — see docs/decisions/02-printer-vlan-architecture.md
# The printer's MQTT port 8883 is a TLS-authenticated broker and does not
# respond to unauthenticated TCP probes in a way that reliably confirms health.
# Ping is a better liveness check here; if the printer is powered on and
# network-connected, ping will succeed. MQTT connectivity is confirmed
# indirectly via Bambuddy (which would show HTTP errors if the broker is down).
NAS_IP="192.168.40.50"
NAS_NFS_PORT="2049"
MQTT_IP="192.168.20.101"
# MQTT TLS listener is live on 8883. Port 1883 remains open only as a staged
# bootstrap path until all clients are migrated.
MQTT_PORT="8883"

ESPHOME_PORT="6053"

# ── VENTSYS DEVICE REGISTRY ──────────────────────────────────────────────────
# All 20 ESPHome boards. Format: "IP:key:Label"
# key is used as the JSON field name (lowercase, underscores).
# Smart plugs are checked by ping (no ESPHome API port — commercial units).
VENTSYS_BOARDS=(
    "192.168.50.21:main_fan:Main Fan"
    "192.168.50.22:booth_fan:Booth Fan"
    "192.168.50.31:fdm_array_1:FDM Sensor Array 1"
    "192.168.50.32:fdm_array_2:FDM Sensor Array 2"
    "192.168.50.33:sla_array_1:SLA Sensor Array 1"
    "192.168.50.34:sla_array_2:SLA Sensor Array 2"
    "192.168.50.35:garage_air_sensor:Garage Air Sensor"
    "192.168.50.36:fdm_pipe_air_sensor:FDM Pipe Air Sensor"
    "192.168.50.37:sla_pipe_air_sensor:SLA Pipe Air Sensor"
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
    "192.168.50.73:plug_uv_1:Plug UV-1 (ventsys-plug-uv-1)"
    "192.168.50.74:plug_uv_2:Plug UV-2 (ventsys-plug-uv-2)"
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
FULL_MODE=0

for arg in "$@"; do
    case "$arg" in
        --json)  JSON_MODE=1 ;;
        --watch) WATCH_MODE=1 ;;
        --full)  FULL_MODE=1 ;;
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
        CHECK_RESULT="pass"
    else
        [ "$JSON_MODE" -eq 0 ] && printf "  ${RED}✗${NC} %s (%s) — unreachable\n" "$label" "$ip"
        fail=$((fail+1))
        CHECK_RESULT="fail"
    fi
}

check_port() {
    local label="$1"
    local ip="$2"
    local port="$3"
    if nc -z -w "$TIMEOUT" "$ip" "$port" 2>/dev/null; then
        [ "$JSON_MODE" -eq 0 ] && printf "  ${GREEN}✓${NC} %s (%s:%s)\n" "$label" "$ip" "$port"
        pass=$((pass+1))
        CHECK_RESULT="pass"
    else
        [ "$JSON_MODE" -eq 0 ] && printf "  ${RED}✗${NC} %s (%s:%s) — port closed\n" "$label" "$ip" "$port"
        fail=$((fail+1))
        CHECK_RESULT="fail"
    fi
}

check_http() {
    local label="$1"
    local url="$2"
    local code
    code=$(curl -k -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null || echo "000")
    if [ "$code" = "200" ] || [ "$code" = "302" ] || [ "$code" = "303" ] || [ "$code" = "401" ]; then
        [ "$JSON_MODE" -eq 0 ] && printf "  ${GREEN}✓${NC} %s — HTTP %s\n" "$label" "$code"
        pass=$((pass+1))
        CHECK_RESULT="pass"
    else
        [ "$JSON_MODE" -eq 0 ] && printf "  ${RED}✗${NC} %s — HTTP %s\n" "$label" "$code"
        fail=$((fail+1))
        CHECK_RESULT="fail"
    fi
}

check_ct_root_usage() {
    local ctid="$1"
    local label="$2"
    local threshold="$3"
    local status disk maxdisk used node
    node=$(hostname -s)
    status=$(pvesh get "/nodes/${node}/lxc/${ctid}/status/current" --output-format json 2>/dev/null || true)
    disk=$(printf '%s' "$status" | sed -n 's/.*"disk":\([0-9][0-9]*\).*/\1/p')
    maxdisk=$(printf '%s' "$status" | sed -n 's/.*"maxdisk":\([0-9][0-9]*\).*/\1/p')
    if [[ "$disk" =~ ^[0-9]+$ ]] && [[ "$maxdisk" =~ ^[1-9][0-9]*$ ]]; then
        used=$((disk * 100 / maxdisk))
    else
        used=""
    fi
    if [[ "$used" =~ ^[0-9]+$ ]] && [ "$used" -le "$threshold" ]; then
        [ "$JSON_MODE" -eq 0 ] && printf "  ${GREEN}✓${NC} %s root — %s%%\n" "$label" "$used"
        pass=$((pass+1)); CHECK_RESULT="pass"
    elif [[ "$used" =~ ^[0-9]+$ ]]; then
        [ "$JSON_MODE" -eq 0 ] && printf "  ${RED}✗${NC} %s root — %s%% (limit %s%%)\n" "$label" "$used" "$threshold"
        fail=$((fail+1)); CHECK_RESULT="fail"
    else
        [ "$JSON_MODE" -eq 0 ] && printf "  ${RED}✗${NC} %s root — usage unavailable\n" "$label"
        fail=$((fail+1)); CHECK_RESULT="fail"
    fi
}

check_ct_mount_source() {
    local ctid="$1"
    local label="$2"
    local target="$3"
    local expected="$4"
    local mount_record host_target source
    mount_record=$(pct config "$ctid" 2>/dev/null | awk -v target="$target" '$0 ~ /^mp[0-9]+:/ && $0 ~ "mp=" target "([,]|$)" {sub(/^[^:]+: /, ""); print; exit}')
    host_target=${mount_record%%,*}
    source=$(findmnt -rn -o SOURCE "$host_target" 2>/dev/null || true)
    if [ "$source" = "$expected" ]; then
        [ "$JSON_MODE" -eq 0 ] && printf "  ${GREEN}✓${NC} %s — %s\n" "$label" "$source"
        pass=$((pass+1)); CHECK_RESULT="pass"
    else
        [ "$JSON_MODE" -eq 0 ] && printf "  ${RED}✗${NC} %s — expected %s, got %s\n" "$label" "$expected" "${source:-unmounted}"
        fail=$((fail+1)); CHECK_RESULT="fail"
    fi
}

check_backup_age() {
    local label="$1"
    local pattern="$2"
    local max_hours="$3"
    local newest now age_hours
    newest=$(find /mnt/pve/omv-backups/dump -maxdepth 1 -type f -name "$pattern" -printf '%T@\n' 2>/dev/null | sort -nr | head -1)
    now=$(date +%s)
    if [ -n "$newest" ]; then
        age_hours=$(awk -v now="$now" -v newest="$newest" 'BEGIN {printf "%d", (now-newest)/3600}')
    else
        age_hours=""
    fi
    if [[ "$age_hours" =~ ^[0-9]+$ ]] && [ "$age_hours" -le "$max_hours" ]; then
        [ "$JSON_MODE" -eq 0 ] && printf "  ${GREEN}✓${NC} %s — %sh old\n" "$label" "$age_hours"
        pass=$((pass+1)); CHECK_RESULT="pass"
    else
        [ "$JSON_MODE" -eq 0 ] && printf "  ${RED}✗${NC} %s — newest archive %s\n" "$label" "${age_hours:+${age_hours}h old}${age_hours:-missing}"
        fail=$((fail+1)); CHECK_RESULT="fail"
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
    check_ping "Router" "$ROUTER_IP"; r_router="$CHECK_RESULT"
    check_ping "Internet" "$INTERNET_TARGET"; r_internet="$CHECK_RESULT"

    # ── CORE SERVICES ──
    [ "$JSON_MODE" -eq 0 ] && echo ""
    [ "$JSON_MODE" -eq 0 ] && echo "Core Services:"
    r_ha_ping="skipped"
    check_http "Home Assistant UI" "https://${HA_IP}:${HA_PORT}"; r_ha_http="$CHECK_RESULT"
    check_port "Frigate CT SSH" "$FRIGATE_IP" "22"; r_frigate_ping="$CHECK_RESULT"
    check_http "Frigate UI" "https://${FRIGATE_IP}:${FRIGATE_PORT}/api/version"; r_frigate_http="$CHECK_RESULT"
    check_port "Docker host VM SSH" "$DOCKER_HOST_IP" "22"; r_docker_host="$CHECK_RESULT"
    check_http "Bambuddy UI" "http://${BAMBUDDY_IP}:${BAMBUDDY_PORT}"; r_bambuddy="$CHECK_RESULT"
    check_http "Immich API" "$IMMICH_URL"; r_immich="$CHECK_RESULT"
    check_http "OMV Transfer Portal" "$TRANSFER_PORTAL_URL"; r_transfer_portal="$CHECK_RESULT"
    check_http "llama.cpp health" "$LLAMACPP_URL"; r_llamacpp="$CHECK_RESULT"
    check_http "Open WebUI health" "$OPENWEBUI_URL"; r_openwebui="$CHECK_RESULT"
    check_port "OMV backup NFS" "$NAS_IP" "$NAS_NFS_PORT"; r_nas="$CHECK_RESULT"
    # The P1S printer's MQTT port 8883 is the Bambu Lab printer-side MQTT broker
    # which only accepts authenticated connections from Bambu cloud clients —
    # a raw TCP connect returns a TLS handshake, not an open port, causing false
    # failures. Ping is the correct liveness check for a commercial device.
    r_p1s="skipped"
    check_port "MQTT Broker" "$MQTT_IP" "$MQTT_PORT"; r_mqtt="$CHECK_RESULT"

    if [ "$FULL_MODE" -eq 1 ]; then
        check_ping "P1S Printer" "$P1S_IP"; r_p1s="$CHECK_RESULT"
    elif [ "$JSON_MODE" -eq 0 ]; then
        echo "  - P1S check skipped until the printer is physically available"
    fi

    declare -A ventsys_results
    if [ "$FULL_MODE" -eq 1 ]; then
        # ── VENTSYS ESP32 BOARDS ──
        [ "$JSON_MODE" -eq 0 ] && echo ""
        [ "$JSON_MODE" -eq 0 ] && echo "VentSys ESP32 Boards (ESPHome API port ${ESPHOME_PORT}):"
        for entry in "${VENTSYS_BOARDS[@]}"; do
            ip="${entry%%:*}"; rest="${entry#*:}"; key="${rest%%:*}"; label="${rest##*:}"
            check_port "$label" "$ip" "$ESPHOME_PORT"
            ventsys_results["$key"]="$CHECK_RESULT"
        done
    fi

    declare -A plug_results
    if [ "$FULL_MODE" -eq 1 ]; then
        # ── VENTSYS SMART PLUGS ──
        [ "$JSON_MODE" -eq 0 ] && echo ""
        [ "$JSON_MODE" -eq 0 ] && echo "VentSys Smart Plugs (ping):"
        for entry in "${VENTSYS_PLUGS[@]}"; do
            ip="${entry%%:*}"; rest="${entry#*:}"; key="${rest%%:*}"; label="${rest##*:}"
            check_ping "$label" "$ip"
            plug_results["$key"]="$CHECK_RESULT"
        done
    fi

    # ── PROXMOX VMs (only if running on Proxmox host) ──
    if command -v qm >/dev/null 2>&1; then
        [ "$JSON_MODE" -eq 0 ] && echo ""
        [ "$JSON_MODE" -eq 0 ] && echo "Proxmox VMs:"
        # VM 101 and VM 104 are intentionally stopped rollback artefacts.
        for vmid in 100 102 103; do
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

        if command -v pct >/dev/null 2>&1; then
            [ "$JSON_MODE" -eq 0 ] && echo ""
            [ "$JSON_MODE" -eq 0 ] && echo "Proxmox LXCs:"
            for ctid in 111 114; do
                status=$(pct status "$ctid" 2>/dev/null | awk '{print $2}' || echo "unknown")
                name=$(pct config "$ctid" 2>/dev/null | awk '/^hostname:/ {print $2}' || echo "ct-$ctid")
                if [ "$status" = "running" ]; then
                    [ "$JSON_MODE" -eq 0 ] && printf "  ${GREEN}✓${NC} CT %s (%s) — running\n" "$ctid" "$name"
                    pass=$((pass+1))
                else
                    [ "$JSON_MODE" -eq 0 ] && printf "  ${RED}✗${NC} CT %s (%s) — %s\n" "$ctid" "$name" "$status"
                    fail=$((fail+1))
                fi
            done

            [ "$JSON_MODE" -eq 0 ] && echo ""
            [ "$JSON_MODE" -eq 0 ] && echo "Guest capacity and required mounts:"
            check_ct_root_usage 111 "CT 111 Frigate" 80; r_ct111_root="$CHECK_RESULT"
            check_ct_root_usage 114 "CT 114 local AI" 80; r_ct114_root="$CHECK_RESULT"
            check_ct_mount_source 111 "CT 111 recording mount" "/mnt/nas/frigate" "192.168.40.50:/export/frigate"; r_frigate_mount="$CHECK_RESULT"

            [ "$JSON_MODE" -eq 0 ] && echo ""
            [ "$JSON_MODE" -eq 0 ] && echo "Backup freshness (maximum 36h):"
            check_backup_age "VM 100 archive" "vzdump-qemu-100-*.vma.zst" 36; r_backup_vm100="$CHECK_RESULT"
            check_backup_age "VM 102 archive" "vzdump-qemu-102-*.vma.zst" 36; r_backup_vm102="$CHECK_RESULT"
            check_backup_age "VM 103 archive" "vzdump-qemu-103-*.vma.zst" 36; r_backup_vm103="$CHECK_RESULT"
            check_backup_age "CT 111 archive" "vzdump-lxc-111-*.tar.zst" 36; r_backup_ct111="$CHECK_RESULT"
            check_backup_age "CT 114 archive" "vzdump-lxc-114-*.tar.zst" 36; r_backup_ct114="$CHECK_RESULT"
        fi

        # Proxmox disk usage
        if [ "$JSON_MODE" -eq 0 ]; then
            echo ""
            echo "Proxmox Storage:"
            while read -r storage total used; do
                [ -z "$storage" ] && continue
                pct=$((used * 100 / total))
                threshold=85
                [ "$storage" = "omv-backups" ] && threshold=80
                if [ "$pct" -gt "$threshold" ]; then
                    printf "  ${RED}✗${NC}  %-20s %d%% (limit %d%%)\n" "$storage" "$pct" "$threshold"
                    fail=$((fail+1))
                else
                    printf "  ${GREEN}✓${NC}  %-20s %d%%\n" "$storage" "$pct"
                    pass=$((pass+1))
                fi
            done < <(pvesm status 2>/dev/null | awk 'NR>1 && $4>0 {print $1, $4, $5}')
        fi
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
        # JSON output for automated consumers such as dashboards and alerting scripts.
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
    "docker_host": "$r_docker_host",
    "bambuddy": "$r_bambuddy",
    "immich": "$r_immich",
    "transfer_portal": "$r_transfer_portal",
    "llamacpp": "$r_llamacpp",
    "openwebui": "$r_openwebui",
    "p1s": "$r_p1s",
    "nas": "$r_nas",
    "mqtt": "$r_mqtt",
    "ct111_root": "${r_ct111_root:-skipped}",
    "ct114_root": "${r_ct114_root:-skipped}",
    "frigate_mount": "${r_frigate_mount:-skipped}",
    "backup_vm100": "${r_backup_vm100:-skipped}",
    "backup_vm102": "${r_backup_vm102:-skipped}",
    "backup_vm103": "${r_backup_vm103:-skipped}",
    "backup_ct111": "${r_backup_ct111:-skipped}",
    "backup_ct114": "${r_backup_ct114:-skipped}",
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
    [ "$fail" -eq 0 ]
fi
