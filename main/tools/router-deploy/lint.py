#!/usr/bin/env python3
"""Static safety gate for OpenWrt router source specs."""

from __future__ import annotations

import ipaddress
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.parse_uci import (  # noqa: E402
    get_bridge_vlans,
    get_dhcp_scopes,
    get_domains,
    get_hosts,
    get_interfaces,
    get_rules,
    get_sections,
    get_wifi_ifaces,
    get_zones,
    load_conf,
)

ROOT = Path(__file__).resolve().parents[2]
CONF_DIR = ROOT / "configs" / "openwrt"
FILES = ["vlan-config.conf", "firewall-config.conf", "dhcp-config.conf", "wireless-config.conf", "system-config.conf"]

errors: list[str] = []
warnings: list[str] = []


def err(file_name: str, message: str, line: int = 0) -> None:
    prefix = f"{file_name}:{line}" if line else file_name
    errors.append(f"[ERROR] {prefix}: {message}")


def warn(file_name: str, message: str, line: int = 0) -> None:
    prefix = f"{file_name}:{line}" if line else file_name
    warnings.append(f"[WARN] {prefix}: {message}")


def check_merge_markers() -> None:
    markers = ("<<<<<<<", "=======", ">>>>>>>")
    for name in FILES:
        path = CONF_DIR / name
        if not path.exists():
            err(name, f"missing file: {path}")
            continue
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if any(line.strip().startswith(m) for m in markers):
                err(name, "merge conflict marker found", i)


def load_all() -> dict[str, list]:
    loaded: dict[str, list] = {}
    for name in FILES:
        path = CONF_DIR / name
        if not path.exists():
            # check_merge_markers already reported the missing file; skip
            # silently here to avoid duplicate errors on first-time setup.
            continue
        try:
            loaded[name] = load_conf(path)
        except Exception as ex:  # pragma: no cover
            err(name, f"parse failure: {ex}")
    return loaded


def required_sections_check(files: dict[str, list]) -> None:
    vlan = files.get("vlan-config.conf", [])
    fw = files.get("firewall-config.conf", [])
    dhcp = files.get("dhcp-config.conf", [])
    wifi = files.get("wireless-config.conf", [])

    interfaces = get_interfaces(vlan)
    bridge_vlans = get_bridge_vlans(vlan)
    zones = get_zones(fw)
    rules = get_rules(fw)
    scopes = get_dhcp_scopes(dhcp)
    hosts = get_hosts(dhcp)
    domains = get_domains(dhcp)
    wifi_ifaces = get_wifi_ifaces(wifi)

    required_interfaces = {"lan", "management", "automation", "nvr", "printers", "storage", "iot_sensors", "monitoring", "dmz", "guest"}
    missing_ifaces = required_interfaces - set(interfaces)
    if missing_ifaces:
        err("vlan-config.conf", f"missing required interfaces: {sorted(missing_ifaces)}")

    if len(bridge_vlans) < 10:
        err("vlan-config.conf", f"expected at least 10 bridge-vlan sections, found {len(bridge_vlans)}")

    required_zones = {"wan", "lan", "management", "automation", "nvr", "printers", "storage", "iot_sensors", "monitoring", "dmz", "guest", "vpn_clients"}
    missing_zones = required_zones - set(zones)
    if missing_zones:
        err("firewall-config.conf", f"missing required zones: {sorted(missing_zones)}")
    if len(rules) < 20:
        err("firewall-config.conf", "unexpectedly low number of firewall rules parsed")

    missing_scopes = required_interfaces - set(scopes)
    if missing_scopes:
        err("dhcp-config.conf", f"missing required dhcp scopes: {sorted(missing_scopes)}")
    if not hosts:
        warn("dhcp-config.conf", "no host reservations found")
    if not domains:
        warn("dhcp-config.conf", "no local domain records found")

    if len(wifi_ifaces) < 9:
        err("wireless-config.conf", f"expected >=9 wifi-iface sections, found {len(wifi_ifaces)}")
    ssids = {w.get("ssid") for w in wifi_ifaces}
    if "HomePrinters" not in ssids:
        err("wireless-config.conf", "HomePrinters SSID missing")


def cross_file_consistency(files: dict[str, list]) -> None:
    vlan = files.get("vlan-config.conf", [])
    fw = files.get("firewall-config.conf", [])
    dhcp = files.get("dhcp-config.conf", [])
    wifi = files.get("wireless-config.conf", [])

    interfaces = get_interfaces(vlan)
    if_names = set(interfaces)

    for zname, zone in get_zones(fw).items():
        for net in zone.get_list("network"):
            if net in {"wan", "wan6", "wg0"}:
                continue
            if net not in if_names:
                err("firewall-config.conf", f"zone '{zname}' references unknown interface '{net}'", zone.line_no)

    for sname, scope in get_dhcp_scopes(dhcp).items():
        iface = scope.get("interface", sname)
        if iface and iface not in if_names:
            err("dhcp-config.conf", f"scope '{sname}' references unknown interface '{iface}'", scope.line_no)

    for w in get_wifi_ifaces(wifi):
        net = w.get("network")
        ssid = w.get("ssid", "?")
        if net and net not in if_names:
            err("wireless-config.conf", f"SSID '{ssid}' references unknown interface '{net}'", w.line_no)


def vlan_set_consistency(files: dict[str, list]) -> None:
    vlan = files.get("vlan-config.conf", [])
    interfaces = get_interfaces(vlan)
    bridge_vlans = get_bridge_vlans(vlan)

    from_bridge = {int(v.get("vlan")) for v in bridge_vlans if (v.get("vlan") or "").isdigit()}
    from_ifaces = set()
    for iface in interfaces.values():
        dev = iface.get("device", "")
        m = re.match(r"br-lan\.(\d+)$", dev)
        if m:
            from_ifaces.add(int(m.group(1)))

    if from_bridge != from_ifaces:
        err("vlan-config.conf", f"bridge-vlan ids {sorted(from_bridge)} do not match interface VLAN ids {sorted(from_ifaces)}")

    pvid_map: dict[str, list[int]] = {}
    for bv in bridge_vlans:
        vid = bv.get("vlan")
        if not (vid and vid.isdigit()):
            continue
        for p in bv.get_list("ports"):
            if ":u" in p:
                port = p.split(":", 1)[0]
                pvid_map.setdefault(port, []).append(int(vid))
    for port, vids in pvid_map.items():
        if len(set(vids)) > 1:
            err("vlan-config.conf", f"port '{port}' has multiple PVIDs {sorted(set(vids))}")


def dhcp_range_and_reservations(files: dict[str, list]) -> None:
    vlan = files.get("vlan-config.conf", [])
    dhcp = files.get("dhcp-config.conf", [])

    interfaces = get_interfaces(vlan)
    scopes = get_dhcp_scopes(dhcp)
    hosts = get_hosts(dhcp)

    iface_to_subnet: dict[str, ipaddress.IPv4Network] = {}
    for name, iface in interfaces.items():
        ip = iface.get("ipaddr")
        mask = iface.get("netmask", "255.255.255.0")
        if not ip:
            continue
        try:
            iface_to_subnet[name] = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
        except Exception:
            warn("vlan-config.conf", f"could not parse subnet for interface '{name}'", iface.line_no)

    dynamic_ranges: list[tuple[str, ipaddress.IPv4Address, ipaddress.IPv4Address, int]] = []
    for sname, scope in scopes.items():
        iface_name = scope.get("interface", sname)
        start = scope.get("start")
        limit = scope.get("limit")
        subnet = iface_to_subnet.get(iface_name)
        if subnet is None:
            continue
        if not (start and limit and start.isdigit() and limit.isdigit()):
            continue
        # Range bounds and IP reconstruction below assume a /24. Surface a clear
        # warning rather than silently producing wrong addresses on /23, /25, etc.
        if subnet.prefixlen != 24:
            warn(
                "dhcp-config.conf",
                f"scope '{sname}' uses non-/24 subnet {subnet}; range validation skipped",
                scope.line_no,
            )
            continue
        s = int(start)
        l = int(limit)
        e = s + l - 1
        if s < 1 or e > 254:
            err("dhcp-config.conf", f"scope '{sname}' dynamic range .{s}-.{e} invalid", scope.line_no)
            continue
        start_ip = ipaddress.IPv4Address(f"{subnet.network_address.exploded.rsplit('.',1)[0]}.{s}")
        end_ip = ipaddress.IPv4Address(f"{subnet.network_address.exploded.rsplit('.',1)[0]}.{e}")
        if start_ip not in subnet or end_ip not in subnet:
            err("dhcp-config.conf", f"scope '{sname}' dynamic range outside subnet {subnet}", scope.line_no)
        dynamic_ranges.append((sname, start_ip, end_ip, scope.line_no))

    seen_ips: dict[str, tuple[str, int]] = {}
    for host in hosts:
        name = host.get("name", "?")
        ip_text = host.get("ip")
        if not ip_text:
            continue
        try:
            ip_obj = ipaddress.IPv4Address(ip_text)
        except Exception:
            err("dhcp-config.conf", f"host '{name}' has invalid IP '{ip_text}'", host.line_no)
            continue
        if ip_text in seen_ips:
            prev_name, prev_line = seen_ips[ip_text]
            err("dhcp-config.conf", f"duplicate static IP {ip_text} on '{name}' and '{prev_name}' (line {prev_line})", host.line_no)
        else:
            seen_ips[ip_text] = (name, host.line_no)

        if not any(ip_obj in subnet for subnet in iface_to_subnet.values()):
            err("dhcp-config.conf", f"host '{name}' static IP {ip_text} not inside any declared interface subnet", host.line_no)

        for scope_name, start_ip, end_ip, line_no in dynamic_ranges:
            if start_ip <= ip_obj <= end_ip:
                err("dhcp-config.conf", f"host '{name}' static IP {ip_text} overlaps dynamic pool of '{scope_name}'", host.line_no)
                break


def critical_input_rules(files: dict[str, list]) -> None:
    fw = files.get("firewall-config.conf", [])
    zones = get_zones(fw)
    rule_names = [r.get("name", "") for r in get_rules(fw)]

    restricted = [z for z, sec in zones.items() if sec.get("input") == "REJECT" and z != "wan"]

    for zone in sorted(restricted):
        if zone == "vpn_clients":
            # VPN clients may require DNS but not DHCP.
            has_dns = any(rn == f"Allow DNS input {zone}" for rn in rule_names)
            if not has_dns:
                err("firewall-config.conf", f"zone '{zone}' missing 'Allow DNS input {zone}'")
            continue

        has_dhcp = any(rn == f"Allow DHCP input {zone}" for rn in rule_names)
        has_dns = any(rn == f"Allow DNS input {zone}" for rn in rule_names)
        if not has_dhcp:
            err("firewall-config.conf", f"zone '{zone}' missing 'Allow DHCP input {zone}'")
        if not has_dns:
            err("firewall-config.conf", f"zone '{zone}' missing 'Allow DNS input {zone}'")


def architecture_policy_check(files: dict[str, list]) -> None:
    dhcp = files.get("dhcp-config.conf", [])
    fw = files.get("firewall-config.conf", [])
    system = files.get("system-config.conf", [])

    dnsmasq_sections = get_sections(dhcp, "dnsmasq")
    if not dnsmasq_sections:
        err("dhcp-config.conf", "missing dnsmasq section")
        return

    dnsmasq = dnsmasq_sections[0]
    servers = dnsmasq.get_list("server")
    if not servers or servers[0] != "192.168.20.102#53":
        err("dhcp-config.conf", "AdGuard Home on docker-host must be first upstream DNS server")
    if "9.9.9.9" not in servers:
        err("dhcp-config.conf", "Quad9 9.9.9.9 fallback DNS missing")
    if any(server in {"8.8.8.8", "8.8.4.4"} for server in servers):
        err("dhcp-config.conf", "Google Public DNS fallback is not approved for this project")
    if dnsmasq.get("strictorder") != "1":
        err("dhcp-config.conf", "dnsmasq strictorder must stay enabled for AdGuard-first fallback behavior")

    scopes = get_dhcp_scopes(dhcp)
    iot = scopes.get("iot_sensors")
    if iot:
        ntp_options = [opt for opt in iot.get_list("dhcp_option") if opt.startswith("42,") or opt == "42"]
        if ntp_options:
            err("dhcp-config.conf", "iot_sensors must not receive DHCP option 42; ESPHome time comes from HA")

    domains = {d.get("name"): d.get("ip") for d in get_domains(dhcp)}
    required_domains = {
        "adguard.home.local": "192.168.20.102",
        "immich.home.local": "192.168.20.102",
        "homepage.home.local": "192.168.20.102",
        "dozzle.home.local": "192.168.20.102",
        "omv.home.local": "192.168.40.50",
        "omv-nas.home.local": "192.168.40.50",
        "nas.home.local": "192.168.40.50",
    }
    for name, ip in required_domains.items():
        if domains.get(name) != ip:
            err("dhcp-config.conf", f"missing local DNS alias {name} -> {ip}")

    rules = {r.get("name", ""): r for r in get_rules(fw)}
    required_rules = [
        "Docker Host AdGuard Upstream DNS",
        "Docker Host Tailscale Egress",
        "Docker Host to InfluxDB",
        "LAN to Docker Host App UIs",
        "VPN to OMV NAS",
        "Block VPN to Storage",
        "Automation to Router NTP",
        "NVR to Router NTP",
        "Monitoring to Router NTP",
        "Storage to Router NTP",
        "Printers to Router NTP",
        "IoT to Router NTP",
    ]
    for rule in required_rules:
        if rule not in rules:
            err("firewall-config.conf", f"missing architecture rule '{rule}'")

    vpn_omv = rules.get("VPN to OMV NAS")
    if vpn_omv and (
        vpn_omv.get("dest") != "storage"
        or vpn_omv.get("dest_ip") != "192.168.40.50"
        or vpn_omv.get("target") != "ACCEPT"
    ):
        err("firewall-config.conf", "VPN to OMV NAS must be host-only to 192.168.40.50")

    block_storage = rules.get("Block VPN to Storage")
    if block_storage and (
        block_storage.get("dest") != "storage"
        or block_storage.get("dest_ip")
        or block_storage.get("target") != "REJECT"
    ):
        err("firewall-config.conf", "Block VPN to Storage must reject broad storage VLAN access")

    ntp_sections = [s for s in system if s.stype == "timeserver" and s.name == "ntp"]
    if not ntp_sections:
        err("system-config.conf", "missing timeserver 'ntp' section")
    else:
        ntp = ntp_sections[0]
        if ntp.get("enabled") != "1" or ntp.get("enable_server") != "1":
            err("system-config.conf", "router-local NTP server must be enabled")


def main() -> int:
    print("Router Config Lint")
    print("=" * 60)
    print(f"Config directory: {CONF_DIR}")
    print()

    check_merge_markers()
    files = load_all()
    if files:
        required_sections_check(files)
        cross_file_consistency(files)
        vlan_set_consistency(files)
        dhcp_range_and_reservations(files)
        critical_input_rules(files)
        architecture_policy_check(files)

    if warnings:
        print(f"Warnings: {len(warnings)}")
        for w in warnings:
            print(w)
        print()

    if errors:
        print(f"Errors: {len(errors)}")
        for e in errors:
            print(e)
        return 1

    print("PASSED: all checks clean.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
