# Bambuddy

The tracked rebuild template uses a private bridge network (`10.240.23.0/24`),
not host networking. This makes the Docker `DOCKER-USER` policy enforce the UI
source scope on port `8000`.

The companion routed-UFW script allows this bridge only to the required Home
Assistant MQTT/API and P1S MQTT/FTP destinations. Install that script before
recreating the live stack; otherwise Docker's default-deny routed policy will
correctly prevent Bambuddy from reaching the printer or Home Assistant.

## Controlled migration

1. Back up `/opt/stacks/bambuddy/data` and `logs`; keep the live `.env`.
2. Install `system/docker-host-ufw-route-bambuddy.sh` and run it once.
3. Copy only `docker-compose.yml` from this directory into the live stack.
   Do not overwrite the live `.env`, `data`, or `logs` directories.
4. Run `docker compose config --quiet`, then `docker compose up -d --force-recreate`.
5. Confirm `docker network inspect bambuddy` reports `10.240.23.0/24`, then
   verify Bambuddy's UI, MQTT publishing and printer status.

The image is pinned by manifest digest. Change it only through a reviewed
maintenance window, recording the prior and candidate digests plus smoke-test
results.
