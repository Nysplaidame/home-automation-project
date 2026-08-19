---
title: Phase 05 - docker-host
description: Rebuild VM 103 Docker, Compose, firewall, Tailscale host routes, and rollback baseline
tags: [install, docker-host, tailscale]
created: 2026-05-24
modified: 2026-08-09
type: install-guide
status: active
---

# Phase 05 - docker-host

## Purpose

Turn prepared Debian VM 103 into the trusted Docker Compose host for internal
services and the narrow Tailscale host-route gateway. This phase establishes the
host; application stacks are introduced in Phases 07-09.

## Current-state callout

The current VM is Debian 13 at `192.168.20.102`, uses the required
`/opt/stacks/<service>/` layout, and is already running live workloads. It
advertises only the approved HA, Frigate, OMV, and monitoring host routes. The
fresh path below remains authoritative for rebuilding it without relying on
that live state.

## Runs on

- Proxmox host shell for VM identity and snapshot/rollback checks.
- docker-host local console or SSH at `192.168.20.102` as `root`.
- Admin laptop from the repository root to stage tracked firewall files.
- Tailscale admin console for explicit route approval and ACL verification.

## Stop conditions

- VM 103 identity, VLAN, disk, or address differs from the approved baseline.
- The router's bounded maintenance egress is absent during package installation
  or remains enabled after it.
- Docker's official repository key/fingerprint or Debian codename is unexpected.
- Applying UFW or `DOCKER-USER` would remove the local console recovery path.
- Tailscale proposes or retains any broad VLAN route.
- A stateful stack would write to an absent OMV mount.

## Prerequisites

- Phase 02 prepared VM 103 with Debian 13, VLAN 20, static
  `192.168.20.102/24`, gateway/DNS `192.168.20.1`, and an admin SSH key.
- Router policy provides bounded TCP `80/443` maintenance egress for only
  `192.168.20.102` during package/image operations.
- `<TAILSCALE_AUTH_KEY>` is an ephemeral, reusable-or-one-off key with the
  minimum approved tags and expiry policy.
- The tracked `configs/docker-host/system/` files have been reviewed against
  the current access and service matrices.

## Inputs

- `<TAILSCALE_AUTH_KEY>` entered at a hidden prompt; never placed literally in
  the command line, repository, or evidence output.

## 1. Verify VM 103 before changing the guest

Run on: Proxmox host shell.

```sh
qm status 103
qm config 103 | grep -E '^(name|memory|cores|machine|bios|net0|onboot|startup|scsi0|ipconfig0|nameserver):'
```

Expected result: VM 103 is `running`; name is `docker-host`; VLAN tag is `20`;
the MAC and storage match the inventory; `onboot` is `1`; startup order is `3`;
and cloud-init address/gateway are `192.168.20.102/24` and `192.168.20.1`.

Recovery: stop and correct the guest shell in Phase 02 before installing
anything. Do not repair a wrong VLAN by adding a second in-guest address.

## 2. Establish the Debian and recovery baseline

Run on: docker-host local console or SSH.

```sh
hostnamectl
cat /etc/os-release
ip -brief address
ip route show
findmnt /
df -h /
systemctl --failed --no-pager
```

Expected result: hostname `docker-host`, Debian 13, only the planned VLAN 20
address/default route, a mounted root filesystem with adequate space, and no
unexplained failed units.

Run on: docker-host local console or SSH while maintenance egress is active.

```sh
apt-get update
apt-get install -y ca-certificates curl gnupg ufw fail2ban qemu-guest-agent jq openssl less
systemctl enable --now qemu-guest-agent
systemctl is-active qemu-guest-agent
```

Expected result: APT exits `0` and the final command prints `active`.

Run on: Proxmox host shell.

```sh
qm agent 103 ping
vzdump 103 --mode snapshot --compress zstd --storage omv-backups
```

Expected result: agent ping exits silently with `0`; `vzdump` ends with
`TASK OK`. Record the backup volume ID before continuing.

Recovery: use the local console for network/package repair. If the baseline
cannot be recovered safely, restore the new archive as an isolated VM ID and
validate it before replacing VM 103.

## 3. Install Docker Engine from its signed Debian repository

Run on: docker-host over SSH while bounded maintenance egress is active.

```sh
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg \
  | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
. /etc/os-release
printf '%s\n' \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $VERSION_CODENAME stable" \
  >/etc/apt/sources.list.d/docker.list
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable --now docker
```

Expected result: packages install without unsigned-repository warnings and
Docker becomes active.

Run on: docker-host over SSH.

```sh
docker --version
docker compose version
systemctl is-active docker
docker run --rm hello-world
```

Expected result: version strings print, Docker is `active`, and the test image
prints `Hello from Docker!`. Remove the test container automatically with
`--rm`; retaining the cached image is harmless.

Recovery: inspect `/etc/apt/sources.list.d/docker.list`, the Debian codename,
key permissions, DNS/time, and maintenance egress. Do not install an unrelated
convenience script over a broken signed-repository setup.

## 4. Establish the Compose filesystem policy

Run on: docker-host over SSH.

```sh
install -d -m 0755 /opt/stacks
findmnt --target /opt/stacks
stat -c '%U:%G %a %n' /opt/stacks
docker compose version
```

Expected result: `/opt/stacks` resolves to the VM's intended root/storage,
ownership is `root:root`, mode is `755`, and Compose v2 is available. Every
stack must later live at `/opt/stacks/<service>/`; do not scatter Compose files
under `/root`, `/home`, or `/srv`.

Recovery: stop any misplaced stack, copy its Compose and state through that
service's backup/restore path, validate the new directory, then remove the old
deployment only after the new one works.

## 5. Apply host firewall and Docker-published-port policy

UFW protects host listeners and routed traffic. Docker-published ports are also
filtered in `DOCKER-USER` because Docker DNAT can bypass the normal UFW input
path.

Run on: Admin laptop from repository root in PowerShell.

```powershell
scp -r .\main\configs\docker-host\system root@192.168.20.102:/tmp/docker-host-system
```

Expected result: SCP finishes without error and creates the tracked files under
`/tmp/docker-host-system/` on VM 103.

Run on: docker-host local console or SSH.

```sh
ufw default deny incoming
ufw default allow outgoing
ufw default deny routed
ufw allow from 192.168.10.0/24 to any port 22 proto tcp comment 'Management SSH'
ufw --force enable
install -m 0755 /tmp/docker-host-system/docker-host-firewall.sh /usr/local/sbin/docker-host-firewall.sh
install -m 0644 /tmp/docker-host-system/docker-host-firewall.service /etc/systemd/system/docker-host-firewall.service
install -d -m 0755 /etc/fail2ban/jail.d
install -m 0644 /tmp/docker-host-system/docker-host-fail2ban-sshd.local /etc/fail2ban/jail.d/docker-host-sshd.local
systemctl daemon-reload
systemctl enable --now fail2ban docker-host-firewall.service
```

Expected result: UFW reports active with default deny incoming/routed;
Fail2ban and the firewall unit become active/exited without error.

Run on: docker-host local console or SSH.

```sh
ufw status verbose
systemctl status docker-host-firewall.service --no-pager
iptables -S DOCKER-USER
ip6tables -S DOCKER-USER
fail2ban-client status sshd
```

Expected result: management SSH is allowed; source-scoped `RETURN` rules precede
service-specific `DROP` rules; both chains end in a general `RETURN`; and the
SSH jail is running.

Recovery: keep the local console open. If approved SSH is lost, run
`ufw disable`, stop `docker-host-firewall.service`, correct the tracked policy,
and reapply both layers. Never leave UFW disabled after the repair or add a
broad allow rule as the final fix.

## 6. Install Tailscale without exposing the key

Install Tailscale through its official Debian repository during the same
bounded maintenance window. Then enter the auth key at a hidden prompt.

Run on: docker-host local console or SSH after Tailscale package installation.

```sh
systemctl enable --now tailscaled
printf '%s\n' 'net.ipv4.ip_forward = 1' >/etc/sysctl.d/99-tailscale-subnet-router.conf
sysctl -p /etc/sysctl.d/99-tailscale-subnet-router.conf
read -r -s -p 'Tailscale auth key: ' TS_AUTH_KEY; printf '\n'
tailscale up --auth-key="$TS_AUTH_KEY" --accept-dns=false --hostname=docker-host \
  --advertise-routes=192.168.20.101/32,192.168.30.20/32,192.168.40.50/32,192.168.60.10/32
unset TS_AUTH_KEY
```

Expected result: forwarding prints `net.ipv4.ip_forward = 1`; `tailscale up`
returns without authentication error. Approve only the four `/32` routes in the
admin console and apply the intended ACL/tag policy.

Run on: docker-host over SSH.

```sh
tailscale status
tailscale ip -4
tailscale debug prefs | grep -E 'AdvertiseRoutes|RouteAll|CorpDNS'
```

Expected result: docker-host is online, one Tailscale IPv4 address prints, the
advertised set contains exactly the four approved `/32` routes, default-route
acceptance is off, and Tailscale DNS acceptance remains off.

Recovery: run `tailscale down` if identity, tags, or routes are wrong; revoke
the node/key in the admin console; correct the command; authenticate again.
Never approve `/24` routes to make one host reachable.

## 7. Add only required routed UFW paths

After the corresponding remote-access decision is approved, install the tracked
route script for monitoring and Frigate. AdGuard's routed upstream-DNS and
Homepage-preview scripts belong with those services, not the empty host.

Run on: docker-host over SSH.

```sh
install -m 0755 /tmp/docker-host-system/docker-host-ufw-route-monitoring-tailscale.sh \
  /usr/local/sbin/docker-host-ufw-route-monitoring-tailscale.sh
/usr/local/sbin/docker-host-ufw-route-monitoring-tailscale.sh
ufw status numbered
```

Expected result: routed allows exist only from `tailscale0` to monitoring
`3000/3001` and Frigate HTTPS `8971`; there is no routed allow to InfluxDB,
Frigate port `5000`, or a whole subnet.

Recovery: delete the exact numbered incorrect UFW rule from local console,
correct the tracked script, rerun it, and repeat both allowed and denied tests.

## 8. Close maintenance egress and prove denial

Remove the router's temporary Docker-host update rule after packages and
approved images are present.

Run on: docker-host over SSH after router maintenance egress is removed.

```sh
curl -4I --connect-timeout 5 --max-time 8 https://download.docker.com/
apt-get update
```

Expected result: direct external access fails or times out under the normal
policy. `apt-get update` may succeed only through the documented apt cache;
record which path was used. An unrestricted direct success is a failed gate.

Recovery: if general egress still works, inspect the OpenWrt rule and forwarding
counter and remove the narrow temporary rule. If updates are needed later,
reopen only the bounded maintenance rule for a recorded window.

## 9. Validate positive and denied access

Run on: Admin laptop in PowerShell from Management VLAN.

```powershell
Test-NetConnection 192.168.20.102 -Port 22
```

Expected result: `TcpTestSucceeded : True`.

Run on: an intentionally unapproved Guest/DMZ client in PowerShell.

```powershell
Test-NetConnection 192.168.20.102 -Port 22
Test-NetConnection 192.168.20.102 -Port 8081
```

Expected result: both return `TcpTestSucceeded : False` while public internet
still works. Port `8081` may not listen until Dozzle is deployed; repeat this
negative test in Phase 07 with the service running.

Run on: approved Tailscale client in PowerShell.

```powershell
Test-NetConnection 192.168.20.101 -Port 8123
Test-NetConnection 192.168.30.20 -Port 8971
Test-NetConnection 192.168.40.50 -Port 443
Test-NetConnection 192.168.60.10 -Port 3000
Test-NetConnection 192.168.60.10 -Port 8086
```

Expected result: the four approved service paths succeed; InfluxDB `8086`
fails. A stopped downstream service is recorded as `BLOCKED`, not treated as
proof of route denial.

## 10. Prove restart and rollback behavior

Run on: docker-host local console or SSH.

```sh
systemctl restart docker
systemctl restart docker-host-firewall.service
systemctl restart tailscaled
systemctl is-active docker tailscaled
systemctl is-active docker-host-firewall.service
iptables -S DOCKER-USER | tail -n 5
tailscale status
```

Expected result: Docker and Tailscale are `active`; the oneshot firewall is
`active`; the chain is repopulated after Docker restart; and the Tailscale node
and exact route advertisements return.

If the host baseline must be rolled back, shut down VM 103 and restore the
Phase 02/Step 2 archive as a new isolated VM ID with NIC disconnected. Validate
identity, filesystem, Docker state, and firewall there before replacing the
production guest.

## End-of-phase validation

Run on: docker-host over SSH.

```sh
hostname
docker --version
docker compose version
docker info --format '{{.ServerVersion}} {{.CgroupDriver}}'
stat -c '%U:%G %a %n' /opt/stacks
systemctl --failed --no-pager
ufw status verbose
iptables -S DOCKER-USER
tailscale status
findmnt -t nfs,nfs4
```

Expected result: identity and versions are recorded, `/opt/stacks` is
`root:root 755`, no unexplained unit is failed, firewall layers are present,
only four host routes are advertised, and no NFS dependency is claimed until
Phase 06 mounts it.

## Failure recovery matrix

| Symptom | Nearest checks | Bounded recovery | Do not do |
|---|---|---|---|
| Wrong VM/VLAN/IP | `qm config`, guest `ip route` | repair Phase 02 shell before install | add compensating guest routes |
| Docker APT fails | time, DNS, repo line/key, maintenance rule | correct signed repo and retry | pipe an unknown install script to shell |
| Docker does not start | journal, disk, containerd | fix baseline or restore isolated VM backup | delete `/var/lib/docker` blindly |
| SSH lost after UFW | local console, numbered rules | temporarily disable, correct source rule, re-enable | leave UFW disabled |
| Published port too broad | UFW plus `DOCKER-USER` counters | stop stack; narrow tracked rules; reload | rely on UFW alone |
| Tailscale route absent | daemon, node auth, route approval, ACL | approve exact `/32` and retest | advertise a VLAN `/24` |
| Wrong Tailscale identity/routes | `tailscale status/debug prefs` | `tailscale down`, revoke, re-authenticate | keep an ambiguously tagged node |
| Host regression after change | Proxmox backup and console | isolated restore then deliberate promotion | overwrite live VM with an untested restore |

## Completion checklist

- [ ] VM 103 identity, VLAN, resources, and guest baseline are recorded.
- [ ] QEMU agent works and a pre-host-build Proxmox archive has `TASK OK`.
- [ ] Docker Engine and Compose v2 are installed from the signed official repository.
- [ ] `/opt/stacks` policy is in place and no service is deployed elsewhere.
- [ ] UFW, Fail2ban, and persistent `DOCKER-USER` policy survive Docker restart.
- [ ] Tailscale advertises exactly HA, Frigate, OMV, and monitoring `/32` routes.
- [ ] Approved Tailscale paths work and sampled denied paths fail.
- [ ] Temporary router maintenance egress is removed and normal denial is proved.
- [ ] VM rollback is identified and isolated-restore procedure is recorded.
- [ ] OMV-backed app-data backup mount/timer is completed in Phases 06 and 10 before dependent services become live.
