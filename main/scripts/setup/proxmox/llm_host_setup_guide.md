# Local AI LXC Setup Guide

Compatibility filename retained for existing links. Production local AI runs
in unprivileged **CT 114**, not VM 104.

## Production specification

| Field | Value |
|---|---|
| Hostname | `llm-host` |
| Address | `192.168.20.104/24`, gateway `192.168.20.1`, VLAN 20 |
| Resources | 6 cores, 28672 MiB RAM, 100 GiB root, no swap |
| Features | `nesting=1,keyctl=1` |
| Startup | `onboot=1`, order 4 |
| Stack | `/opt/stacks/local-ai` |

Install Docker Engine, Compose, UFW, Fail2ban and VA/Vulkan tools. Apply shared
GPU mapping from `igpu_passthrough_guide.md`, then deploy
`configs/local-ai/docker-compose.yml`.

October4 read-only `pct config 114` confirms6 cores,28672 MiB RAM and no swap;
older4-core/10–20 GiB descriptions are superseded. No resource allocation changed.

October2 diagnosis, reconfirmed October4: Fail2ban is not installed and Debian security metadata
expired June26. CT114 needs the scoped package-cache input permission, client
proxy and a working temporary cache-host upstream path before installation.
Follow [the prepared repair procedure](../../../docs/procedures/ct114-package-path-repair.md);
source configuration is not proof of a working package path or deployed jail.

Persistent directories:

- `models/`
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
curl -fsS http://127.0.0.1:8081/v1/models
docker logs llama-cpp 2>&1 | grep -E 'Vulkan|model loaded|server is listening'
docker logs wyoming-whisper 2>&1 | grep Ready
curl -fsS http://127.0.0.1:3002/ >/dev/null
```

## llama.cpp migration notes

`llama-cpp` is the preferred unattended inference runtime for CT 114. It serves
the local GGUF model on `8081/tcp` and exposes an OpenAI-compatible local API at
`http://192.168.20.104:8081/v1`. This does not require an OpenAI subscription;
the phrase only describes the HTTP API shape that Open WebUI understands.

Add the llama.cpp connection in Open WebUI as:

- URL: `http://llama-cpp:8080/v1` from inside the Compose network, or
  `http://192.168.20.104:8081/v1` from outside CT 114.
- API key: `sk-no-key-required`.
- Provider: `llama.cpp`, when the UI offers a provider selector.

The production GGUF should be present as:

```bash
/opt/stacks/local-ai/models/home-assistant-llm.gguf
```

Host UFW and `DOCKER-USER` policy must both restrict published ports. Include
OpenWakeWord port 10400; the retired VM firewall omitted this protection.

VM 104 is a stopped rollback artifact only. Never start it while CT 114 owns
`192.168.20.104`.
