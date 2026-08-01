# Mullvad download gateway

Live and acceptance-proven on 2026-08-01. The WireGuard private key/address
remain only in the mode-`0600` live `.env`; they are not present in this
repository.

qBittorrent shares Gluetun's network namespace, publishes only the local Web UI
through Gluetun, and has no mount for final libraries or quarantine. Download
payloads remain on the OMV media export. No peer-listening port is published
because Mullvad does not provide port forwarding.

The live `.env` needs the WireGuard `PrivateKey` and IPv4 `Address` from a
Mullvad-generated WireGuard configuration, not the public device key shown in
the account device list. Keep those values only in the mode-`0600` live file.
The default server filter uses a city rather than one hostname so removal of a
single relay does not strand the gateway.

qBittorrent is configured to use
`/downloads/incomplete` for incomplete payloads and `/downloads/complete` for
completed payloads. Promotion from `complete` to the sibling NAS-backed
`/mnt/omv/media/quarantine` tree is an explicit host-side review step; the
container cannot see that path or any final library.

Acceptance passed by dropping Gluetun's `tun0` interface: qBittorrent public
egress failed closed, its local Web UI remained available, and host egress
continued. Gluetun then recovered automatically and Mullvad recognition passed.
The stronger full-provider-stop proof also passed; after a manual full
stop/start of `download-vpn`, recreate qBittorrent so it attaches to the new
network namespace:

```bash
cd /opt/stacks/download-gateway
docker compose up -d --force-recreate qbittorrent
```

The permanent Web UI credential is stored in Windows Credential Manager as
`home-automation/qbittorrent`. Backup run `20260801T144643Z` passed an isolated
restore check for the credential hash and both download paths.
