# ha-media-proxy

Plain-HTTP playback endpoint so ESPHome voice satellites (Home Assistant Voice PE,
`home-assistant-voice-0ae52a`, IoT VLAN 50 `192.168.50.108`) can fetch TTS replies.

Why (2026-11-11): the PE could not play any reply. Its log showed:

- `couldn't get hostname for :homeassistant.home.local` - ESP-IDF resolves `*.local` only via
  mDNS, never unicast DNS, so the router's `home.local` records are unusable.
- HA (SSL enabled) refuses IP-only `internal_url` values when building device media URLs.
- HA's certificate is from the private Home Local CA, which stock PE firmware does not trust.
- Router rule `Block IoT to Automation` rejects VLAN 50 -> HA `8123`.

Design: HA `internal_url` = `http://ha-media.home.arpa:8124`. nginx on docker-host (host
networking, UFW-scoped) forwards only `/api/tts_proxy/` and `/api/esphome/ffmpeg_proxy/` to HA over
HTTPS; everything else returns 404. Browsers and the companion app keep using HTTPS directly.

Router requirements (OpenWrt):

- DNS: `ha-media.home.arpa` -> `192.168.20.102` (non-`.local` name).
- Firewall: allow `iot_sensors` `192.168.50.108` -> `automation` `192.168.20.102` TCP `8124`.

docker-host UFW: `ufw allow from 192.168.50.108 to any port 8124 proto tcp` (+ management
`192.168.10.0/24` for testing).

Side effect: anything else HA hands out via `internal_url` (outside these two paths) 404s through
this proxy. Revert with HA Settings > System > Network > Home Assistant URL.
