# LLM Host VM Setup Guide

**VM ID:** 104
**Hostname:** llm-host
**IP:** 192.168.20.104
**VLAN:** 20, Automation / trusted app services
**Host:** Proxmox on MINISFORUM M1 Pro-125H
**Purpose:** Local LLM, STT, and TTS inference for Home Assistant and internal AI workflows

VM 104 is the dedicated inference host. Keep legacy local LLM runtime, Open WebUI, and Wyoming
voice services here rather than on VM 103 `docker-host`. Future containerized
query apps can live on VM 103 and be queried from VM 104 only after their own
design and firewall rules are approved.

---

## Current Target Build

| Setting | Value |
|---|---|
| OS | Debian GNU/Linux 13, trixie genericcloud |
| Hostname | llm-host |
| IP | 192.168.20.104/24 |
| Gateway/DNS | 192.168.20.1 |
| Machine | q35 |
| BIOS | OVMF, pre-enrolled keys disabled |
| Disk | local-lvm, 120-180 GiB, SCSI, discard on, SSD emulation |
| CPU/RAM | 4 cores, 8192 MiB |
| Network | vmbr0, VLAN tag 20, VirtIO |
| Boot | onboot enabled, startup after HA, Frigate, monitoring, and docker-host |

Upgrade path after host RAM expands to 64 GB:

- keep the same VM ID, IP, DNS aliases, and ports
- increase VM memory to 20-24 GiB
- keep the legacy local LLM runtime model alias `home-assistant-llm`
- retarget the alias from a 7B/8B Q4 model to a tested 14B Q4/Q5 model

---

## Phase 1 - Create VM 104

Run on: Proxmox host shell.

```bash
cd /var/lib/vz/template/iso
wget -O debian-13-genericcloud-amd64.qcow2 \
  https://cloud.debian.org/images/cloud/trixie/latest/debian-13-genericcloud-amd64.qcow2

qm create 104 \
  --name llm-host \
  --memory 8192 \
  --cores 4 \
  --cpu host \
  --machine q35 \
  --bios ovmf \
  --ostype l26 \
  --net0 virtio,bridge=vmbr0,tag=20 \
  --agent enabled=1 \
  --onboot 1 \
  --startup order=4

qm importdisk 104 debian-13-genericcloud-amd64.qcow2 local-lvm
qm set 104 --scsihw virtio-scsi-single
qm set 104 --scsi0 local-lvm:vm-104-disk-0,discard=on,ssd=1,cache=writeback
qm resize 104 scsi0 160G
qm set 104 --efidisk0 local-lvm:0,efitype=4m,pre-enrolled-keys=0
qm set 104 --boot order=scsi0
qm set 104 --ide2 local-lvm:cloudinit
qm set 104 --ciuser root
qm set 104 --sshkeys /root/proxmox-admin.pub
qm set 104 --ipconfig0 ip=192.168.20.104/24,gw=192.168.20.1
qm set 104 --nameserver 192.168.20.1
qm set 104 --searchdomain home.local
qm start 104
```

Import the Debian cloud disk before creating `efidisk0`. Proxmox increments
the `vm-104-disk-*` volume number as disks are created; creating EFI first can
make the imported Debian disk become `vm-104-disk-1` instead of the expected
`vm-104-disk-0`.

After first boot:

Run on: llm-host over SSH.

```bash
hostnamectl set-hostname llm-host
apt-get update
apt-get install -y qemu-guest-agent ca-certificates curl gnupg ufw
systemctl enable --now qemu-guest-agent
```

---

## Phase 2 - Install Docker Compose

Run on: llm-host over SSH while a temporary maintenance egress rule is active.

```bash
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg \
  | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable --now docker
docker --version
docker compose version
```

Remove the temporary egress rule after package and image pulls are complete.

---

## Phase 3 - Stage The AI Stack

Run on: llm-host over SSH.

```bash
mkdir -p /opt/stacks/local-ai/{legacy-local-llm,open-webui,whisper,piper}
cd /opt/stacks/local-ai
nano docker-compose.yml
```

Use this rebuildable baseline as the first CPU-only stack:

```yaml
services:
  legacy-local-llm:
    image: legacy-local-llm/legacy-local-llm:latest
    container_name: legacy-local-llm
    restart: unless-stopped
    ports:
      - "retired-api-port:retired-api-port"
    volumes:
      - ./legacy-local-llm:/root/.legacy-local-llm

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    restart: unless-stopped
    depends_on:
      - legacy-local-llm
    ports:
      - "3002:8080"
    environment:
      - OLLAMA_BASE_URL=http://legacy-local-llm:retired-api-port
    volumes:
      - ./open-webui:/app/backend/data

  wyoming-whisper:
    image: rhasspy/wyoming-whisper:latest
    container_name: wyoming-whisper
    restart: unless-stopped
    ports:
      - "10300:10300"
    command: ["--model", "base-int8", "--language", "en"]
    volumes:
      - ./whisper:/data

  wyoming-piper:
    image: rhasspy/wyoming-piper:latest
    container_name: wyoming-piper
    restart: unless-stopped
    ports:
      - "10200:10200"
    command: ["--voice", "en_GB-alba-medium"]
    volumes:
      - ./piper:/data
```

Start and inspect:

Run on: llm-host over SSH.

```bash
cd /opt/stacks/local-ai
docker compose config
docker compose up -d
docker compose ps
```

If the selected Piper voice is unavailable, choose a small or medium English
voice from the current `rhasspy/wyoming-piper` documentation and record the
choice in the live notes before treating TTS as validated.

---

## Phase 4 - Create The Stable legacy local LLM runtime Alias

Pick a 7B/8B Q4-class model for the first 32 GB phase. Do not start with a 14B
model on the current host. The initial live deployment used
`llama3.1:8b-instruct-q4_K_M`.

Run on: llm-host over SSH.

```bash
docker exec -it legacy-local-llm legacy-local-llm pull <7B_OR_8B_Q4_MODEL>
cat >/opt/stacks/local-ai/Modelfile.home-assistant-llm <<'EOF'
FROM <7B_OR_8B_Q4_MODEL>

SYSTEM """
You are the local Home Assistant voice and infrastructure assistant.
Be concise, prefer safe actions, and never bypass safety-critical confirmations.
"""

PARAMETER num_ctx 4096
PARAMETER temperature 0.4
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1
EOF

docker exec -i legacy-local-llm sh -c 'cat >/tmp/Modelfile.home-assistant-llm && legacy-local-llm create home-assistant-llm -f /tmp/Modelfile.home-assistant-llm' \
  < /opt/stacks/local-ai/Modelfile.home-assistant-llm
docker exec -it legacy-local-llm legacy-local-llm run home-assistant-llm "Reply with LOCAL_AI_READY."
```

Use the same `home-assistant-llm` name later when retargeting to a 14B model.
Home Assistant should never need to change model names during the RAM upgrade.

---

## Phase 5 - Host Firewall

Run on: llm-host over SSH.

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow from 192.168.10.0/24 to any port 22 proto tcp comment "Management SSH"
ufw allow from 192.168.20.101 to any port retired-api-port proto tcp comment "HA to legacy local LLM runtime"
ufw allow from 192.168.20.101 to any port 10200 proto tcp comment "HA to Wyoming Piper"
ufw allow from 192.168.20.101 to any port 10300 proto tcp comment "HA to Wyoming Whisper"
ufw allow from 192.168.10.0/24 to any port 3002 proto tcp comment "Management to Open WebUI"
ufw allow from 192.168.1.0/24 to any port 3002 proto tcp comment "LAN to Open WebUI"
ufw allow from 192.168.60.10 to any port retired-api-port proto tcp comment "Monitoring to legacy local LLM runtime"
ufw allow from 192.168.60.10 to any port 3002 proto tcp comment "Monitoring to Open WebUI"
ufw allow from 192.168.60.10 to any port 10200 proto tcp comment "Monitoring to Piper"
ufw allow from 192.168.60.10 to any port 10300 proto tcp comment "Monitoring to Whisper"
ufw --force enable
ufw status verbose
```

Docker-published ports are DNATed before normal UFW `INPUT` handling. Add a
`DOCKER-USER` guard so the published AI ports stay scoped.

Run on: llm-host over SSH.

```bash
cat >/usr/local/sbin/llm-host-firewall.sh <<'EOF'
#!/bin/sh
set -e

iptables -N DOCKER-USER 2>/dev/null || true
iptables -F DOCKER-USER
iptables -A DOCKER-USER -m conntrack --ctstate RELATED,ESTABLISHED -j RETURN

# legacy local LLM runtime API: HA, management, LAN testing, and monitoring.
iptables -A DOCKER-USER -p tcp -s 192.168.20.101 -m conntrack --ctorigdst 192.168.20.104 --ctorigdstport retired-api-port -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.10.0/24 -m conntrack --ctorigdst 192.168.20.104 --ctorigdstport retired-api-port -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.1.0/24 -m conntrack --ctorigdst 192.168.20.104 --ctorigdstport retired-api-port -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.60.10 -m conntrack --ctorigdst 192.168.20.104 --ctorigdstport retired-api-port -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.104 --ctorigdstport retired-api-port -j DROP

# Open WebUI: management, LAN, and monitoring.
iptables -A DOCKER-USER -p tcp -s 192.168.10.0/24 -m conntrack --ctorigdst 192.168.20.104 --ctorigdstport 3002 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.1.0/24 -m conntrack --ctorigdst 192.168.20.104 --ctorigdstport 3002 -j RETURN
iptables -A DOCKER-USER -p tcp -s 192.168.60.10 -m conntrack --ctorigdst 192.168.20.104 --ctorigdstport 3002 -j RETURN
iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.104 --ctorigdstport 3002 -j DROP

# Wyoming voice services: HA and monitoring only.
for port in 10200 10300; do
  iptables -A DOCKER-USER -p tcp -s 192.168.20.101 -m conntrack --ctorigdst 192.168.20.104 --ctorigdstport "$port" -j RETURN
  iptables -A DOCKER-USER -p tcp -s 192.168.60.10 -m conntrack --ctorigdst 192.168.20.104 --ctorigdstport "$port" -j RETURN
  iptables -A DOCKER-USER -p tcp -m conntrack --ctorigdst 192.168.20.104 --ctorigdstport "$port" -j DROP
done

iptables -A DOCKER-USER -j RETURN
EOF

chmod 0755 /usr/local/sbin/llm-host-firewall.sh
cat >/etc/systemd/system/llm-host-firewall.service <<'EOF'
[Unit]
Description=llm-host Docker published-port firewall
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
ExecStart=/usr/local/sbin/llm-host-firewall.sh
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now llm-host-firewall.service
iptables -S DOCKER-USER
```

Do not open VM 104 to Guest, DMZ, NVR, Printers, or IoT VLANs.

---

## Phase 6 - Home Assistant Integration

Run on: Home Assistant UI.

1. Add the legacy local LLM runtime integration with URL `http://192.168.20.104:retired-api-port`.
2. Select model `home-assistant-llm` for Assist testing.
3. Add Wyoming integrations:
   - Piper TTS: `192.168.20.104`, port `10200`
   - Whisper STT: `192.168.20.104`, port `10300`
4. Create or update an Assist pipeline using the local STT, local LLM, and local
   TTS services.
5. Expose only approved non-critical entities to the LLM while testing.

---

## Validation

Run on: Admin laptop.

```powershell
Test-NetConnection 192.168.20.104 -Port retired-api-port
Test-NetConnection 192.168.20.104 -Port 3002
Test-NetConnection 192.168.20.104 -Port 10200
Test-NetConnection 192.168.20.104 -Port 10300
```

Run on: llm-host over SSH.

```bash
free -h
docker compose -f /opt/stacks/local-ai/docker-compose.yml ps
curl -s http://127.0.0.1:retired-api-port/api/tags
```

Run the full procedure in `docs/procedures/local_ai_performance_testing.md`
before calling the AI stack live.

---

## Completion Checklist

- [ ] VM 104 exists with 8 GB RAM, 4 cores, and VLAN 20 networking.
- [ ] DNS aliases resolve to `192.168.20.104`.
- [ ] Docker Compose is installed.
- [ ] `/opt/stacks/local-ai/` exists.
- [ ] legacy local LLM runtime, Open WebUI, Wyoming Whisper, and Wyoming Piper are running.
- [ ] `home-assistant-llm` alias exists and points to a 7B/8B Q4-class model.
- [ ] HA legacy local LLM runtime integration connects.
- [ ] HA Wyoming integrations connect.
- [ ] Voice round trip works from HA Assist or Companion App.
- [ ] Performance test passes with no host swap.
- [ ] Monitoring checks are added before relying on the service.
