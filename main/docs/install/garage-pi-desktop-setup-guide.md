---
title: Garage Raspberry Pi Desktop Setup Guide
description: Lean Raspberry Pi 5 desktop, NVMe boot, OLED case display, project access, and optional AI/camera readiness
tags: [install, raspberry-pi, garage, desktop, ventsys, ai, oled]
created: 2026-06-10
modified: 2026-08-25
type: install-guide
status: draft
---

# Garage Raspberry Pi Desktop Setup Guide

This guide builds the garage Raspberry Pi as a lean local desktop and project
workstation. It is intended for the Raspberry Pi 5 in the garage case with NVMe
storage, keyboard, mouse, monitor, and the small OLED status screen in the case.

The Pi is an operator station, flashing station, dashboard viewer, and
experimental edge-AI node. It is not the primary service host for the project.
Home Assistant, Frigate, docker-host, monitoring, and future NAS workloads remain
on their existing project hosts unless a later decision deliberately moves them.

## Purpose

The garage Pi should:

- run Raspberry Pi OS 64-bit with Desktop from NVMe storage
- use Firefox as the main browser
- join the management network through `homeadmin` Wi-Fi or management Ethernet
- have a static DHCP reservation on VLAN 10
- expose SSH as a fallback administration path
- access Home Assistant, VentSys, Proxmox, router, NAS, Grafana, Uptime Kuma,
  AdGuard, docker-host services, and ESPHome
- flash ESPHome / VentSys boards over USB
- run the case OLED system-status display as a `systemd` service
- support a Pi Camera for experimental local motion/person/face work
- leave heavier AI, recording, and alarm decisions offloaded until validated

## Runs on

- Device: garage Raspberry Pi 5
- RAM: 4 GB
- Storage: NVMe SSD through the case M.2 adapter
- Case: GeeekPi N07 Mini Tower NVMe NAS Kit class case with heatsink, fan, OLED,
  and bottom-mounted M.2 adapter
- OS: Raspberry Pi OS 64-bit with Desktop
- Network: management VLAN 10 through `homeadmin` Wi-Fi or management Ethernet
- Operator context: local GUI desktop and local terminal
- SSH: enabled, but used as a fallback rather than the normal setup route

## Hardware Decisions

Use a 1 TB NVMe SSD if the price difference is tolerable. A 512 GB SSD is
acceptable, but 1 TB leaves room for Python virtual environments, package caches,
ESPHome / PlatformIO build artifacts, browser cache, camera clips, small local
AI experiments, and future experiments without constant cleanup.

Do not design this build around a PCIe AI HAT while the NVMe adapter is installed.
The Pi 5 PCIe path is already being used for storage. If local acceleration is
needed later, prefer one of these paths:

- Raspberry Pi AI Camera, because the accelerator is in the camera module
- USB accelerator, if software support is confirmed
- offload camera inference to Frigate or heavier LLM/voice inference to CT 114
  `llm-host`

## Prerequisites

- Raspberry Pi 5, 4 GB RAM
- GeeekPi N07 / 52Pi-style mini tower case assembled with fan, heatsink, OLED,
  and M.2 adapter
- 512 GB or 1 TB NVMe SSD
- monitor, keyboard, and mouse
- Raspberry Pi Imager on another computer
- `homeadmin` SSID and password
- ability to add a static DHCP reservation on the router
- optional Pi Camera for later AI experiments
- optional USB microphone and wired/HDMI speaker for later voice experiments

## Inputs

| Placeholder | Meaning |
|---|---|
| `GARAGE_PI_USER` | The Linux user created in Raspberry Pi Imager |
| `GARAGE_PI_HOSTNAME` | Suggested hostname: `garage-pi` |
| `GARAGE_PI_WIFI_SSID` | Suggested SSID: `homeadmin` |
| `GARAGE_PI_WIFI_PASSWORD` | Password for the management Wi-Fi |
| `GARAGE_PI_MAC` | Wi-Fi or Ethernet MAC address used for DHCP reservation |
| `GARAGE_PI_IP` | Static DHCP address assigned on management VLAN 10 |
| `HA_URL` | Current Home Assistant URL, normally `https://192.168.20.101:8123` |
| `NAS_HOST` | Future NAS address, currently planned as `192.168.40.50` |

Keep passwords and tokens in the password manager, not in this repository.

## Phase 1 - Flash Raspberry Pi OS To NVMe

Use Raspberry Pi Imager from another computer.

Select:

- Device: Raspberry Pi 5
- OS: Raspberry Pi OS 64-bit with Desktop
- Storage: the NVMe SSD attached through the USB/NVMe writer or case adapter

In the Imager settings, set:

- hostname: `garage-pi`
- username and password
- Wi-Fi SSID: `homeadmin`
- Wi-Fi country: `GB`
- locale/timezone: `Europe/London`
- SSH: enabled

Expected result:

- the Pi boots into the Raspberry Pi OS desktop from NVMe
- the first login is manual
- Wi-Fi attempts to join `homeadmin`
- SSH is available after the network is up

## Phase 2 - First Boot Checks

Run on: garage Pi local terminal.

```bash
whoami
echo "$HOME"
hostnamectl
```

Explanation:

- `whoami` prints the active Linux username. Use this value anywhere the older
  OLED guide says `YOUR_USERNAME`.
- `echo "$HOME"` prints the current user's home directory.
- `hostnamectl` shows the hostname and OS identity.

Expected result:

- username matches the account created in Imager
- hostname is `garage-pi`
- OS is Raspberry Pi OS 64-bit

Run on: garage Pi local terminal.

```bash
findmnt /
lsblk -o NAME,MODEL,SIZE,TYPE,FSTYPE,MOUNTPOINTS
```

Explanation:

- `findmnt /` shows which device backs the root filesystem.
- `lsblk` lists disks, partitions, filesystem types, and mount points.

Expected result:

- root filesystem is on the NVMe drive, not a microSD card
- the NVMe capacity matches the installed SSD

If the Pi does not boot from NVMe, remove any inserted microSD card and retry.
If that still fails, use `raspi-config` to check boot order.

Run on: garage Pi local terminal.

```bash
sudo raspi-config
```

Explanation:

- `sudo` runs a command with administrator privileges.
- `raspi-config` opens Raspberry Pi's configuration tool.

Use:

```text
Advanced Options -> Boot Order -> NVMe/USB Boot
```

Reboot when prompted.

## Phase 3 - Update And Confirm Core Hardware

Run on: garage Pi local terminal.

```bash
sudo apt update
sudo apt full-upgrade -y
sudo reboot
```

Explanation:

- `apt update` refreshes package indexes.
- `apt full-upgrade -y` installs available upgrades and allows package
  dependency changes required by the OS.
- `reboot` restarts the Pi so kernel, firmware, and desktop updates are active.

Run on: garage Pi local terminal after reboot.

```bash
vcgencmd measure_temp
vcgencmd get_throttled
```

Explanation:

- `vcgencmd measure_temp` reports the current SoC temperature.
- `vcgencmd get_throttled` reports undervoltage and thermal throttling flags.

Expected result:

- temperature is reasonable for an idle desktop
- `get_throttled` returns `0x0` during normal idle operation

If throttling appears, check the case fan, heatsink contact, power supply, and
USB/NVMe cabling before adding heavier workloads.

## Phase 4 - Network And Static DHCP

Use the GUI network menu first. Connect to `homeadmin` and confirm internet
access. If Ethernet is later connected through the managed switch, prefer the
management VLAN port/profile.

Run on: garage Pi local terminal.

```bash
nmcli device status
ip -br addr
ip route
resolvectl dns
```

Explanation:

- `nmcli device status` shows NetworkManager device state.
- `ip -br addr` shows compact interface and IP information.
- `ip route` shows the default gateway and routing table.
- `resolvectl dns` shows DNS servers in use.

Expected result:

- Wi-Fi or Ethernet is connected
- the Pi has a management-network address
- default gateway points at the router
- DNS points at the project DNS path

Run on: garage Pi local terminal.

```bash
ip link show wlan0
ip link show eth0
```

Explanation:

- `ip link show <interface>` displays the hardware/MAC address for an interface.

Record the MAC address for the interface you want the router to reserve. Add a
static DHCP reservation on the router for `garage-pi` on VLAN 10.

Suggested reservation:

```text
hostname: garage-pi
network: management / VLAN 10
address: choose an unused 192.168.10.x address
```

After adding the reservation, reconnect Wi-Fi or reboot.

Run on: garage Pi local terminal.

```bash
ping -c 3 192.168.10.1
curl -k -I https://192.168.20.101:8123
curl -I http://192.168.60.10:3000
curl -I http://192.168.60.10:3001
```

Explanation:

- `ping -c 3` sends three ICMP probes to confirm basic reachability.
- `curl -I` fetches only HTTP response headers, which is enough to prove a web
  service is reachable without downloading the full page.

Expected result:

- router responds
- Home Assistant responds
- Grafana responds
- Uptime Kuma responds

If management Wi-Fi cannot connect, troubleshoot in this order:

1. confirm Wi-Fi country is `GB`
2. confirm password
3. confirm SSID is visible
4. confirm router allows the Pi MAC
5. test temporary Ethernet
6. inspect NetworkManager with `nmcli device status`

## Phase 5 - Lean Desktop Package Set

Raspberry Pi OS Desktop is the base. Keep the desktop lean and add tools that
serve the project directly.

Run on: garage Pi local terminal.

```bash
sudo apt install -y \
  firefox-esr \
  git \
  curl \
  wget \
  jq \
  tree \
  htop \
  btop \
  rsync \
  zip \
  unzip \
  nano \
  vim \
  ca-certificates \
  gnupg \
  lsb-release \
  dnsutils \
  traceroute \
  nmap \
  iperf3 \
  tcpdump \
  mosquitto-clients \
  cifs-utils \
  smbclient \
  nfs-common \
  python3 \
  python3-venv \
  python3-pip \
  pipx \
  python3-dev \
  i2c-tools \
  smartmontools \
  nvme-cli
```

Explanation:

- `apt install -y` installs named packages and answers yes to prompts.
- `firefox-esr` provides the preferred browser.
- `git`, `curl`, `wget`, `jq`, `tree`, `rsync`, `zip`, and `unzip` are general
  project and file-transfer tools.
- `htop` and `btop` show interactive resource usage.
- `nano` and `vim` provide terminal editing options.
- `ca-certificates`, `gnupg`, and `lsb-release` support secure package sources.
- `dnsutils`, `traceroute`, `nmap`, `iperf3`, and `tcpdump` support network
  diagnostics.
- `mosquitto-clients` provides MQTT test commands.
- `cifs-utils`, `smbclient`, and `nfs-common` support NAS access.
- Python packages support virtual environments and local tooling.
- `i2c-tools` supports the OLED display and I2C checks.
- `smartmontools` and `nvme-cli` support SSD health checks.

Expected result:

- package installation completes without errors
- Firefox launches from the menu
- terminal tools are available

Optional heavier packages should wait until the base machine is stable:

- VSCodium or VS Code
- Wireshark
- Docker
- MQTT Explorer
- Raspberry Pi Connect or VNC
- Tailscale
- Node.js
- OpenCV / AI frameworks

## Phase 6 - Remove Unwanted Desktop Extras Carefully

Do not strip the desktop until network, display, browser, and OLED setup are
working. Remove only apps you know you do not want.

Run on: garage Pi local terminal.

```bash
apt list --installed | less
```

Explanation:

- `apt list --installed` lists installed packages.
- `less` lets you scroll through long output without dumping it all to the
  terminal.

Use the GUI package tool or `apt remove` only for clearly unwanted applications.
Avoid removing network, display, Bluetooth, audio, printing, camera, Python, or
desktop session packages during the first build.

## Phase 7 - Enable SSH Fallback

SSH should be enabled, but local GUI and local terminal remain the normal setup
path.

Run on: garage Pi local terminal.

```bash
sudo systemctl enable --now ssh
systemctl status ssh --no-pager -l
```

Explanation:

- `systemctl enable --now ssh` starts SSH now and enables it at boot.
- `systemctl status` shows whether the service is running.
- `--no-pager -l` prints full status output directly in the terminal.

Expected result:

- SSH service is active
- management devices can connect when needed

Prefer SSH keys over passwords once the Pi is stable.

## Phase 8 - Case OLED Setup

The case OLED setup is required for this build. The canonical detailed procedure
is [oled-screen-setup-guide.md](oled-screen-setup-guide.md).

Use that guide for the full `sys_info.py` script body. This section records how
it fits into the garage Pi build.

Run on: garage Pi local terminal.

```bash
sudo raspi-config
```

Use:

```text
Interface Options -> I2C -> Enable
```

Run on: garage Pi local terminal.

```bash
sudo usermod -aG gpio,i2c "$USER"
sudo reboot
```

Explanation:

- `usermod -aG gpio,i2c "$USER"` adds the current user to the GPIO and I2C
  device groups without removing existing group memberships.

After reboot, continue with the OLED guide:

1. create `~/oled`
2. create `~/oled/venv`
3. clone `luma.examples`
4. install the example package inside the virtual environment
5. install `psutil`
6. test `sys_info.py` manually
7. replace `sys_info.py` with the project version
8. create `~/start_oled.sh`
9. create `/etc/systemd/system/minitower_oled.service`
10. enable and restart the service

Run on: garage Pi local terminal after following the OLED guide.

```bash
systemctl status minitower_oled.service --no-pager -l
sudo journalctl -b -u minitower_oled.service -n 100 --no-pager
```

Explanation:

- `journalctl -b -u <service>` shows logs for a service from the current boot.
- `-n 100` limits output to the last 100 lines.

Expected result:

- OLED shows CPU, temperature, uptime, RAM, disk, network traffic, and IP
- `minitower_oled.service` is active

If the OLED is blank, follow the troubleshooting section in
[oled-screen-setup-guide.md](oled-screen-setup-guide.md) before continuing.

## Phase 9 - Browser And Project Shortcuts

Create Firefox bookmarks or desktop launchers for the internal tools.

Recommended bookmarks:

| Service | URL |
|---|---|
| Home Assistant | `https://192.168.20.101:8123` |
| VentSys dashboard | `https://192.168.20.101:8123/local/ventsys-dashboard.html` |
| Home Assistant monitoring page | `https://192.168.20.101:8123/monitoring/overview` |
| Proxmox | `https://192.168.10.10:8006` |
| Grafana | `http://192.168.60.10:3000` |
| Uptime Kuma | `http://192.168.60.10:3001` |
| docker-host Homepage | `http://192.168.20.102:3001` |
| Bambuddy | `http://192.168.20.102:8000` |
| AdGuard Home | `http://192.168.20.102:8080` |

Direct Grafana and Kuma access are the reliable paths for now. Embedded Grafana
or Kuma views in Home Assistant remain parked until HTTPS / same-origin reverse
proxy decisions are made.

## Phase 10 - Project Repository Access

Use the Pi as a reader/operator station first. Only make code edits here if that
is comfortable on the small machine.

Run on: garage Pi local terminal.

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/Nysplaidame/home-automation-project.git
```

Explanation:

- `mkdir -p` creates the target directory and does nothing if it already exists.
- `cd` changes the current working directory.
- `git clone` downloads a working copy of the repository.

Expected result:

- project repository exists at `~/projects/home-automation-project`

After cloning, read:

- `README.md`
- `main/README.md`
- `main/PROJECT-INDEX.md`
- `main/TO-DO.md`
- relevant `main/HANDOFF-*.md` files when resuming live work

## Phase 11 - NAS Access Readiness

The NAS is still planned in the project baseline. Prepare client tooling now,
but only create persistent mounts after the NAS is live.

Run on: garage Pi local terminal after NAS is live.

```bash
smbclient -L //NAS_HOST -U YOUR_NAS_USER
showmount -e NAS_HOST
```

Explanation:

- `smbclient -L` lists SMB shares visible on the NAS.
- `showmount -e` lists NFS exports from the NAS.

Expected result:

- SMB or NFS exports are visible after the NAS is deployed

Do not add `/etc/fstab` entries until the final NAS address, share names, and
credentials are known.

## Phase 12 - ESPHome And VentSys Flashing Station

The garage Pi should be able to identify and flash ESP32 boards over USB.

Run on: garage Pi local terminal.

```bash
sudo usermod -aG dialout "$USER"
sudo reboot
```

Explanation:

- `dialout` grants access to USB serial devices such as ESP32 boards.

Run on: garage Pi local terminal after reboot and plugging in a board.

```bash
lsusb
ls -l /dev/serial/by-id/
dmesg | tail -n 50
```

Explanation:

- `lsusb` lists USB devices.
- `/dev/serial/by-id/` contains stable names for serial adapters when available.
- `dmesg | tail -n 50` shows the latest kernel messages, useful when a USB
  device was just plugged in.

Expected result:

- USB serial adapter appears
- board can be selected from ESPHome or local flashing tools

Prefer the Home Assistant ESPHome add-on for normal firmware management. Use
local tooling only when USB recovery or offline build/testing is needed.

Optional local ESPHome environment:

Run on: garage Pi local terminal.

```bash
mkdir -p ~/venvs
python3 -m venv ~/venvs/esphome
source ~/venvs/esphome/bin/activate
pip install --upgrade pip
pip install esphome
esphome version
```

Explanation:

- `python3 -m venv` creates an isolated Python environment.
- `source <venv>/bin/activate` activates that environment for the current shell.
- `pip install --upgrade pip` updates Python's package installer inside the
  virtual environment.
- `pip install esphome` installs ESPHome locally without changing system Python.
- `esphome version` confirms the command works.

Keep local ESPHome builds optional. They can consume storage and time, and the HA
add-on remains the normal project path.

## Phase 13 - MQTT And Home Assistant Diagnostics

Use MQTT diagnostics from the Pi when checking VentSys or Bambuddy topics.

Run on: garage Pi local terminal.

```bash
mosquitto_sub -h 192.168.20.101 -p 8883 \
  --cafile /path/to/ca.crt \
  -u mqtt \
  -P 'MQTT_PASSWORD' \
  -t 'ventsys/#' -v
```

Explanation:

- `mosquitto_sub` subscribes to MQTT topics.
- `-h` sets the broker host.
- `-p` sets the broker port.
- `--cafile` points at the MQTT TLS certificate authority file.
- `-u` and `-P` provide MQTT credentials.
- `-t 'ventsys/#'` subscribes to all topics under `ventsys/`.
- `-v` prints topic names as well as payloads.

Do not store MQTT passwords in shell history or committed files. Use the password
manager and paste only when needed.

Expected result:

- messages appear when VentSys devices publish
- TLS verification succeeds

## Phase 14 - Pi Camera Baseline

Camera and AI work is experimental at first. Do not connect detection results to
alarm behavior until the system has been observed for false positives and false
negatives.

Run on: garage Pi local terminal.

```bash
sudo raspi-config
```

Use any camera interface option required by the installed Raspberry Pi OS image.
Modern Raspberry Pi OS images usually use the libcamera stack by default.

Run on: garage Pi local terminal.

```bash
libcamera-hello --list-cameras
libcamera-still -o ~/camera-test.jpg
```

Explanation:

- `libcamera-hello --list-cameras` lists detected cameras.
- `libcamera-still` captures a still image.

Expected result:

- Pi Camera is detected
- `~/camera-test.jpg` is created

AI camera paths to evaluate later:

- standard Pi Camera with CPU-only experiments
- Raspberry Pi AI Camera for local camera-side inference
- USB accelerator if supported
- RTSP feed into Frigate if the camera path becomes security-relevant

## Phase 15 - Optional AI Experiment Layer

Keep AI optional and reversible. The 4 GB Pi can do useful light work, but it
should not become the dependable alarm brain without a separate validation phase.

Good local candidates:

- motion detection
- simple person/object detection at modest resolution
- known/unknown face experiments
- wake-word detection
- lightweight event scripts that publish MQTT or call Home Assistant webhooks

Better offloaded:

- reliable intruder/alarm decisions
- long-term video recording
- multi-stage face recognition
- full voice assistant pipelines
- local LLMs

Before installing AI frameworks, create a dedicated environment:

Run on: garage Pi local terminal.

```bash
mkdir -p ~/ai
python3 -m venv ~/ai/venv
source ~/ai/venv/bin/activate
pip install --upgrade pip
```

Explanation:

- this keeps experimental AI packages away from the system Python and away from
  the OLED virtual environment

Do not install OpenCV, TensorFlow Lite, PyTorch, face-recognition libraries, or
voice stacks until the exact experiment is chosen. Those dependencies are large
and can make a lean desktop feel untidy quickly.

Suggested decision gates:

1. camera stable for several days
2. motion/person detection works locally without throttling
3. known/unknown face detection tested against normal garage lighting
4. results published as advisory Home Assistant entities only
5. alarm integration considered only after an observation period

## Phase 16 - Optional Voice Assistant Layer

Voice is also experimental. Use reliable audio hardware before installing the
software stack.

Suggested hardware:

- USB microphone or small USB mic array
- wired, HDMI, or USB speaker
- avoid Bluetooth as the primary garage voice path unless reliability is proven

Preferred architecture:

- Pi handles microphone/speaker and possibly wake word
- Home Assistant Assist handles conversation/intent
- heavier speech-to-text or text-to-speech can be offloaded if latency is poor

Do not install a full voice stack in the base build. Add it as a separate module
after the desktop, OLED, network, and camera are stable.

## Phase 17 - Maintenance

Run on: garage Pi local terminal.

```bash
df -h
free -h
vcgencmd measure_temp
vcgencmd get_throttled
sudo nvme smart-log /dev/nvme0
```

Explanation:

- `df -h` shows filesystem capacity.
- `free -h` shows RAM and swap use.
- `nvme smart-log` shows NVMe health data.

Expected result:

- plenty of free disk space
- idle memory pressure is reasonable
- no throttling flags
- NVMe health is normal

Update policy:

- apply OS updates during an intentional maintenance window
- reboot after kernel or firmware updates
- test Home Assistant, dashboard access, OLED service, and network reachability
  after updates
- avoid automatic container updates on the Pi unless a later decision approves
  local Docker workloads

## Failure Recovery

Wi-Fi fails:

- verify Wi-Fi country
- verify SSID/password
- test Ethernet on management VLAN
- inspect `nmcli device status`
- check DHCP reservation after recording the correct MAC

Desktop is slow:

- close browser tabs
- avoid Chromium-heavy apps
- delay Docker, VS Code, MQTT Explorer, and AI frameworks
- check `btop`, temperature, and throttling

OLED is blank:

- run the script manually from the OLED guide
- check `minitower_oled.service`
- check journal logs
- verify I2C is enabled
- verify user is in `gpio` and `i2c`

ESP32 flashing fails:

- verify USB data cable
- check `lsusb`
- check `/dev/serial/by-id/`
- confirm user is in `dialout`
- try a different USB port

AI experiments overload the Pi:

- stop the experiment
- disable any local service created for it
- move inference to Frigate, docker-host, Proxmox, or a dedicated accelerator
- keep the Pi as the UI/control station

## Completion Checklist

- [ ] Raspberry Pi OS 64-bit Desktop boots from NVMe
- [ ] hostname is `garage-pi`
- [ ] manual login works
- [ ] Firefox works
- [ ] SSH service is enabled and reachable from management network
- [ ] Wi-Fi or Ethernet is on management VLAN
- [ ] static DHCP reservation is recorded
- [ ] Home Assistant is reachable
- [ ] VentSys dashboard URL is bookmarked
- [ ] Grafana and Uptime Kuma are reachable directly
- [ ] project repository is cloned or otherwise accessible
- [ ] OLED service is active and showing system status
- [ ] user is in `gpio`, `i2c`, and `dialout`
- [ ] ESP32 USB serial device can be identified
- [ ] Pi Camera baseline test passes if camera is installed
- [ ] AI and voice layers remain experimental and are not alarm-authoritative
- [ ] disk, temperature, and throttling checks are clean
