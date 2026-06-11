---
title: Garage Admin Raspberry Pi Setup Guide
description: Command-by-command setup for a Raspberry Pi used as a trusted garage admin workstation on the HomeAdmin management SSID
tags: [procedure, raspberry-pi, management, wifi, admin]
created: 2026-06-09
modified: 2026-06-09
type: procedure
status: active
---

# Garage Admin Raspberry Pi Setup Guide

This guide sets up a Raspberry Pi in the garage as a trusted admin workstation on
the `HomeAdmin` management SSID. It assumes a fresh Raspberry Pi OS install and
does not assume admin tools are already installed.

Do not commit plaintext WiFi passwords to this repository. The `HomeAdmin`
password is stored in Bitwarden as:

```text
Bitwarden item: wifi-homeadmin
SSID: HomeAdmin
Backup 2.4GHz SSID: HomeAdmin-2G
Network: VLAN 10 / Management / 192.168.10.0/24
```

When a command below asks for `HOMEADMIN_WIFI_PASSWORD`, paste the value from the
Bitwarden item `wifi-homeadmin` into the shell for that session only.

## Target State

| Item | Value |
|---|---|
| Hostname | `garage-admin-pi` |
| Primary SSID | `HomeAdmin` |
| Backup SSID | `HomeAdmin-2G` |
| VLAN | `10` / Management |
| Suggested reserved IP | `192.168.10.20` |
| Router gateway | `192.168.10.1` |
| DNS domain | `home.local` |
| SSH | Enabled, key-based, password login disabled after key test |
| Firewall | UFW enabled, SSH allowed only from management VLAN |

## 1. Prepare The OS

Use Raspberry Pi Imager on a laptop/desktop.

1. Choose a current Raspberry Pi OS Lite 64-bit image.
2. Set the hostname to `garage-admin-pi`.
3. Create an admin user. Suggested username:

```text
garageadmin
```

4. Enable SSH.
5. Add your SSH public key if Raspberry Pi Imager offers that option.
6. Configure WiFi only if you are comfortable entering the `wifi-homeadmin`
   password into the imager. Otherwise skip WiFi here and configure it from the
   Pi console in the next section.
7. Write the image to the SD card, insert it into the Pi, and boot.

If you have a keyboard and monitor connected, log in locally. If you used Imager
to configure WiFi and SSH, try SSH from another management client:

```bash
ssh garageadmin@garage-admin-pi.local
```

If mDNS does not resolve yet, continue from the local console.

## 2. Connect To HomeAdmin WiFi

First set the WiFi country. The project is operated in the UK.

```bash
sudo raspi-config nonint do_wifi_country GB
```

Check whether NetworkManager is present:

```bash
command -v nmcli || echo "nmcli is not installed or not in PATH"
```

On current Raspberry Pi OS, `nmcli` is normally present. Use it when available:

```bash
read -s -p "HomeAdmin WiFi password from Bitwarden item wifi-homeadmin: " HOMEADMIN_WIFI_PASSWORD
echo
sudo nmcli radio wifi on
sudo nmcli dev wifi rescan
sudo nmcli dev wifi list
sudo nmcli dev wifi connect "HomeAdmin" password "$HOMEADMIN_WIFI_PASSWORD"
unset HOMEADMIN_WIFI_PASSWORD
```

If 5GHz coverage is poor in the garage, use the 2.4GHz backup SSID instead:

```bash
read -s -p "HomeAdmin WiFi password from Bitwarden item wifi-homeadmin: " HOMEADMIN_WIFI_PASSWORD
echo
sudo nmcli dev wifi connect "HomeAdmin-2G" password "$HOMEADMIN_WIFI_PASSWORD"
unset HOMEADMIN_WIFI_PASSWORD
```

Verify the Pi landed on the management subnet:

```bash
ip -brief address
ip route
hostname -I
```

Expected result: the WiFi interface, usually `wlan0`, has an address in:

```text
192.168.10.100-149 before reservation
192.168.10.20 after reservation
```

If `nmcli` is not available, use the emergency `wpa_supplicant` path:

```bash
read -s -p "HomeAdmin WiFi password from Bitwarden item wifi-homeadmin: " HOMEADMIN_WIFI_PASSWORD
echo
wpa_passphrase "HomeAdmin" "$HOMEADMIN_WIFI_PASSWORD" | sudo tee /etc/wpa_supplicant/wpa_supplicant.conf
unset HOMEADMIN_WIFI_PASSWORD
sudo chmod 600 /etc/wpa_supplicant/wpa_supplicant.conf
sudo rfkill unblock wifi
sudo systemctl restart wpa_supplicant || true
sudo systemctl restart dhcpcd || true
sleep 10
hostname -I
```

## 3. Set Hostname And Baseline Identity

Run these even if Raspberry Pi Imager already set the hostname.

```bash
sudo hostnamectl set-hostname garage-admin-pi
printf "127.0.1.1\tgarage-admin-pi\n" | sudo tee /tmp/garage-admin-hosts-line
grep -q '^127.0.1.1' /etc/hosts && sudo sed -i 's/^127\.0\.1\.1.*/127.0.1.1\tgarage-admin-pi/' /etc/hosts || cat /tmp/garage-admin-hosts-line | sudo tee -a /etc/hosts
rm /tmp/garage-admin-hosts-line
hostnamectl
```

Reboot once after WiFi and hostname changes:

```bash
sudo reboot
```

After reboot, reconnect:

```bash
ssh garageadmin@garage-admin-pi.local
```

## 4. Record MAC Address For DHCP Reservation

On the Pi:

```bash
ip link show wlan0
cat /sys/class/net/wlan0/address
```

Copy the MAC address. It will look like:

```text
aa:bb:cc:dd:ee:ff
```

## 5. Add Router DHCP Reservation

Use the router UI or SSH. The management DHCP dynamic range is
`192.168.10.100-149`; the `.11-.99` range is reserved for static admin devices.
This guide suggests:

```text
garage-admin-pi.home.local -> 192.168.10.20
```

Before assigning it, check from any management client:

```bash
ping -c 3 192.168.10.20 || true
```

No replies usually means the address is free.

To add the reservation through router SSH, replace `AA:BB:CC:DD:EE:FF` with the
Pi's WiFi MAC:

```bash
ssh root@192.168.10.1
```

Then on the router:

```sh
uci add dhcp host
uci set dhcp.@host[-1].name='garage-admin-pi'
uci set dhcp.@host[-1].dns='1'
uci set dhcp.@host[-1].mac='AA:BB:CC:DD:EE:FF'
uci set dhcp.@host[-1].ip='192.168.10.20'
uci add dhcp domain
uci set dhcp.@domain[-1].name='garage-admin-pi.home.local'
uci set dhcp.@domain[-1].ip='192.168.10.20'
uci commit dhcp
/etc/init.d/dnsmasq restart
exit
```

Reconnect the Pi to pick up the reservation:

```bash
sudo nmcli connection down "HomeAdmin" || true
sudo nmcli connection up "HomeAdmin" || true
hostname -I
```

If that does not refresh the lease, reboot:

```bash
sudo reboot
```

Verify:

```bash
ping -c 3 192.168.10.1
ping -c 3 proxmox.home.local
ping -c 3 garage-admin-pi.home.local
```

## 6. Update The Pi

Start with package indexes and a full upgrade.

```bash
sudo apt-get update
sudo apt-get -y full-upgrade
sudo apt-get -y autoremove
sudo reboot
```

Reconnect after reboot:

```bash
ssh garageadmin@garage-admin-pi.home.local
```

## 7. Install Admin Tooling

Install baseline tools. This command intentionally includes common utilities
that may not be present on a Lite image.

```bash
sudo apt-get update
sudo apt-get install -y \
  avahi-utils \
  ca-certificates \
  curl \
  dnsutils \
  fail2ban \
  git \
  gnupg \
  htop \
  iftop \
  iotop \
  iperf3 \
  iputils-ping \
  jq \
  lsb-release \
  mtr-tiny \
  nano \
  net-tools \
  netcat-openbsd \
  nmap \
  openssh-client \
  openssh-server \
  python3 \
  python3-pip \
  python3-venv \
  ripgrep \
  rsync \
  tcpdump \
  tmux \
  traceroute \
  unattended-upgrades \
  ufw \
  vim \
  wget \
  whois
```

Install MQTT tooling for VentSys checks:

```bash
sudo apt-get install -y mosquitto-clients
```

Confirm key tools:

```bash
for cmd in ssh curl git jq rg nmap tcpdump mosquitto_sub mosquitto_pub dig avahi-resolve ping; do
  command -v "$cmd" >/dev/null && echo "OK: $cmd" || echo "MISSING: $cmd"
done
```

## 8. SSH Key Setup

From your laptop or main admin machine, generate a key if you do not already
have one:

```bash
ssh-keygen -t ed25519 -a 64 -f ~/.ssh/garage_admin_pi_ed25519 -C "garage-admin-pi"
```

Copy the public key to the Pi:

```bash
ssh-copy-id -i ~/.ssh/garage_admin_pi_ed25519.pub garageadmin@garage-admin-pi.home.local
```

If `ssh-copy-id` is not available on the client, display the public key:

```bash
cat ~/.ssh/garage_admin_pi_ed25519.pub
```

Then on the Pi:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

Paste the public key into `authorized_keys`, save, then test key login from the
client:

```bash
ssh -i ~/.ssh/garage_admin_pi_ed25519 garageadmin@garage-admin-pi.home.local
```

Do not disable password login until this key login test succeeds.

## 9. SSH Hardening

Run this only after key login works.

```bash
sudo install -d -m 755 /etc/ssh/sshd_config.d
sudo tee /etc/ssh/sshd_config.d/99-homeadmin-hardening.conf >/dev/null <<'EOF'
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
X11Forwarding no
AllowUsers garageadmin
EOF
sudo sshd -t
sudo systemctl reload ssh
```

Open a second terminal and confirm login still works before closing the current
session:

```bash
ssh -i ~/.ssh/garage_admin_pi_ed25519 garageadmin@garage-admin-pi.home.local
```

If login fails, remove the hardening file from the still-open session:

```bash
sudo rm /etc/ssh/sshd_config.d/99-homeadmin-hardening.conf
sudo systemctl reload ssh
```

## 10. Local Firewall

Allow SSH from the management VLAN only.

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from 192.168.10.0/24 to any port 22 proto tcp comment 'Management SSH'
sudo ufw --force enable
sudo ufw status verbose
```

## 11. Fail2ban

Enable a basic SSH jail.

```bash
sudo tee /etc/fail2ban/jail.d/garage-admin-pi-sshd.local >/dev/null <<'EOF'
[sshd]
enabled = true
backend = systemd
bantime = 1h
findtime = 10m
maxretry = 5
EOF
sudo systemctl enable --now fail2ban
sudo fail2ban-client status
sudo fail2ban-client status sshd
```

## 12. Automatic Security Updates

Enable unattended security updates. This keeps the Pi boring in the best way.

```bash
sudo dpkg-reconfigure -plow unattended-upgrades
```

If the interactive prompt is unavailable, force-enable it:

```bash
sudo apt-get install -y unattended-upgrades
sudo tee /etc/apt/apt.conf.d/20auto-upgrades >/dev/null <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
APT::Periodic::AutocleanInterval "7";
EOF
sudo systemctl enable --now unattended-upgrades
systemctl status unattended-upgrades --no-pager
```

## 13. Optional Tailscale

Install Tailscale only if the Pi should also be reachable through the tailnet.
Do not advertise routes from this Pi unless there is a deliberate reason.

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up --hostname garage-admin-pi --ssh
tailscale status
```

In the Tailscale admin console, approve the device if required. Keep it as a
normal client, not a subnet router.

## 14. Network Validation

Run these from the Pi.

```bash
ip -brief address
ip route
resolvectl status || cat /etc/resolv.conf
```

Management VLAN basics:

```bash
ping -c 3 192.168.10.1
ping -c 3 proxmox.home.local
ping -c 3 192.168.10.10
```

Expected admin targets:

```bash
ping -c 3 homeassistant.home.local
ping -c 3 docker-host.home.local
ping -c 3 monitoring.home.local
```

DNS checks:

```bash
dig router.home.local
dig proxmox.home.local
dig homeassistant.home.local
dig docker-host.home.local
```

Port checks:

```bash
nc -vz 192.168.10.1 22
nc -vz 192.168.10.10 8006
nc -vz 192.168.20.101 8123
nc -vz 192.168.20.102 22
nc -vz 192.168.60.10 3000
nc -vz 192.168.60.10 3001
```

## 15. Useful Admin Commands

Router:

```bash
ssh root@192.168.10.1
```

Proxmox:

```bash
ssh root@192.168.10.10
```

Home Assistant reachability:

```bash
curl -I http://192.168.20.101:8123
```

Docker host:

```bash
ssh root@192.168.20.102
```

MQTT TLS quick check. Use the MQTT credentials and CA from Bitwarden/project
secrets, not committed plaintext:

```bash
mkdir -p ~/admin-secrets
nano ~/admin-secrets/mqtt-ca.crt
chmod 700 ~/admin-secrets
chmod 600 ~/admin-secrets/mqtt-ca.crt
read -p "MQTT username: " MQTT_USER
read -s -p "MQTT password: " MQTT_PASS
echo
mosquitto_sub \
  --cafile ~/admin-secrets/mqtt-ca.crt \
  -h 192.168.20.101 \
  -p 8883 \
  -u "$MQTT_USER" \
  -P "$MQTT_PASS" \
  -t 'ventsys/#' \
  -v \
  -C 5
unset MQTT_USER MQTT_PASS
```

## 16. Maintenance Routine

Monthly:

```bash
sudo apt-get update
apt list --upgradable
sudo apt-get -y full-upgrade
sudo apt-get -y autoremove
sudo reboot
```

Health snapshot:

```bash
hostnamectl
uptime
df -h
free -h
ip -brief address
sudo ufw status verbose
sudo fail2ban-client status sshd
```

## 17. Physical Notes

- Label the Pi with hostname and reserved IP.
- Keep it powered from a reliable supply, not a weak USB port.
- If it is used as an emergency admin path, avoid using it for experiments.
- Do not bridge interfaces or enable routing without writing a separate decision
  and firewall review.

## 18. Completion Checklist

- [ ] Pi boots cleanly.
- [ ] Pi joins `HomeAdmin` or `HomeAdmin-2G`.
- [ ] Pi has management IP `192.168.10.20`.
- [ ] `garage-admin-pi.home.local` resolves.
- [ ] SSH key login works.
- [ ] SSH password login is disabled.
- [ ] UFW is enabled and allows SSH only from `192.168.10.0/24`.
- [ ] Fail2ban is running.
- [ ] Admin tools are installed.
- [ ] Router, Proxmox, HA, docker-host, and monitoring reachability tests pass.
