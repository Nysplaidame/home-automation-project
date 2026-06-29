# WireGuard VPN — Client Setup Guide
# Server: GL-MT6000 router, port 51820 UDP
# VPN subnet: 10.0.0.0/24 (server = 10.0.0.1)
# Clients: 10.0.0.2 (mobile 1), 10.0.0.3 (mobile 2), 10.0.0.4 (laptop)
#
# Keys and server config were generated in Phase 1 and deployed in Phase 6
# of the router setup. Tailscale is the daily remote-access layer; WireGuard is
# kept as a dormant fallback. This guide covers client configuration and testing.
# Server setup reference: scripts/setup/router/phase_6_vpn_setup.md

---

## Access granted to VPN clients (per firewall rules)

| Destination | Access |
|---|---|
| LAN (192.168.1.0/24) | ✅ Full |
| HA (192.168.20.101:8123) | ✅ Port 8123 only |
| DMZ (192.168.70.0/24) | ✅ Full |
| Management (192.168.10.0/24) | ❌ Blocked |
| NVR (192.168.30.0/24) | ❌ Blocked |
| Printers (192.168.35.0/24) | ❌ Blocked |
| OMV NAS (192.168.40.50) | ✅ Host only, selected ports |
| Storage VLAN (192.168.40.0/24) | ❌ Broad subnet blocked |
| IoT (192.168.50.0/24) | ❌ Blocked |

---

## Phase 1 — Retrieve client config files from router

The router generated client configs during Phase 6 setup at:
`/etc/wireguard/client_configs/client1.conf`, `client2.conf`, `client3.conf`

Copy them off the router before you reconfigure it:

```bash
# From your management laptop (on VLAN 10 or via console)
scp root@192.168.10.1:/etc/wireguard/client_configs/client1.conf ./wg-client1.conf
scp root@192.168.10.1:/etc/wireguard/client_configs/client2.conf ./wg-client2.conf
scp root@192.168.10.1:/etc/wireguard/client_configs/client3.conf ./wg-client3.conf
```

If the files are missing (e.g. router was reset), regenerate them — see Phase 1.4 below.

---

## Phase 1.4 — Regenerate client configs (if needed)

SSH into the router and run:

```bash
mkdir -p /etc/wireguard/client_configs
SERVER_PUBLIC_KEY=$(cat /etc/wireguard/keys/server_public.key)

# Get your current public IP
# Use local WAN interface lookup; no external IP service dependency.
WAN_IP=$(ip -4 addr show "$(uci get network.wan.device 2>/dev/null || echo wan)" \
         | awk '/inet /{split($2,a,"/"); print a[1]; exit}')
if [ -z "$WAN_IP" ]; then
    WAN_IP="YOUR_PUBLIC_IP_HERE"
fi
echo "WAN IP: $WAN_IP"

for i in 1 2 3; do
    ip=$((i+1))
    cat > /etc/wireguard/client_configs/client${i}.conf << EOF
[Interface]
PrivateKey = $(cat /etc/wireguard/keys/client${i}_private.key)
Address = 10.0.0.${ip}/24
# VPN AllowedIPs includes 192.168.20.101/32 for HA itself, not the full VLAN 20
# subnet. Use the main LAN gateway for DNS because it is covered by
# 192.168.1.0/24 and answers home.local queries via dnsmasq on the router.
DNS = 192.168.1.1

[Peer]
PublicKey = $SERVER_PUBLIC_KEY
Endpoint = ${WAN_IP}:51820
AllowedIPs = 192.168.1.0/24, 192.168.20.101/32, 192.168.40.50/32, 192.168.70.0/24, 10.0.0.0/24
# Include the DMZ subnet so VPN-to-DMZ firewall rules can match routed traffic.
PersistentKeepalive = 25
EOF
    echo "Generated client${i}.conf (IP: 10.0.0.${ip})"
done
```

> `AllowedIPs` controls what traffic routes through the tunnel:
> - `192.168.1.0/24` — main LAN access
> - `192.168.20.101/32` — HA only (not the whole VLAN)
> - `192.168.40.50/32` — OMV host only (not the whole storage VLAN)
> - `192.168.70.0/24` — DMZ access
> - `10.0.0.0/24` — VPN subnet itself
>
> This is a split-tunnel config. Traffic to other sites goes via your phone's normal internet.
> To route ALL traffic through the VPN (full tunnel), change AllowedIPs to `0.0.0.0/0, ::/0`.

---

## Phase 2 — Install WireGuard on clients

### Mobile (iOS / Android)

1. Install the WireGuard app from App Store / Play Store
2. Tap `+` → `Create from QR code` or `Create from file`
3. Generate a QR code from the config file (on your laptop):
   ```bash
   # Install qrencode if needed: apt-get install qrencode / brew install qrencode
   qrencode -t ansiutf8 < wg-client1.conf
   ```
4. Scan the QR code with the WireGuard app
5. Name the tunnel (e.g. `Home VPN`)

### Windows laptop

```powershell
# Install WireGuard from https://www.wireguard.com/install/
# Then in WireGuard app: Add Tunnel → Import from file → select wg-client3.conf
```

### Linux laptop

```bash
sudo apt-get install wireguard
sudo cp wg-client3.conf /etc/wireguard/wg0.conf
sudo chmod 600 /etc/wireguard/wg0.conf
sudo wg-quick up wg0

# Enable at boot
sudo systemctl enable wg-quick@wg0
```

### macOS

```bash
brew install wireguard-tools
sudo cp wg-client3.conf /usr/local/etc/wireguard/wg0.conf
sudo wg-quick up wg0
```

---

## Phase 3 — Test the VPN connection

After connecting:

```bash
# Check you got a VPN IP
ip addr show wg0     # should show 10.0.0.x
# Or on mobile, the VPN status shows the tunnel IP

# Test access to Home Assistant
curl http://192.168.20.101:8123
# Should return HA login page HTML

# Test host-only fallback access to OMV
curl -I http://192.168.40.50/

# Test access to main LAN
ping 192.168.1.1

# Verify blocked access (should fail — this is correct)
ping 192.168.10.10   # management — should timeout
ping 192.168.30.20   # Frigate — should timeout
ping 192.168.50.1    # IoT — should timeout
```

---

## Phase 4 — Dynamic IP handling (if your WAN IP changes)

Home ISPs often change your public IP. If the VPN stops connecting after some time, the endpoint IP in the client config has changed.

**Option A — update client configs manually**
When the IP changes, get the new one from your router (`Status → Overview → WAN IP`) and update the `Endpoint` line in each client's config.

**Option B — use a dynamic DNS (DDNS) service**
The GL-MT6000 supports DDNS:
`Advanced Settings → DDNS`

Register a free hostname at ddns.net, no-ip.com, or DuckDNS.
Once configured, replace the IP in client configs with your DDNS hostname:
```
Endpoint = yourhome.duckdns.org:51820
```

This keeps working even when your ISP changes your IP.

---

## Phase 5 — Add or revoke clients

### Add a new client

On the router:

```bash
# Generate new key pair
wg genkey | tee /etc/wireguard/keys/client4_private.key | wg pubkey > /etc/wireguard/keys/client4_public.key

# Add peer to running WireGuard interface
wg set wg0 peer $(cat /etc/wireguard/keys/client4_public.key) \
    allowed-ips 10.0.0.5/32 \
    persistent-keepalive 25

# Persist to UCI
uci add network wireguard_wg0
uci set network.@wireguard_wg0[-1].public_key="$(cat /etc/wireguard/keys/client4_public.key)"
uci add_list network.@wireguard_wg0[-1].allowed_ips='10.0.0.5/32'
uci set network.@wireguard_wg0[-1].persistent_keepalive='25'
uci commit network

# Generate client config
SERVER_PUBLIC_KEY=$(cat /etc/wireguard/keys/server_public.key)
# Use local WAN interface lookup; no external IP service dependency.
WAN_IP=$(ip -4 addr show "$(uci get network.wan.device 2>/dev/null || echo wan)" \
         | awk '/inet /{split($2,a,"/"); print a[1]; exit}')
if [ -z "$WAN_IP" ]; then
    WAN_IP="YOUR_PUBLIC_IP_HERE"
fi
cat > /etc/wireguard/client_configs/client4.conf << EOF
[Interface]
PrivateKey = $(cat /etc/wireguard/keys/client4_private.key)
Address = 10.0.0.5/24
# VPN AllowedIPs includes 192.168.20.101/32 for HA itself, not the full VLAN 20
# subnet. Use the main LAN gateway for DNS because it is covered by
# 192.168.1.0/24 and answers home.local queries via dnsmasq on the router.
DNS = 192.168.1.1

[Peer]
PublicKey = $SERVER_PUBLIC_KEY
Endpoint = ${WAN_IP}:51820
AllowedIPs = 192.168.1.0/24, 192.168.20.101/32, 192.168.40.50/32, 192.168.70.0/24, 10.0.0.0/24
# Include the DMZ subnet so VPN-to-DMZ firewall rules can match routed traffic.
PersistentKeepalive = 25
EOF
```

### Revoke a client

```bash
# Find the peer (by public key)
wg show wg0 peers

# Remove peer from running config
wg set wg0 peer <CLIENT_PUBLIC_KEY> remove

# Remove from UCI
uci show network | grep wireguard_wg0   # find the section
uci delete network.@wireguard_wg0[N]   # N = the index with that public key
uci commit network
/etc/init.d/network restart
```

---

## Quick reference

| Item | Value |
|---|---|
| Server endpoint | `<your-WAN-IP>:51820` or DDNS hostname |
| Protocol | UDP |
| VPN subnet | 10.0.0.0/24 |
| Server IP (in tunnel) | 10.0.0.1 |
| Client IPs | 10.0.0.2 / .3 / .4 |
| Access via VPN | HA (192.168.20.101:8123), OMV host (192.168.40.50 selected ports), LAN (192.168.1.0/24), DMZ (192.168.70.0/24) |
| Blocked via VPN | Management, NVR, Printers, broad Storage VLAN, IoT |
| Keys location (router) | `/etc/wireguard/keys/` |
| Client configs (router) | `/etc/wireguard/client_configs/` |
| Firewall zone | `vpn_clients` — see firewall-config.conf |
