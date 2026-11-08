# Obico ML API on CT 114

This is the self-hosted inference-only component used by Bambuddy's failure
detection.  It is not the full Obico server: no Obico account, cloud service,
printer registration, or public endpoint is used.

## Placement and boundary

- Host: CT 114 `llm-host` (`192.168.20.104`, VLAN 20).
- API: TCP 3333, published only so Bambuddy on VM 103 (`192.168.20.102`) can
  request classifications.
- Camera frames: the ML API fetches Bambuddy's temporary snapshot URLs from
  `http://192.168.20.102:8000`; it never connects directly to the P1S.
- Limits: 2 CPUs and 5 GiB RAM.  CT 114 is allocated 6 CPUs / 28 GiB RAM so
  the resident 14B assistant and failure detector do not contend for the old
  20 GiB allocation.

The paired host UFW rule and `system/llm-host-firewall.sh` Docker rule must be
present before this port is exposed.  Do not add a router rule or public proxy.

## Deployment

The live stack lives at `/opt/stacks/obico-ml-api`.  CT 114 intentionally has
no WAN egress, so do **not** build or update there.  On an approved maintenance
builder, obtain and review the upstream `release` source, place its `ml_api`
directory at `obico-server/ml_api`, and build the image there.  The current
Docker host needs `--network=host` for that controlled build because its default
Docker bridge is unavailable.  Transfer the resulting image with `docker image
save` / `docker image load`, then start it on CT 114:

```bash
cp .env.example .env
chmod 0600 .env
docker compose config --quiet
docker compose up -d --no-build
curl -fsS http://127.0.0.1:3333/hc/
```

The derived Dockerfile uses HTTPS Ubuntu package sources so a controlled build
needs no port-80 WAN exception.  Record the upstream release commit before an
update.  Updates are manual maintenance actions: obtain and review the release
source, build externally, transfer the image, then confirm health and a
Bambuddy test.  Do not use an automatic updater for this model service.

## Bambuddy settings

In Bambuddy, set **Settings → Network → External URL** to
`http://192.168.20.102:8000`.  Then under **Settings → Failure Detection**:

- Enable detection.
- Set Obico ML API URL to `http://192.168.20.104:3333`.
- Leave the token empty unless `ML_API_TOKEN` was deliberately set in the
  live `.env`; if it is set, enter the same value here.
- Start with Medium sensitivity, a 10-second poll interval, `Notify only`,
  and the P1S as the only monitored printer.

Use Bambuddy's Test button, then confirm an ordinary active print has a green
`Safe` badge with a rising frame count.  Only after observing successful prints
and notifications should the action be changed to pause.  Do not configure
power-off until its physical safety interlock is separately accepted.
