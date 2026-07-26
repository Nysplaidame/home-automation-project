#!/bin/sh
set -eu

# Docker-published ports traverse DOCKER-USER before UFW INPUT. Keep the
# Homepage preview proxy's access to Grafana and Uptime Kuma source-scoped.
for port in 3000 3001; do
  if ! iptables -C DOCKER-USER -p tcp -s 192.168.20.102/32 \
    -m conntrack --ctorigdst 192.168.60.10 --ctorigdstport "$port" \
    -j RETURN 2>/dev/null; then
    iptables -I DOCKER-USER 2 -p tcp -s 192.168.20.102/32 \
      -m conntrack --ctorigdst 192.168.60.10 --ctorigdstport "$port" \
      -j RETURN
  fi
done
