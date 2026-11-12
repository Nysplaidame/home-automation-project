#!/bin/sh
set -e

# Docker-published ports bypass ordinary UFW INPUT processing. Match original
# destination ports in DOCKER-USER so VM 102 services stay source-scoped.
iptables -N DOCKER-USER 2>/dev/null || true
iptables -F DOCKER-USER
iptables -A DOCKER-USER -m conntrack --ctstate RELATED,ESTABLISHED -j RETURN

# OMV's existing SMART-health push must survive every full chain rebuild.
iptables -A DOCKER-USER -p tcp -s 192.168.40.50 -m conntrack --ctorigdst 192.168.60.10 --ctorigdstport 3001 -j RETURN

# Grafana and Uptime Kuma: management, the Homepage HTTPS preview proxy,
# HA health checks, and Tailscale clients.
for port in 3000 3001; do
    for source in 192.168.10.0/24 192.168.20.101 192.168.20.102 100.64.0.0/10; do
        iptables -A DOCKER-USER -p tcp -s "$source" -m conntrack --ctorigdst 192.168.60.10 --ctorigdstport "$port" -j RETURN
    done
    iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.60.10 --ctorigdstport "$port" -j DROP
done

# InfluxDB: management, HA, and docker-host Telegraf only; no Tailscale route.
for source in 192.168.10.0/24 192.168.20.101 192.168.20.102; do
    iptables -A DOCKER-USER -p tcp -s "$source" -m conntrack --ctorigdst 192.168.60.10 --ctorigdstport 8086 -j RETURN
done
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.60.10 --ctorigdstport 8086 -j DROP

# Loki ingestion is private: only the docker-host Alloy collector may reach it.
# Loki itself verifies the collector's client certificate (mTLS).
iptables -A DOCKER-USER -p tcp -s 192.168.20.102 -m conntrack --ctorigdst 192.168.60.10 --ctorigdstport 3100 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.60.10 --ctorigdstport 3100 -j DROP

# Router syslog reaches the Telegraf container through its published UDP port.
iptables -A DOCKER-USER -p udp -s 192.168.60.1 -m conntrack --ctorigdst 192.168.60.10 --ctorigdstport 514 -j RETURN
iptables -A DOCKER-USER -p udp -m conntrack --ctorigdst 192.168.60.10 --ctorigdstport 514 -j DROP

iptables -A DOCKER-USER -j RETURN
