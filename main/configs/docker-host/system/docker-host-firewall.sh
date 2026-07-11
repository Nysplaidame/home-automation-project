#!/bin/sh
set -e

# Docker-published ports are DNATed before the normal UFW INPUT path.
# Match original host ports in DOCKER-USER so Docker-exposed services stay scoped.
iptables -N DOCKER-USER 2>/dev/null || true
iptables -F DOCKER-USER
iptables -A DOCKER-USER -m conntrack --ctstate RELATED,ESTABLISHED -j RETURN

# ntfy notifications: management, LAN, HA, monitoring, and Tailscale.
iptables -A DOCKER-USER -p tcp -s 192.168.10.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8085 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.1.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8085 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.20.101 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8085 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.60.10 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8085 -j RETURN
iptables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8085 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8085 -j DROP

# SearXNG: management, LAN, monitoring, Tailscale, HA, and local AI.
iptables -A DOCKER-USER -p tcp -s 192.168.10.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8087 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.1.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8087 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.20.101 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8087 -j RETURN
iptables -A DOCKER-USER -p tcp -s 172.30.32.0/23 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8087 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.20.104 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8087 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.60.10 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8087 -j RETURN
iptables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8087 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8087 -j DROP

# Whoogle: management, LAN, monitoring, and Tailscale only.
iptables -A DOCKER-USER -p tcp -s 192.168.10.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8088 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.1.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8088 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.60.10 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8088 -j RETURN
iptables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8088 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8088 -j DROP

# Immich UI: management, LAN, monitoring, and Tailscale.
iptables -A DOCKER-USER -p tcp -s 192.168.10.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 2283 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.1.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 2283 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.60.10 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 2283 -j RETURN
iptables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 2283 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 2283 -j DROP

# Mealie recipe and meal-planning UI: management, LAN, HA, monitoring, and Tailscale.
iptables -A DOCKER-USER -p tcp -s 192.168.10.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 9925 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.1.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 9925 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.20.101 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 9925 -j RETURN
iptables -A DOCKER-USER -p tcp -s 172.30.32.0/23 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 9925 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.60.10 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 9925 -j RETURN
iptables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 9925 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 9925 -j DROP

# Grocy food-stock UI/API: management, LAN, HA, monitoring, and Tailscale.
for source in 192.168.10.0/24 192.168.1.0/24 192.168.20.101 172.30.32.0/23 192.168.60.10; do
    iptables -A DOCKER-USER -p tcp -s "$source" -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 9283 -j RETURN
done
iptables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 9283 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 9283 -j DROP

# GardenKeeper UI: management, LAN, HA, monitoring, and Tailscale.
for source in 192.168.10.0/24 192.168.1.0/24 192.168.20.101 192.168.60.10; do
    iptables -A DOCKER-USER -p tcp -s "$source" -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8091 -j RETURN
done
iptables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8091 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8091 -j DROP

# GardenKeeper API: Home Assistant, management, monitoring, and Tailscale.
for source in 192.168.20.101 192.168.10.0/24 192.168.60.10; do
    iptables -A DOCKER-USER -p tcp -s "$source" -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8090 -j RETURN
done
iptables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8090 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8090 -j DROP

# Homepage UI: management, LAN, monitoring, and Tailscale.
for source in 192.168.10.0/24 192.168.1.0/24 192.168.60.10; do
    iptables -A DOCKER-USER -p tcp -s "$source" -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 3001 -j RETURN
done
iptables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 3001 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 3001 -j DROP

# Mermaid Viewer: LAN and Tailscale only.
iptables -A DOCKER-USER -p tcp -s 192.168.1.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8092 -j RETURN
iptables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8092 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8092 -j DROP

# Household Hub UI: management, LAN, monitoring, and Tailscale.
for source in 192.168.10.0/24 192.168.1.0/24 192.168.60.10; do
    iptables -A DOCKER-USER -p tcp -s "$source" -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8100 -j RETURN
done
iptables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8100 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8100 -j DROP

# Household Hub API: Home Assistant, management, LAN, monitoring, and Tailscale.
for source in 192.168.20.101 192.168.10.0/24 192.168.1.0/24 192.168.60.10; do
    iptables -A DOCKER-USER -p tcp -s "$source" -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8101 -j RETURN
done
iptables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8101 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8101 -j DROP

# Obsidian LiveSync CouchDB: management, LAN, monitoring, and Tailscale.
for source in 192.168.10.0/24 192.168.1.0/24 192.168.60.10; do
    iptables -A DOCKER-USER -p tcp -s "$source" -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 5984 -j RETURN
done
iptables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 5984 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 5984 -j DROP

# Dozzle admin log UI: management and monitoring only.
iptables -A DOCKER-USER -p tcp -s 192.168.10.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8081 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.60.10 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8081 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8081 -j DROP

# AdGuard admin UI: management, LAN, monitoring, and Tailscale interface.
iptables -A DOCKER-USER -p tcp -s 192.168.10.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8080 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.1.0/24 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8080 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.60.10 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8080 -j RETURN
iptables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8080 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 8080 -j DROP

# AdGuard DNS: router and monitoring only; clients should use router-local DNS.
iptables -A DOCKER-USER -p tcp -s 192.168.20.1 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 53 -j RETURN
iptables -A DOCKER-USER -p udp -s 192.168.20.1 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 53 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.60.10 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 53 -j RETURN
iptables -A DOCKER-USER -p udp -s 192.168.60.10 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 53 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 53 -j DROP
iptables -A DOCKER-USER -p udp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 53 -j DROP

iptables -A DOCKER-USER -j RETURN

# Docker also publishes several services on IPv6. The host has no LAN IPv6
# service policy; retain only the Tailscale path and let tailnet ACLs provide
# identity-level authorization. Match each published TCP port explicitly.
ip6tables -N DOCKER-USER 2>/dev/null || true
ip6tables -F DOCKER-USER
ip6tables -A DOCKER-USER -m conntrack --ctstate RELATED,ESTABLISHED -j RETURN
for port in 2283 3001 5984 8080 8081 8085 8087 8088 8090 8091 8092 8100 8101 9283 9925; do
    ip6tables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdstport "$port" -j RETURN
    ip6tables -A DOCKER-USER -p tcp -m conntrack --ctorigdstport "$port" -j DROP
done

# AdGuard DNS is deliberately IPv4-only from the router and monitoring host.
for proto in tcp udp; do
    ip6tables -A DOCKER-USER -p "$proto" -m conntrack --ctorigdstport 53 -j DROP
done
ip6tables -A DOCKER-USER -j RETURN
