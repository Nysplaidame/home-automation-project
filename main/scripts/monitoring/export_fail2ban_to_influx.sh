#!/bin/sh
# Export Fail2ban jail counters to InfluxDB line protocol.

set -eu

: "${INFLUX_URL:=http://192.168.60.10:8086}"
: "${INFLUX_ORG:=homelab}"
: "${INFLUX_BUCKET:=dockerhost}"
: "${JAILS:=sshd}"

if [ -z "${INFLUX_TOKEN:-}" ]; then
    echo "INFLUX_TOKEN is required" >&2
    exit 1
fi

escape_tag() {
    printf '%s' "$1" | sed 's/\\/\\\\/g; s/ /\\ /g; s/,/\\,/g; s/=/\\=/g'
}

now="$(date +%s)"
payload=""

for jail in $JAILS; do
    status="$(fail2ban-client status "$jail" 2>/dev/null || true)"
    [ -n "$status" ] || continue

    currently_failed="$(printf '%s\n' "$status" | awk -F: '/Currently failed/ {gsub(/[ \t]/, "", $2); print $2; exit}')"
    total_failed="$(printf '%s\n' "$status" | awk -F: '/Total failed/ {gsub(/[ \t]/, "", $2); print $2; exit}')"
    currently_banned="$(printf '%s\n' "$status" | awk -F: '/Currently banned/ {gsub(/[ \t]/, "", $2); print $2; exit}')"
    total_banned="$(printf '%s\n' "$status" | awk -F: '/Total banned/ {gsub(/[ \t]/, "", $2); print $2; exit}')"

    currently_failed="${currently_failed:-0}"
    total_failed="${total_failed:-0}"
    currently_banned="${currently_banned:-0}"
    total_banned="${total_banned:-0}"

    jail_tag="$(escape_tag "$jail")"
    payload="${payload}fail2ban,jail=${jail_tag} currently_failed=${currently_failed}i,total_failed=${total_failed}i,currently_banned=${currently_banned}i,total_banned=${total_banned}i ${now}
"
done

[ -n "$payload" ] || exit 0

curl -fsS \
    -X POST \
    -H "Authorization: Token ${INFLUX_TOKEN}" \
    --data-binary "$payload" \
    "${INFLUX_URL%/}/api/v2/write?org=${INFLUX_ORG}&bucket=${INFLUX_BUCKET}&precision=s" >/dev/null

printf 'exported Fail2ban metrics for: %s\n' "$JAILS"
