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
iptables -A DOCKER-USER -p tcp -s 192.168.60.10 -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 9925 -j RETURN
iptables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 9925 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 9925 -j DROP

# Grocy food-stock UI: management, LAN, monitoring, and Tailscale.
for source in 192.168.10.0/24 192.168.1.0/24 192.168.60.10; do
    iptables -A DOCKER-USER -p tcp -s "$source" -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 9283 -j RETURN
done
iptables -A DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 9283 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.102 --ctorigdstport 9283 -j DROP

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
