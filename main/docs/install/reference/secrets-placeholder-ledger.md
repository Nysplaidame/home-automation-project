---
title: Secrets Placeholder Ledger
description: Central placeholder list for the installation manual suite
tags: [install, secrets, placeholders]
created: 2026-05-24
modified: 2026-08-09
type: reference
status: active
---

# Secrets Placeholder Ledger

Store real values in the password manager. Never commit real values.

| Placeholder | Created in | Stored as | Used by |
|---|---|---|---|
| `<ADMIN_SSH_PUBLIC_KEY>` | Admin laptop | SSH public key entry | Proxmox, Debian VMs, OMV |
| `<OPENWRT_IMAGE_PATH>` | Official OpenWrt download | Local verified firmware path, not secret | Router clean install |
| `<OPENWRT_IMAGE_SHA256>` | Official OpenWrt image selector | Published digest, not secret | Router image verification |
| `<ROUTER_SNAPSHOT_TIMESTAMP>` | Router-deploy snapshot creation | Selected known-good snapshot ID, not secret | Physical router recovery |
| `<ROUTER_ROOT_PASSWORD>` | Router first boot | OpenWrt root login | Router setup |
| `<WIFI_MAIN_PASSWORD>` | Router phase 1 | WiFi credentials | Main SSID |
| `<WIFI_IOT_PASSWORD>` | Router phase 1 | WiFi credentials | IoT SSID |
| `<WIFI_GUEST_PASSWORD>` | Router phase 1 | WiFi credentials | Guest SSID |
| `<WIREGUARD_SERVER_PRIVATE_KEY>` | Router phase 1 | WireGuard server | Dormant fallback |
| `<WIREGUARD_CLIENT_PRIVATE_KEY>` | Router phase 6 | WireGuard client | Fallback clients |
| `<TAILSCALE_AUTH_KEY>` | Tailscale admin console | Tailscale docker-host | docker-host route join |
| `<DOCKER_HOST_TAILSCALE_IP>` | `tailscale ip -4` on docker-host | Node address, not secret | AdGuard split DNS and Homepage allowed hosts |
| `<OMV_ADMIN_PASSWORD>` | OMV install | OMV admin | OMV web UI |
| `<OMV_HA_PASSWORD>` | OMV users | OMV service user | HA backups |
| `<OMV_FRIGATE_PASSWORD>` | OMV users | OMV service user | Frigate archive |
| `<OMV_IMMICH_PASSWORD>` | OMV users | OMV service user | Immich storage |
| `<MQTT_PASSWORD>` | HA Mosquitto | MQTT user | HA, Frigate, Bambuddy, VentSys |
| `<HA_ADMIN_PASSWORD>` | HA onboarding | HA admin | Home Assistant UI |
| `<HA_LONG_LIVED_TOKEN>` | HA profile | HA token | Dashboards, Bambuddy |
| `<P1S_SERIAL>` | Printer label/app | Bambu P1S serial | Bambuddy HA package |
| `<FRIGATE_RTSP_PASSWORD>` | Camera setup | Camera RTSP | Frigate |
| `<FRIGATE_MQTT_PASSWORD>` | HA Mosquitto | MQTT user | Frigate |
| `<ADGUARD_ADMIN_PASSWORD>` | AdGuard first run | AdGuard admin | AdGuard UI |
| `<IMMICH_ADMIN_EMAIL>` | Immich first run | Immich admin | Immich UI |
| `<IMMICH_ADMIN_PASSWORD>` | Immich first run | Immich admin | Immich UI |
| `<IMMICH_DB_PASSWORD>` | Immich rebuild | PostgreSQL application password | Immich database |
| `<PAPERLESS_ADMIN_USER>` | Paperless first run | Paperless admin | Paperless UI |
| `<PAPERLESS_ADMIN_PASSWORD>` | Paperless first run | Paperless admin | Paperless UI |
| `<MEALIE_ADMIN_EMAIL>` | Mealie first run | Mealie admin | Mealie UI |
| `<MEALIE_ADMIN_PASSWORD>` | Mealie first run | Mealie admin | Mealie UI |
| `<MEALIE_API_TOKEN>` | Mealie admin UI | Mealie API token | Home Assistant Mealie recipe tools |
| `<GROCY_ADMIN_PASSWORD>` | Grocy first run | Grocy admin | Grocy UI |
| `<OBSIDIAN_LIVESYNC_ADMIN_USER>` | Obsidian LiveSync setup | CouchDB admin user | CouchDB / Self-hosted LiveSync |
| `<OBSIDIAN_LIVESYNC_ADMIN_PASSWORD>` | Obsidian LiveSync setup | CouchDB admin password | CouchDB / Self-hosted LiveSync |
| `<NTFY_ADMIN_PASSWORD>` | ntfy auth setup | ntfy admin | ntfy server |
| `<NTFY_MONITORING_PASSWORD>` | ntfy auth setup | ntfy monitoring write user | Uptime Kuma notifications |
| `<NTFY_WATCHTOWER_PASSWORD>` | ntfy auth setup | ntfy Watchtower write user | Watchtower monitor-only notifications |
| `<NTFY_MOBILE_SUBSCRIBER_PASSWORD>` | ntfy household subscriber setup | Read-only mobile subscriber credential | ntfy phone clients |
| `<WATCHTOWER_NTFY_PASSWORD>` | ntfy auth setup | ntfy Watchtower write user | Watchtower monitor-only notifications |
| `<NODE_RED_ADMIN_PASSWORD>` | Node-RED evaluation gate | Node-RED named administrator | Node-RED editor/admin API |
| `<ACTUAL_PASSWORD>` | Actual first run | Actual password | Actual Budget |
| `<SCRYPTED_ADMIN_PASSWORD>` | Scrypted first run | Scrypted admin | Scrypted UI |
| `<SEARXNG_SECRET_KEY>` | SearXNG config | SearXNG instance secret | SearXNG |
| `<VAULTWARDEN_ADMIN_TOKEN>` | Password manager | Vaultwarden admin token | Vaultwarden gate |
| `<PORTAINER_ADMIN_PASSWORD>` | Portainer first run | Portainer admin | Portainer UI |
| `<WATCHTOWER_HTTP_API_TOKEN>` | Password manager | Watchtower token | Watchtower metrics/API |
| `<NODE_RED_CREDENTIAL_SECRET>` | Password manager | Node-RED secret | Node-RED flows |
| `<7B_OR_8B_Q4_GGUF_MODEL>` | llm-host model selection | Not secret; record selected GGUF model in local AI notes | CT 114 `home-assistant-llm` alias |
| `<DEBIAN_13_LXC_TEMPLATE>` | Proxmox `pveam available` | Selected template filename, not secret | CT 114 clean creation |
| `<LOCAL_AI_CHAT_MODEL_PATH>` | Approved model transfer source | Local source path, not secret | CT 114 chat-model staging |
| `<LOCAL_AI_CHAT_MODEL_SHA256>` | Approved model publisher/project record | Expected digest, not secret | CT 114 chat-model verification |
| `<LOCAL_AI_EMBED_MODEL_PATH>` | Approved model transfer source | Local source path, not secret | CT 114 embedding-model staging |
| `<LOCAL_AI_EMBED_MODEL_SHA256>` | Approved model publisher/project record | Expected digest, not secret | CT 114 embedding-model verification |

If a guide introduces a new placeholder, add it here before using it elsewhere.
