---
title: Phase 07 - Tier 1 Apps
description: Ordered rebuild of AdGuard Home, Immich, Homepage, and Dozzle with acceptance and rollback gates
tags: [install, docker-host, tier1]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: active
---

# Phase 07 - Tier 1 Apps

## Purpose

Deploy the core docker-host services in a controlled order:

1. AdGuard Home, without removing router DNS fallback;
2. Immich, only after its OMV mount and matched backup boundary exist;
3. Homepage, after its links and local-CA TLS material are ready;
4. Dozzle, last, with a read-only Docker socket and admin-only access.

Phase 12 contains the final outage, denial, monitoring, and recovery drills.
This phase gets each service from blank source to locally validated without
claiming `Live` early.

## Current-state callout

All four services are currently live on VM 103. Immich media is OMV-backed;
its machine-learning container is intentionally stopped under the current VM
capacity policy. The tracked templates are rebuild source, not a copy of live
secrets, databases, TLS private keys, or generated application state.

## Runs on

- Admin laptop from repository root to stage tracked templates and use UIs.
- docker-host over SSH at `192.168.20.102` as `root`.
- OpenWrt router over SSH for direct AdGuard and fallback checks.
- Home Assistant local-CA signing workflow for the Homepage certificate.
- An approved Management/LAN client and an intentionally denied Guest/DMZ
  client for access tests.

## Stop conditions

- Phase 05 host firewall layers or Tailscale identity are not healthy.
- An existing stack or state directory has not been backed up before replacement.
- A tracked Compose file does not pass `docker compose config --quiet`.
- Immich's `/mnt/omv/immich` resolves to local VM storage or is absent.
- Homepage private-key material would leave docker-host or enter Git.
- A Docker-published port is reachable from a denied source.
- Router DNS fallback is not retained before AdGuard becomes preferred.

## Prerequisites

- Phase 05 host baseline and Phase 06 OMV mounts are complete.
- `docker-host-firewall.service` is active and the tracked route/firewall
  helpers are staged under `/tmp/docker-host-system/`.
- Router DNS policy still retains its documented public fallback.
- A current backup destination exists for application state.
- The [service matrix](../../reference/service-matrix.md),
  [access matrix](../../reference/access-matrix.md), and four service manuals
  have been reviewed.

## Inputs

- `<ADGUARD_ADMIN_PASSWORD>` entered only in the first-run UI.
- `<IMMICH_ADMIN_EMAIL>` and `<IMMICH_ADMIN_PASSWORD>` entered only in the UI.
- `<IMMICH_DB_PASSWORD>` generated locally and copied to the password manager.
- `<DOCKER_HOST_TAILSCALE_IP>` obtained from `tailscale ip -4`.
- A Homepage leaf certificate and CA chain signed by `Home Local CA`; the
  Homepage private key is generated and retained on docker-host.

## 1. Capture the empty-or-existing baseline

Run on: docker-host over SSH.

```sh
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
ss -lntup | grep -E ':(53|443|2283|3001|8080|8081)\b' || true
systemctl is-active docker-host-firewall.service
tailscale ip -4
findmnt --target /mnt/omv/immich
df -h / /mnt/omv/immich
```

Expected result: existing listeners/containers are understood, firewall unit is
`active`, one Tailscale IPv4 address is recorded, and the Immich target resolves
to the intended OMV NFS filesystem with adequate space.

If rebuilding over an existing service, stop it and back up its documented
state first. Do not overwrite an unexamined `/opt/stacks/<service>` directory.

Run on: docker-host over SSH for an existing deployment.

```sh
for service in adguard-home immich homepage dozzle; do
  if [ -f "/opt/stacks/$service/docker-compose.yml" ]; then
    (cd "/opt/stacks/$service" && docker compose stop)
  fi
done
```

Expected result: each existing stack stops cleanly. Stateful backup/restore
evidence must already exist before its directory is replaced.

Recovery: restart the unchanged old stack if staging cannot continue. If its
backup is absent or ambiguous, stop the rebuild and return to Phase 10.

## 2. Stage tracked templates without secrets

Run on: Admin laptop from repository root in PowerShell.

```powershell
ssh root@192.168.20.102 "rm -rf /tmp/tier1-stacks; mkdir -p /tmp/tier1-stacks"
scp -r .\main\configs\docker-host\stacks\adguard-home root@192.168.20.102:/tmp/tier1-stacks/
scp -r .\main\configs\docker-host\stacks\immich root@192.168.20.102:/tmp/tier1-stacks/
scp -r .\main\configs\docker-host\stacks\homepage root@192.168.20.102:/tmp/tier1-stacks/
scp -r .\main\configs\docker-host\stacks\dozzle root@192.168.20.102:/tmp/tier1-stacks/
```

Expected result: all four copies finish without error. The remote staging tree
contains examples and templates but no live `.env`, database, certificate key,
or application data.

Run on: docker-host over SSH on a blank or approved replacement build.

```sh
for service in adguard-home immich homepage dozzle; do
  install -d -m 0755 "/opt/stacks/$service"
  cp -a "/tmp/tier1-stacks/$service/." "/opt/stacks/$service/"
done
find /opt/stacks/{adguard-home,immich,homepage,dozzle} -maxdepth 2 -type f -printf '%m %p\n' | sort
```

Expected result: each stack has a Compose file; example files are present; no
`.env` or TLS private key appears unless created locally in later steps.

Recovery: compare the staged tree with the repository. Remove only the newly
copied blank destination after confirming it contains no pre-existing state.

## 3. Deploy AdGuard Home without making DNS brittle

Follow the [AdGuard manual](../services/adguard-home.md) for policy and backup
details. First create its non-secret node-address environment.

Run on: docker-host over SSH.

```sh
cd /opt/stacks/adguard-home
DOCKER_HOST_TAILSCALE_IP=$(tailscale ip -4)
test -n "$DOCKER_HOST_TAILSCALE_IP"
printf 'DOCKER_HOST_TAILSCALE_IP=%s\n' "$DOCKER_HOST_TAILSCALE_IP" >.env
chmod 600 .env
ip -4 address show dev tailscale0 | grep -F "$DOCKER_HOST_TAILSCALE_IP"
ss -lntup | grep -E ':(53|8080)\b' || true
docker compose config --quiet
docker compose up -d
docker compose ps
```

Expected result: the current node address exists on `tailscale0`, Compose exits
`0`, and `adguard-home` becomes `Up` with DNS bound only to the documented LAN
and Tailscale addresses plus admin port `8080`.

In the first-run UI at `http://adguard.home.local:8080/`, create the named admin
with `<ADGUARD_ADMIN_PASSWORD>`, leave DHCP disabled, configure approved
upstreams/blocklists, and retain OpenWrt as DHCP/local-DNS/fallback authority.

Run on: docker-host over SSH after first-run setup.

```sh
install -m 0755 /tmp/docker-host-system/docker-host-ufw-route-dns.sh \
  /usr/local/sbin/docker-host-ufw-route-dns.sh
/usr/local/sbin/docker-host-ufw-route-dns.sh
install -m 0644 /tmp/docker-host-system/adguard-home-compose.service \
  /etc/systemd/system/adguard-home-compose.service
systemctl daemon-reload
systemctl enable --now adguard-home-compose.service
systemctl reload docker-host-firewall.service
docker compose logs --tail=80
```

Expected result: the routed upstream-DNS rules apply, the boot gate waits for
the Tailscale address, firewall policy reloads, and logs show normal startup
without an upstream failure loop.

Run on: OpenWrt router over SSH.

```sh
nslookup example.com 192.168.20.102
```

Expected result: a public answer returns through AdGuard. Then query through
the router from an admin client; both public and `home.local` names must work.

Recovery: if port 53 is owned elsewhere, stop AdGuard and identify the owner;
do not bind `0.0.0.0` blindly. If upstream fails, inspect UFW route rules and
OpenWrt egress. If household DNS is affected, stop AdGuard and use the already
configured router fallback; run the controlled fallback drill in Phase 12.

## 4. Deploy Immich only on the verified OMV media mount

Follow the [Immich manual](../services/immich.md). The database remains local to
VM 103; its backup must be consistent with the remote media tree.

Run on: docker-host over SSH.

```sh
findmnt -n -o SOURCE,FSTYPE,TARGET --target /mnt/omv/immich
test "$(findmnt -n -o FSTYPE --target /mnt/omv/immich)" = nfs4
touch /mnt/omv/immich/.immich-write-test
rm /mnt/omv/immich/.immich-write-test
cd /opt/stacks/immich
cp .env.example .env
IMMICH_DB_PASSWORD=$(openssl rand -base64 36 | tr -d '\n')
while IFS= read -r line; do
  case "$line" in
    DB_PASSWORD=*) printf 'DB_PASSWORD=%s\n' "$IMMICH_DB_PASSWORD" ;;
    *) printf '%s\n' "$line" ;;
  esac
done <.env.example >.env.tmp
mv .env.tmp .env
chmod 600 .env
install -m 0600 /dev/null /root/immich-db-password.txt
printf '%s\n' "$IMMICH_DB_PASSWORD" >/root/immich-db-password.txt
unset IMMICH_DB_PASSWORD
docker compose config --quiet
```

Expected result: the target explicitly reports NFSv4, create/delete succeeds,
`.env` is mode `600`, the password is generated without terminal output, and
Compose validates. Copy the password file value into the password manager over
an approved private workflow, then retain or securely remove the root-only file
according to the secrets policy.

Run on: docker-host over SSH.

```sh
cd /opt/stacks/immich
docker compose up -d database redis immich-server
docker compose ps
docker compose exec -T database sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:2283/
systemctl reload docker-host-firewall.service
```

Expected result: database, Redis, and server become `Up`/healthy; PostgreSQL
reports `accepting connections`; HTTP returns `200` or its documented redirect;
and firewall policy reloads. Machine learning remains stopped until its
separate capacity gate passes.

Create the owner at `http://immich.home.local:2283/` with
`<IMMICH_ADMIN_EMAIL>` and `<IMMICH_ADMIN_PASSWORD>`. Do not import real media
until a matched database/media backup and isolated restore proof exist.

Recovery: if the mount is missing or local, stop `immich-server` immediately
before repairing NFS. For database failure, keep media untouched and diagnose
the local PostgreSQL volume. Never point a trial restored database at the live
media tree.

## 5. Issue Homepage TLS and deploy the portal

Follow the [Homepage manual](../services/homepage.md). Generate the private key
on docker-host; only its CSR leaves the host for signing by `Home Local CA`.

Run on: docker-host over SSH.

```sh
cd /opt/stacks/homepage
DOCKER_HOST_TAILSCALE_IP=$(tailscale ip -4)
test -n "$DOCKER_HOST_TAILSCALE_IP"
printf 'DOCKER_HOST_TAILSCALE_IP=%s\n' "$DOCKER_HOST_TAILSCALE_IP" >.env
chmod 600 .env
install -d -m 0700 tls
openssl req -new -newkey rsa:3072 -nodes \
  -keyout tls/homepage.key \
  -out tls/homepage.csr \
  -subj '/O=Home Automation/CN=homepage.home.local' \
  -addext 'subjectAltName=DNS:homepage.home.local,IP:192.168.20.102'
chmod 600 tls/homepage.key
```

Expected result: a mode-`600` private key and CSR are created. Sign the CSR
through the Phase 03/local-CA procedure and return only the signed chain as
`homepage.crt` plus `ca.crt` to `/opt/stacks/homepage/tls/`; never copy the CA
private key here.

Run on: docker-host over SSH after the signed files return.

```sh
cd /opt/stacks/homepage
openssl verify -CAfile tls/ca.crt tls/homepage.crt
openssl x509 -in tls/homepage.crt -noout -subject -issuer -dates -ext subjectAltName
docker compose config --quiet
docker compose up -d
install -m 0755 /tmp/docker-host-system/docker-host-ufw-homepage-previews.sh \
  /usr/local/sbin/docker-host-ufw-homepage-previews.sh
/usr/local/sbin/docker-host-ufw-homepage-previews.sh
systemctl reload docker-host-firewall.service
docker compose ps
```

Expected result: certificate verification prints `OK`; subject/SAN contains the
friendly DNS name and IP; Compose validates; Homepage and preview proxy are
`Up`; and source-scoped preview/firewall rules apply.

Run on: Admin laptop in PowerShell with `Home Local CA` trusted.

```powershell
Invoke-WebRequest https://192.168.20.102/api/services -UseBasicParsing
Invoke-WebRequest https://192.168.20.102/images/portal-background.svg -UseBasicParsing
```

Expected result: both return `StatusCode 200` with no certificate bypass or
warning. Validate one desktop and mobile viewport plus one direct link and one
preview.

Recovery: if only TLS/proxy fails, stop `preview-proxy` and use the internal
rollback endpoint `http://192.168.20.102:3001/` from an approved source. If YAML
breaks the portal, restore the last known-good config and call `/api/revalidate`.
Do not expose port `3001` more broadly as a permanent fix.

## 6. Deploy Dozzle last and prove socket/read restrictions

Follow the [Dozzle manual](../services/dozzle.md).

Run on: docker-host over SSH.

```sh
cd /opt/stacks/dozzle
docker compose config --quiet
docker compose up -d
systemctl reload docker-host-firewall.service
docker compose ps
docker inspect dozzle --format '{{range .Mounts}}{{println .Source .Destination .RW}}{{end}}'
curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8081/
```

Expected result: Dozzle is `Up`, the `/var/run/docker.sock` mount line ends in
`false`, and HTTP returns `200` or a documented authentication redirect.

Run on: an intentionally unapproved Guest/DMZ client in PowerShell.

```powershell
Test-NetConnection 192.168.20.102 -Port 8081
```

Expected result: `TcpTestSucceeded : False`; repeat from Management and expect
`True`.

Recovery: if socket mount is writable or access is broad, stop Dozzle and fix
Compose plus both host-firewall layers before restart. Do not grant the
container a privileged socket proxy or wider network to repair log visibility.

## 7. Validate all Tier 1 stacks in order

Run on: docker-host over SSH.

```sh
for service in adguard-home immich homepage dozzle; do
  printf '\n== %s ==\n' "$service"
  (cd "/opt/stacks/$service" && docker compose config --quiet && docker compose ps)
done
systemctl status adguard-home-compose.service docker-host-firewall.service --no-pager
iptables -S DOCKER-USER
ufw status verbose
findmnt --target /mnt/omv/immich
```

Expected result: every Compose render exits `0`; intended containers are `Up`
or healthy; AdGuard boot gate and firewall are active; source-specific rules
precede drops; and Immich's mount remains remote. The intentionally parked
Immich machine-learning service is recorded as such rather than counted failed.

Run on: Admin laptop in PowerShell from an approved network.

```powershell
Resolve-DnsName example.com -Server 192.168.10.1 -DnsOnly
Test-NetConnection 192.168.20.102 -Port 8080
Test-NetConnection 192.168.20.102 -Port 2283
Test-NetConnection 192.168.20.102 -Port 443
Test-NetConnection 192.168.20.102 -Port 8081
```

Expected result: DNS returns a public answer and all four approved UI paths have
`TcpTestSucceeded : True`.

## 8. Backup, monitor, and graduate one service at a time

Before marking any service `Live`:

- AdGuard: back up `conf/` and `work/`, prove router fallback, and monitor DNS
  plus admin UI.
- Immich: create a matched PostgreSQL/media backup, restore both into isolation,
  and complete the disposable-photo workflow.
- Homepage: back up Compose/config/assets/preview proxy and retain its `3001`
  rollback path; do not back up its private key into Git.
- Dozzle: retain Compose/firewall source; it has no critical app data.

Use [Phase 10](10-backups-monitoring-maintenance.md) for restore evidence and
[Phase 12](12-validation-troubleshooting.md) for controlled failure/recovery,
monitor alerts, and final denial tests.

## Failure recovery matrix

| Service/symptom | Nearest checks | Bounded recovery | Do not do |
|---|---|---|---|
| AdGuard will not bind | address presence, port owner, Compose/logs | stop conflict or correct exact bind; retain router fallback | bind all interfaces |
| Router DNS fails with AdGuard stopped | router upstream config/logs | restore last known-good router DNS through Phase 01 | distribute ad hoc client DNS |
| Immich mount absent/local | `findmnt`, NFS, server state | stop writer, repair mount, verify source, restart | create local fallback folder |
| Immich database unhealthy | space, `pg_isready`, logs, local volume | restore matched isolated DB/media set | delete Postgres volume blindly |
| Homepage certificate fails | chain, dates, SAN, client CA trust | reissue leaf; use internal `3001` rollback | use `-SkipCertificateCheck` as acceptance |
| Homepage content broken | Compose/YAML/logs/revalidation | restore known-good config/assets | expose proxy dynamically |
| Dozzle empty | container/logs, socket path/read-only state | correct read-only mount and restart | mount Docker socket writable |
| Any UI reachable from Guest/DMZ | UFW and `DOCKER-USER` counters/order | stop service, narrow tracked policy, reload and retest | rely only on app login |

## Completion checklist

- [ ] Existing state was backed up before any replacement.
- [ ] All four tracked templates pass `docker compose config --quiet` with local inputs.
- [ ] AdGuard direct/router queries pass and router fallback remains configured.
- [ ] Immich media mount is verified NFSv4 before every writer start.
- [ ] Immich database and local UI pass; machine-learning state is explicitly recorded.
- [ ] Homepage local-CA certificate verifies and HTTPS works without bypass.
- [ ] Homepage raw `3001` rollback endpoint remains source-scoped and tested.
- [ ] Dozzle Docker socket is read-only and Management/denied-source tests pass.
- [ ] UFW and `DOCKER-USER` rules survive reload and match the access matrix.
- [ ] Each service has backup, isolated restore, monitoring outage/recovery, and rollback evidence before `Live`.
