#!/bin/sh
set -eu

# Read-only proof for the explicit Docker-network and source-firewall policy.
# Run on docker-host after deploying the tracked Compose/firewall source.

mode="${1:---verify}"

for command in docker iptables ip6tables; do
    command -v "$command" >/dev/null 2>&1 || {
        echo "ERROR: required command not found: $command" >&2
        exit 2
    }
done

expected_networks='
homepage 10.240.1.0/24
adguard-home 10.240.2.0/24
dozzle 10.240.3.0/24
immich 10.240.4.0/24
mealie 10.240.5.0/24
grocy 10.240.6.0/24
obsidian-livesync 10.240.7.0/24
searxng 10.240.8.0/24
whoogle 10.240.9.0/24
jellyfin 10.240.10.0/24
calibre-web 10.240.11.0/24
atsumeru 10.240.12.0/24
mermaid-viewer 10.240.13.0/24
household-hub 10.240.14.0/24
local-alerting 10.240.15.0/24
download-gateway 10.240.20.0/24
gardenkeeper 10.240.21.0/24
docker-host-telegraf 10.240.22.0/24
bambuddy 10.240.23.0/24
gridfinity-layout-tool 172.32.0.0/24
vaultwarden 10.240.30.0/24
recomp-tracker 10.240.31.0/24
troubleshooting-dashboard 10.240.32.0/24
'

inventory() {
    printf '%-28s %-18s %s\n' 'NETWORK' 'SUBNET' 'CONTAINERS'
    docker network ls -q | while read -r id; do
        name="$(docker network inspect --format '{{.Name}}' "$id")"
        subnet="$(docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}}{{end}}' "$id")"
        containers="$(docker network inspect --format '{{range $id, $c := .Containers}}{{$c.Name}} {{end}}' "$id")"
        printf '%-28s %-18s %s\n' "$name" "${subnet:--}" "${containers:--}"
    done
    printf '\n%-28s %s\n' 'CONTAINER' 'IMAGE'
    docker ps --format '{{.Names}} {{.Image}}'
}

case "$mode" in
    --inventory)
        inventory
        exit 0
        ;;
    --verify)
        ;;
    *)
        echo "Usage: $0 [--inventory|--verify]" >&2
        exit 2
        ;;
esac

failed=0
printf '%s\n' "$expected_networks" | while read -r name subnet; do
    [ -n "$name" ] || continue
    actual="$(docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}}{{end}}' "$name" 2>/dev/null || true)"
    if [ "$actual" = "$subnet" ]; then
        printf 'PASS network %-24s %s\n' "$name" "$subnet"
    else
        printf 'FAIL network %-24s expected %s, got %s\n' "$name" "$subnet" "${actual:--}" >&2
        failed=1
    fi
done

# The pipeline above runs in a subshell on POSIX sh, so repeat failures with a
# direct loop that preserves the status for the final exit code.
while read -r name subnet; do
    [ -n "$name" ] || continue
    actual="$(docker network inspect --format '{{range .IPAM.Config}}{{.Subnet}}{{end}}' "$name" 2>/dev/null || true)"
    [ "$actual" = "$subnet" ] || failed=1
done <<EOF
$expected_networks
EOF

if iptables -C DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8000 -j DROP >/dev/null 2>&1; then
    echo 'PASS IPv4 Docker firewall drops unapproved Bambuddy traffic'
else
    echo 'FAIL missing IPv4 Docker firewall Bambuddy drop' >&2
    failed=1
fi

if [ "$(docker inspect bambuddy --format '{{.HostConfig.NetworkMode}}' 2>/dev/null || true)" = 'bambuddy' ]; then
    echo 'PASS Bambuddy uses its scoped bridge'
else
    echo 'FAIL Bambuddy is not attached to its scoped bridge' >&2
    failed=1
fi

if ip6tables -C DOCKER-USER -p tcp -m conntrack --ctorigdstport 8000 -j DROP >/dev/null 2>&1; then
    echo 'PASS IPv6 Docker firewall drops non-Tailscale Bambuddy traffic'
else
    echo 'FAIL missing IPv6 Docker firewall Bambuddy drop' >&2
    failed=1
fi

if iptables -C DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8420 -j DROP >/dev/null 2>&1; then
    echo 'PASS IPv4 Docker firewall drops unapproved Recomp traffic'
else
    echo 'FAIL missing IPv4 Docker firewall Recomp drop' >&2
    failed=1
fi

if ip6tables -C DOCKER-USER -p tcp -m conntrack --ctorigdstport 8420 -j DROP >/dev/null 2>&1; then
    echo 'PASS IPv6 Docker firewall drops non-Tailscale Recomp traffic'
else
    echo 'FAIL missing IPv6 Docker firewall Recomp drop' >&2
    failed=1
fi

if iptables -C DOCKER-USER -p tcp -s 192.168.10.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8094 -j RETURN >/dev/null 2>&1 \
   && iptables -C DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8094 -j DROP >/dev/null 2>&1; then
    echo 'PASS Troubleshooting Dashboard is management-scoped on IPv4'
else
    echo 'FAIL Troubleshooting Dashboard IPv4 scope is incomplete' >&2
    failed=1
fi

if ip6tables -C DOCKER-USER -p tcp -m conntrack --ctorigdstport 8094 -j DROP >/dev/null 2>&1; then
    echo 'PASS Troubleshooting Dashboard has no IPv6 exposure'
else
    echo 'FAIL Troubleshooting Dashboard IPv6 drop is missing' >&2
    failed=1
fi

if iptables -S DOCKER-USER | grep -q -- '--ctorigdstport 8101'; then
    echo 'FAIL stale Docker firewall policy for port 8101 remains' >&2
    failed=1
else
    echo 'PASS no stale Docker firewall policy for port 8101'
fi

exit "$failed"
