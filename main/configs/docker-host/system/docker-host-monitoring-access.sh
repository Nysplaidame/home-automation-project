#!/bin/sh
set -eu
# Host-network Homepage HTTPS and its ntfy proxy, only from monitoring VM102.
ufw allow from 192.168.60.10 to 192.168.20.102 port 443 proto tcp comment 'Monitoring Homepage HTTPS'
ufw allow from 192.168.60.10 to 192.168.20.102 port 8193 proto tcp comment 'Monitoring ntfy HTTPS'
