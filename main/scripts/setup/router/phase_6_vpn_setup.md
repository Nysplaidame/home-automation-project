# Phase 6: WireGuard VPN Setup

**Duration**: 2-3 hours  
**Risk Level**: Medium (VPN connectivity complexity)  
**Prerequisites**: Phase 5 completed, all wireless networks operational

## Overview
Implements WireGuard VPN server for secure remote access to network resources. Establishes encrypted tunnel with controlled access to specific network segments while maintaining security isolation. Provides foundation for remote management and controlled access to internal services.

## Sub-Tasks

### 6.1 Pre-Configuration Validation
**Duration**: 10 minutes

```bash
# Create Phase 6 entry backup
/usr/local/bin/backup_phase.sh 6_entry

# Validate VPN prerequisites
echo "=== Phase 6 Prerequisites ===" > /tmp/phase6_validation.txt

# Check WireGuard packages installed
if opkg list-installed | grep -q "wireguard-tools"; then
    echo "✓ WireGuard tools installed" >> /tmp/phase6_validation.txt
else
    echo "✗ WireGuard tools missing" >> /tmp/phase6_validation.txt
    exit 1
fi

# Verify WireGuard keys exist
if [ -f "/etc/wireguard/keys/server_private.key" ]; then
    echo "✓ WireGuard server keys available" >> /tmp/phase6_validation.txt
else
    echo "✗ WireGuard server keys missing" >> /tmp/phase6_validation.txt
    exit 1
fi

cat /tmp/phase6_validation.txt
echo "Prerequisites validated for VPN setup" >> /tmp/deployment_logs/phase6.log
```

### 6.2 WireGuard Interface Configuration
**Duration**: 30 minutes

```bash
# Load server private key
SERVER_PRIVATE_KEY=$(cat /etc/wireguard/keys/server_private.key)

# Configure WireGuard interface (wg0)
# Only create the wg0 WireGuard interface. Do NOT create a separate
# 'vpn' static interface pointing at wg0 — that is invalid OpenWrt UCI and causes
# the vpn_clients firewall zone to silently have no interface attached (B7).
# The firewall zone in firewall-config.conf now references 'wg0' directly.
uci set network.wg0=interface
uci set network.wg0.proto='wireguard'
uci set network.wg0.private_key="$SERVER_PRIVATE_KEY"
uci set network.wg0.listen_port='51820'
uci add_list network.wg0.addresses='10.0.0.1/24'

echo "WireGuard interface configured" >> /tmp/deployment_logs/phase6.log
```

### 6.3 VPN Client Configurations
**Duration**: 25 minutes

```bash
# Add WireGuard peers (clients)
# Client 1 - Mobile Device
CLIENT1_PUBLIC_KEY=$(cat /etc/wireguard/keys/client1_public.key)
uci add network wireguard_wg0
uci set network.@wireguard_wg0[-1].public_key="$CLIENT1_PUBLIC_KEY"
uci add_list network.@wireguard_wg0[-1].allowed_ips='10.0.0.2/32'
uci set network.@wireguard_wg0[-1].persistent_keepalive='25'

# Client 2 - Mobile Device
CLIENT2_PUBLIC_KEY=$(cat /etc/wireguard/keys/client2_public.key)
uci add network wireguard_wg0
uci set network.@wireguard_wg0[-1].public_key="$CLIENT2_PUBLIC_KEY"
uci add_list network.@wireguard_wg0[-1].allowed_ips='10.0.0.3/32'
uci set network.@wireguard_wg0[-1].persistent_keepalive='25'

# Client 3 - Laptop/Desktop
CLIENT3_PUBLIC_KEY=$(cat /etc/wireguard/keys/client3_public.key)
uci add network wireguard_wg0
uci set network.@wireguard_wg0[-1].public_key="$CLIENT3_PUBLIC_KEY"
uci add_list network.@wireguard_wg0[-1].allowed_ips='10.0.0.4/32'
uci set network.@wireguard_wg0[-1].persistent_keepalive='25'

echo "VPN client configurations added" >> /tmp/deployment_logs/phase6.log
```

### 6.4 VPN Configuration Application
**Duration**: 15 minutes

```bash
# Commit network configuration
uci commit network

# Restart network service
/etc/init.d/network restart
sleep 15

# Verify WireGuard interface is up
if ip addr show wg0 >/dev/null 2>&1; then
    echo "✓ WireGuard interface operational" >> /tmp/deployment_logs/phase6.log
else
    echo "✗ WireGuard interface failed" >> /tmp/deployment_logs/phase6.log
fi
```

### 6.5 VPN Client Configuration Files Generation
**Duration**: 20 minutes

```bash
# Generate client configuration files
mkdir -p /etc/wireguard/client_configs
SERVER_PUBLIC_KEY=$(cat /etc/wireguard/keys/server_public.key)
# On OpenWrt the WAN IP is available directly from the network interface; no
# external IP-echo service is needed.
# grep -oP is not available in BusyBox — use awk for portability.
WAN_IP=$(ip -4 addr show "$(uci get network.wan.device 2>/dev/null || echo wan)" \
         | awk '/inet /{split($2,a,"/"); print a[1]; exit}')
if [ -z "$WAN_IP" ]; then
    WAN_IP="YOUR_PUBLIC_IP_HERE"
fi

# Client 1 configuration
cat > /etc/wireguard/client_configs/client1.conf << EOF
[Interface]
PrivateKey = $(cat /etc/wireguard/keys/client1_private.key)
Address = 10.0.0.2/24
DNS = 192.168.1.1

[Peer]
PublicKey = $SERVER_PUBLIC_KEY
Endpoint = $WAN_IP:51820
AllowedIPs = 192.168.1.0/24, 192.168.20.101/32, 192.168.40.50/32, 192.168.70.0/24, 10.0.0.0/24
PersistentKeepalive = 25
EOF

# Client 2 and 3 configurations (similar pattern)
for i in 2 3; do
    cat > /etc/wireguard/client_configs/client$i.conf << EOF
[Interface]
PrivateKey = $(cat /etc/wireguard/keys/client${i}_private.key)
Address = 10.0.0.$((i+1))/24
DNS = 192.168.1.1

[Peer]
PublicKey = $SERVER_PUBLIC_KEY
Endpoint = $WAN_IP:51820
AllowedIPs = 192.168.1.0/24, 192.168.20.101/32, 192.168.40.50/32, 192.168.70.0/24, 10.0.0.0/24
PersistentKeepalive = 25
EOF
done

echo "VPN client configuration files generated" >> /tmp/deployment_logs/phase6.log
```

## Phase 6 Testing and Validation

### 6.6 VPN Interface Validation
**Duration**: 15 minutes

```bash
echo "=== VPN Interface Validation ===" > /tmp/phase6_validation.txt

# Check WireGuard interface status
if ip addr show wg0 | grep -q "10.0.0.1/24"; then
    echo "✓ WireGuard interface has correct IP" >> /tmp/phase6_validation.txt
else
    echo "✗ WireGuard interface IP incorrect" >> /tmp/phase6_validation.txt
fi

# Check if WireGuard is listening on port 51820
if netstat -ulnp | grep -q ":51820"; then
    echo "✓ WireGuard listening on port 51820" >> /tmp/phase6_validation.txt
else
    echo "✗ WireGuard not listening on port 51820" >> /tmp/phase6_validation.txt
fi

# Verify firewall zone exists for VPN
if uci show firewall | grep -q "zone.*name='vpn_clients'"; then
    echo "✓ VPN firewall zone configured" >> /tmp/phase6_validation.txt
else
    echo "✗ VPN firewall zone missing" >> /tmp/phase6_validation.txt
fi

cat /tmp/phase6_validation.txt
```

### 6.7 VPN Security and Access Validation
**Duration**: 20 minutes

```bash
echo "=== VPN Security and Access Validation ===" > /tmp/phase6_security_test.txt

# Verify VPN clients can access LAN (should be allowed)
if uci show firewall | grep -q "VPN to LAN Access"; then
    echo "✓ VPN to LAN access rule configured" >> /tmp/phase6_security_test.txt
else
    echo "✗ VPN to LAN access rule missing" >> /tmp/phase6_security_test.txt
fi

# Verify VPN clients blocked from sensitive networks
sensitive_blocks=("Management" "NVR" "Storage" "IoT" "Printers")
blocked_count=0
for zone in "${sensitive_blocks[@]}"; do
    if uci show firewall | grep -q "Block VPN to $zone"; then
        blocked_count=$((blocked_count + 1))
    fi
done

if [ $blocked_count -eq 5 ]; then
    echo "✓ VPN blocked from sensitive networks ($blocked_count/5)" >> /tmp/phase6_security_test.txt
else
    echo "✗ VPN sensitive network blocking incomplete ($blocked_count/5)" >> /tmp/phase6_security_test.txt
fi

cat /tmp/phase6_security_test.txt
```

## Success Criteria for Phase 6

- **WireGuard interface operational**: VPN server listening on port 51820
- **Client configurations generated**: 3 client config files ready for distribution
- **Firewall integration**: VPN clients properly integrated with firewall zones
- **Access controls**: VPN clients have controlled access (LAN yes, sensitive networks no)
- **Security isolation maintained**: VPN doesn't compromise network segmentation

## Proceed to Phase 7 only when VPN server operational and security controls validated.
