#!/bin/sh
# CT 114 llm-host: DOCKER-USER scoping for published container ports.
# Deploy to: /usr/local/sbin/llm-host-firewall.sh (run by docker.service.d/firewall.conf)
set -eu

iptables -N DOCKER-USER 2>/dev/null || true
iptables -F DOCKER-USER
iptables -A DOCKER-USER -m conntrack --ctstate RELATED,ESTABLISHED -j RETURN

for source in 192.168.20.101/32 192.168.20.102/32 192.168.10.0/24 192.168.1.0/24 192.168.60.10/32; do
  iptables -A DOCKER-USER -s "$source" -p tcp -m conntrack \
    --ctorigdst 192.168.20.104 --ctorigdstport 8081 -j RETURN
done
iptables -A DOCKER-USER -p tcp -m conntrack \
  --ctorigdst 192.168.20.104 --ctorigdstport 8081 -j DROP

for source in 192.168.20.102/32 192.168.10.0/24 192.168.1.0/24 192.168.60.10/32; do
  iptables -A DOCKER-USER -s "$source" -p tcp -m conntrack \
    --ctorigdst 192.168.20.104 --ctorigdstport 3002 -j RETURN
done
iptables -A DOCKER-USER -p tcp -m conntrack \
  --ctorigdst 192.168.20.104 --ctorigdstport 3002 -j DROP

# Voice Mixer (decision 09): management, LAN, monitoring, and docker-host
# (Tailscale subnet-router traffic arrives SNATed from 192.168.20.102).
for source in 192.168.20.102/32 192.168.10.0/24 192.168.1.0/24 192.168.60.10/32; do
  iptables -A DOCKER-USER -s "$source" -p tcp -m conntrack \
    --ctorigdst 192.168.20.104 --ctorigdstport 7860 -j RETURN
done
iptables -A DOCKER-USER -p tcp -m conntrack \
  --ctorigdst 192.168.20.104 --ctorigdstport 7860 -j DROP

for source in 192.168.20.102/32; do
  iptables -A DOCKER-USER -s "$source" -p tcp -m conntrack \
    --ctorigdst 192.168.20.104 --ctorigdstport 8082 -j RETURN
done
iptables -A DOCKER-USER -p tcp -m conntrack \
  --ctorigdst 192.168.20.104 --ctorigdstport 8082 -j DROP

# Obico failure detection is a machine-to-machine API.  Only Bambuddy on
# docker-host may submit snapshot-classification requests; the ML API itself
# fetches frames back from Bambuddy over the already allowed port 8000 path.
for source in 192.168.20.102/32; do
  iptables -A DOCKER-USER -s "$source" -p tcp -m conntrack \
    --ctorigdst 192.168.20.104 --ctorigdstport 3333 -j RETURN
done
iptables -A DOCKER-USER -p tcp -m conntrack \
  --ctorigdst 192.168.20.104 --ctorigdstport 3333 -j DROP

# 10201 = Metrocop Wyoming TTS (voice-mixer stack)
for port in 10200 10201 10300 10400; do
  for source in 192.168.20.101/32 192.168.60.10/32; do
    iptables -A DOCKER-USER -s "$source" -p tcp -m conntrack \
      --ctorigdst 192.168.20.104 --ctorigdstport "$port" -j RETURN
  done
  iptables -A DOCKER-USER -p tcp -m conntrack \
    --ctorigdst 192.168.20.104 --ctorigdstport "$port" -j DROP
done

iptables -A DOCKER-USER -j RETURN
