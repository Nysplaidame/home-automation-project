# Local AI LXC Setup Guide

Compatibility filename retained for existing links. Production local AI runs
in unprivileged **CT 114**, not VM 104.

## Production specification

| Field | Value |
|---|---|
| Hostname | `llm-host` |
| Address | `192.168.20.104/24`, gateway `192.168.20.1`, VLAN 20 |
| Resources | 4 cores, 10240 MiB RAM, 100 GiB root, no swap |
| Features | `nesting=1,keyctl=1` |
| Startup | `onboot=1`, order 4 |
| Stack | `/opt/stacks/local-ai` |

Install Docker Engine, Compose, UFW, Fail2ban and VA/Vulkan tools. Apply shared
GPU mapping from `igpu_passthrough_guide.md`, then deploy
`configs/local-ai/docker-compose.yml`.

Persistent directories:

- `ollama/`
- `open-webui/`
- `whisper/`
- `piper/`
- `openwakeword/`

VLAN 20 has no general internet egress. Whisper therefore stores its tokenizer
under `whisper/huggingface` and starts with `HF_HUB_OFFLINE=1`.

## Required validation

```bash
cd /opt/stacks/local-ai
docker compose config -q
docker compose up -d
docker ps
docker logs ollama 2>&1 | grep -E 'Vulkan|offloaded [0-9]+/[0-9]+ layers'
docker logs wyoming-whisper 2>&1 | grep Ready
curl -fsS http://127.0.0.1:11434/api/tags
curl -fsS http://127.0.0.1:3002/ >/dev/null
```

Host UFW and `DOCKER-USER` policy must both restrict published ports. Include
OpenWakeWord port 10400; the retired VM firewall omitted this protection.

VM 104 is a stopped rollback artifact only. Never start it while CT 114 owns
`192.168.20.104`.
