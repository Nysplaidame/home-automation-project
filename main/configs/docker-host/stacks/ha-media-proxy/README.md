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

docker-host UFW allows 8124 from `192.168.50.108` (PE), `192.168.20.101` (HA itself: its
`ffmpeg_proxy` re-fetches the source TTS via `internal_url`; without this the PE gets a 5-byte
stream and stays silent) and `192.168.10.0/24` (management testing).

Applied live 2026-11-11 (router backups `/etc/config/{firewall,dhcp}.bak-20261111-ha-media`);
verified: announcement streamed 143 KB FLAC and played.

Side effect: anything else HA hands out via `internal_url` (outside these two paths) 404s through
this proxy.

**Where the setting lives (found 2026-11-13):** `homeassistant: internal_url` in the live
`/config/configuration.yaml` must be `http://ha-media.home.arpa:8124`. It was first set only in the UI
(Settings > System > Network), but a value in YAML overrides the UI value at every HA start, and the YAML
still said `https://192.168.20.101:8123`. After the next restart HA could not build a media URL again and the
Voice PE heard its wake word, played the tone, then did nothing: the pipeline run died at its first event with
`Unable to determine Home Assistant URL to send to device` (`assist_satellite` ->
`async_process_play_media_url`, visible under Settings > System > Logs and in the pipeline debug view). The YAML is
fixed (backup `backups/configuration.yaml.bak-20261113-pre-internal-url`). To revert, change the YAML line, not the
UI. Quick check of the effective value: `GET /api/config` -> `internal_url`.
