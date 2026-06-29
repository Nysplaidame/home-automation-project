#!/bin/sh
set -eu

iptables -N DOCKER-USER 2>/dev/null || true
iptables -F DOCKER-USER
iptables -A DOCKER-USER -m conntrack --ctstate RELATED,ESTABLISHED -j RETURN

for source in 192.168.20.101/32 192.168.10.0/24 192.168.1.0/24 192.168.60.10/32; do
  iptables -A DOCKER-USER -s "$source" -p tcp -m conntrack \
    --ctorigdst 192.168.20.104 --ctorigdstport 8081 -j RETURN
done
iptables -A DOCKER-USER -p tcp -m conntrack \
  --ctorigdst 192.168.20.104 --ctorigdstport 8081 -j DROP

for source in 192.168.10.0/24 192.168.1.0/24 192.168.60.10/32; do
  iptables -A DOCKER-USER -s "$source" -p tcp -m conntrack \
    --ctorigdst 192.168.20.104 --ctorigdstport 3002 -j RETURN
done
iptables -A DOCKER-USER -p tcp -m conntrack \
  --ctorigdst 192.168.20.104 --ctorigdstport 3002 -j DROP

for port in 10200 10300 10400; do
  for source in 192.168.20.101/32 192.168.60.10/32; do
    iptables -A DOCKER-USER -s "$source" -p tcp -m conntrack \
      --ctorigdst 192.168.20.104 --ctorigdstport "$port" -j RETURN
  done
  iptables -A DOCKER-USER -p tcp -m conntrack \
    --ctorigdst 192.168.20.104 --ctorigdstport "$port" -j DROP
done

iptables -A DOCKER-USER -j RETURN
