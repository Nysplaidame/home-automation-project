# TP-Link TL-WA801N — WiFi AP Setup Guide

**Hardware:** TP-Link TL-WA801N (802.11b/g/n, 2.4GHz only, 300Mbps)  
**Role:** Wired access point extending the HomeMain network (VLAN 1, 192.168.1.0/24)  
**Connection:** planned managed-switch access port, untagged VLAN 1
**When to do this:** After router setup is complete and stable

---

## Overview

In the planned managed-switch layout, router `lan5` remains a direct VLAN 1
LAN/recovery port. The TL-WA801N moves to a managed-switch access port configured
as untagged VLAN 1/PVID 1. Do not move the extender until the managed switch is
installed and its VLAN access-port test passes.

The TL-WA801N is 2.4GHz only and has no VLAN awareness. It receives untagged traffic
from the switch access port and broadcasts it as its own SSID. Clients connecting
to the extender are transparently on the main LAN — they get 192.168.1.x IPs from
the router's DHCP pool and fall under the existing `lan` firewall zone with full
internet access.

---

## Physical Setup

1. Place the TL-WA801N where coverage is needed
2. Run an ethernet cable from the **managed switch VLAN 1 access port** to the **TL-WA801N LAN port**
   (use the LAN port, not the WAN port — the WAN port is only used in Repeater/Client mode)
3. Power the TL-WA801N via its included adapter

---

## TL-WA801N Configuration

### Step 1 — Factory reset (recommended)

Hold the reset button on the back for 10 seconds until the power LED flashes.

### Step 2 — Connect to the extender directly

The TL-WA801N defaults to 192.168.0.254 on its own DHCP range when freshly reset.
Temporarily connect your laptop directly to the TL-WA801N LAN port with a second cable
(or connect to its default SSID `TP-Link_XXXXXX`).

Open `http://192.168.0.254` in a browser. Default credentials: `admin` / `admin`.

### Step 3 — Set to Access Point mode

Go to **Operation Mode** → select **Access Point** → Save/Apply.

The device will reboot. In AP mode it no longer runs its own DHCP server and stops
acting as a router — it becomes a transparent bridge between its WiFi and its LAN port.

### Step 4 — Configure the SSID

After reboot, reconnect to the management interface. In AP mode the TL-WA801N will
receive its management IP from the GL-MT6000's DHCP server (192.168.1.x range).
Check your router's DHCP leases table to find it, or use `nmap -sn 192.168.1.0/24`.

Go to **Wireless** → **Wireless Settings**:

| Field | Recommended value |
|---|---|
| SSID | `HomeMain` — same as the router (seamless roaming) |
| Mode | 802.11b/g/n mixed |
| Channel | `6` — matches radio0 on the GL-MT6000 |
| Security | WPA2-PSK (TKIP/AES) |
| Password | Same as HomeMain WiFi password |

Using the same SSID allows devices to roam between the router and the extender without
manually switching networks. Channel 6 matches the router's 2.4GHz radio so clients
roam on the same channel without interference.

### Step 5 — Reserve a DHCP IP for the extender

Once you know the extender's MAC address (printed on the label or visible in the
GL-MT6000 DHCP leases table), add a static reservation to dhcp-config.conf:

```
config host
    option name 'homeextender'
    option dns '1'
    option mac 'XX:XX:XX:XX:XX:XX'   # TL-WA801N MAC
    option ip '192.168.1.203'
```

Suggested IP: 192.168.1.203 (above the .201/.202 Raspberry Pi display reservations).

---

## What does NOT change

| Item | Change needed? |
|---|---|
| vlan-config.conf | Yes for the future managed-switch layout — router `lan3` trunk carries VLAN 1 tagged; the switch presents VLAN 1 untagged to the extender |
| firewall-config.conf | No — extender clients fall under existing `lan` zone |
| dhcp-config.conf | Only the optional static reservation above |
| wireless-config.conf | No — router SSIDs unchanged |
| Any HA config | No |

---

## Limitations to be aware of

**2.4GHz only.** The TL-WA801N cannot extend the 5GHz HomeMain band. Clients that
support 5GHz and connect to the router directly will get better throughput. The extender
is useful for areas where the 5GHz signal doesn't reach, or for older 2.4GHz-only devices.

**No VLAN support.** The extender cannot serve multiple VLANs. It is permanently on
VLAN 1 (main LAN). Do not use it for HomeAdmin, HomeIoT, or HomeGuest clients — those
networks are WiFi-only via the router's own radios.

**Management access.** The extender's web UI is accessible at its 192.168.1.x address
from the main LAN. It is not accessible from other VLANs (management, IoT, etc.) as
those cannot reach 192.168.1.x.

**802.11n (WiFi 4) speed cap.** Maximum 300Mbps theoretical; real-world ~100Mbps.
Adequate for general browsing, streaming, and smart home devices. Not suitable as
a backhaul for the Frigate VM or NAS.
