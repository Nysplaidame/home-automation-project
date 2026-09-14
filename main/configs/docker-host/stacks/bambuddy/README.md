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

## Current boundary and installation

September source review: the running host-network exception remains until P1S
ports21/8883 are reachable and the bridge migration is accepted. The printer is
uncommissioned. The migration above is a future maintenance procedure, not the
current runtime description. Use the [docker-host guide](../../../../scripts/setup/proxmox/docker_host_setup_guide.md)
for blank VM/stack setup; preserve the existing `.env` on recovery. Record the
actual running image and network mode before comparing the pinned bridge template.

## Backup, isolated restore and updates

1. Stop Bambuddy during a quiet window and confirm the container is stopped.
   Preserve `data/`, `logs/`, protected `.env`, Compose, ownership/permissions,
   running image ID/digest and host-network/firewall settings as one checkpoint.
   Copy it to protected storage outside VM103; the central app-data script does
   not capture Bambuddy. Retain the previous image. A live directory copy alone
   is not database consistency evidence.
2. On a disposable Docker VM without production connectivity, restore copied
   data and the saved image. Remove `container_name` and host networking, use
   an isolated bridge, bind UI8000 only to loopback, disable restart, and replace
   MQTT/HA/printer credentials with test values. Never connect restored printer
   or automation identities to the household network.
3. Confirm the UI starts and saved non-secret configuration/history is plausible.
   Keep P1S/MQTT connectivity marked untested. Stop the clone; record checkpoint,
   image, data checks and outcome. Hardware acceptance requires a separate
   authorized idle-status/MQTT test, not an unattended print.
4. For update, review the new image, test copied data first, then update only
   Bambuddy in maintenance. Keep network migration a separately recorded change.
   On failure stop it, preserve failed data, restore the old image and matched
   data/config checkpoint, then validate UI and the intended network boundary.
   Do not downgrade a binary against potentially migrated live data.

Diagrams: [service placement](../../../../docs/diagrams/infrastructure/docker-host-service-placement.mermaid),
[access](../../../../docs/diagrams/network/security-access-flow.mermaid),
[storage](../../../../docs/diagrams/storage/storage-and-backup-flow.mermaid).
