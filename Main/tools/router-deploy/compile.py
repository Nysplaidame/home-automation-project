#!/usr/bin/env python3
"""Compile canonical OpenWrt source specs into deterministic deploy artifacts."""

from __future__ import annotations

import json
import sys
from argparse import ArgumentParser
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.parse_uci import (  # noqa: E402
    extract_bash_from_markdown,
    get_bridge_vlans,
    get_dhcp_scopes,
    get_interfaces,
    get_rules,
    get_wifi_ifaces,
    get_zones,
    parse_uci_commands,
    parse_uci_declarative,
)

ROOT = Path(__file__).resolve().parents[2]
CONF_DIR = ROOT / "configs" / "openwrt"
OUT_DIR = Path(__file__).resolve().parent / "generated"

PLACEHOLDER_PATTERNS = (
    "YOUR_",
    "CLIENT1_PUBLIC_KEY_HERE",
    "CLIENT2_PUBLIC_KEY_HERE",
    "CLIENT3_PUBLIC_KEY_HERE",
    "XX:XX:XX:XX:XX:XX",
)


@dataclass
class SectionSpan:
    stype: str
    name: str | None
    start: int
    end: int


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def _validate_invariants(vlan_sections: list) -> dict:
    bridge_vlans = get_bridge_vlans(vlan_sections)
    interfaces = get_interfaces(vlan_sections)

    lan5_vlan1_untagged = False
    for bv in bridge_vlans:
        if bv.get("vlan") == "1":
            lan5_vlan1_untagged = any(p.startswith("lan5:u") for p in bv.get_list("ports"))
            break

    lan_iface = interfaces.get("lan")
    lan_on_br_lan_1 = bool(lan_iface and lan_iface.get("device") == "br-lan.1")
    lan_gateway_ip = lan_iface.get("ipaddr") if lan_iface else None
    lan_gateway_expected = lan_gateway_ip == "192.168.1.1"

    return {
        "lan5_vlan1_untagged": lan5_vlan1_untagged,
        "lan5_pvid_intact_after_transforms": lan5_vlan1_untagged,
        "lan_on_br_lan_1": lan_on_br_lan_1,
        "lan_gateway_ip": lan_gateway_ip,
        "lan_gateway_expected_192_168_1_1": lan_gateway_expected,
    }


def _get_section_spans(text: str) -> list[SectionSpan]:
    lines = text.splitlines()
    cfg_re = re.compile(
        r"^\s*config\s+([A-Za-z0-9_-]+)(?:\s+'([^']*)'|\s+\"([^\"]*)\")?\s*$"
    )
    raw_spans: list[tuple[str, str | None, int]] = []
    for idx, line in enumerate(lines):
        m = cfg_re.match(line)
        if not m:
            continue
        raw_spans.append((m.group(1), m.group(2) if m.group(2) is not None else m.group(3), idx))

    spans: list[SectionSpan] = []
    for i, (stype, name, start) in enumerate(raw_spans):
        end = (raw_spans[i + 1][2] - 1) if i + 1 < len(raw_spans) else (len(lines) - 1)
        spans.append(SectionSpan(stype=stype, name=name, start=start, end=end))
    return spans


def _remove_matching_sections(
    text: str, predicate: Callable[[SectionSpan, list[str]], bool]
) -> tuple[str, int]:
    lines = text.splitlines()
    keep = [True] * len(lines)
    removed = 0
    for span in _get_section_spans(text):
        if predicate(span, lines):
            removed += 1
            for idx in range(span.start, span.end + 1):
                keep[idx] = False
    out_lines = [line for i, line in enumerate(lines) if keep[i]]
    return ("\n".join(out_lines).strip() + "\n"), removed


def _rewrite_wg0_as_stub(text: str) -> tuple[str, int]:
    lines = text.splitlines()
    rewritten = 0
    for span in _get_section_spans(text):
        if span.stype == "interface" and span.name == "wg0":
            replacement = [
                "config interface 'wg0'",
                "    option proto 'none'",
                "    option auto '0'",
            ]
            lines = lines[: span.start] + replacement + lines[span.end + 1 :]
            rewritten += 1
            break
    return ("\n".join(lines).strip() + "\n"), rewritten


def _disable_placeholder_wifi_ifaces(text: str) -> tuple[str, int]:
    lines = text.splitlines()
    changed = 0
    # Process from bottom to top so line insertions do not invalidate
    # still-to-be-processed section offsets.
    for span in reversed(_get_section_spans(text)):
        if span.stype != "wifi-iface":
            continue
        section_lines = lines[span.start : span.end + 1]
        has_placeholder_key = any(
            re.search(r"^\s*option\s+key\s+['\"]YOUR_", ln) for ln in section_lines
        )
        if not has_placeholder_key:
            continue

        disabled_idx: int | None = None
        for idx in range(span.start + 1, span.end + 1):
            if re.search(r"^\s*option\s+disabled\s+", lines[idx]):
                disabled_idx = idx
                break
        if disabled_idx is not None:
            if "option disabled '1'" not in lines[disabled_idx]:
                indent = re.match(r"^(\s*)", lines[disabled_idx]).group(1)
                lines[disabled_idx] = f"{indent}option disabled '1'"
        else:
            insert_at = span.start + 1
            indent = "    "  # default if no sibling option exists
            for idx in range(span.start + 1, span.end + 1):
                if re.search(r"^\s*(option|list)\s+", lines[idx]):
                    indent = re.match(r"^(\s*)", lines[idx]).group(1)
                    insert_at = idx + 1
            lines.insert(insert_at, f"{indent}option disabled '1'")
        changed += 1
    return ("\n".join(lines).strip() + "\n"), changed


def _strip_temp_firewall_rules(text: str) -> tuple[str, int]:
    """Strip TEMP-prefixed firewall rules from a generated firewall.sh script.

    Any rule whose name begins with 'TEMP ' is stripped regardless of profile.

    SOURCE FORMAT CONSTRAINT: a rule "block" must consist solely of the
    `uci add firewall rule` line followed by `uci set/add_list
    firewall.@rule[-1].*` lines, blank lines, and comments. Any other shell
    statement (e.g. `uci commit firewall`) appearing inside a rule block will
    terminate the block and leave the rule untouched. Keep `commit` calls at
    the end of the source script, not interleaved with rule definitions.
    """
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    removed = 0

    while i < len(lines):
        line = lines[i]
        if line.strip() != "uci add firewall rule":
            out.append(line)
            i += 1
            continue

        j = i + 1
        while j < len(lines):
            s = lines[j].strip()
            if s == "uci add firewall rule":
                break
            # Rule body lines in this script are uci set/add_list targeting @rule[-1],
            # plus optional comments/blank separators.
            if (
                not s
                or s.startswith("#")
                or re.search(r"^\s*uci\s+(set|add_list)\s+firewall\.@rule\[-1\]\.", lines[j])
            ):
                j += 1
                continue
            break
        block = lines[i:j]

        rule_name = None
        for block_line in block:
            m = re.search(
                r"""^\s*uci\s+set\s+firewall\.@rule\[-1\]\.name\s*=\s*(['"])(.+?)\1\s*$""",
                block_line,
            )
            if m:
                rule_name = m.group(2).strip()
                break

        if rule_name and rule_name.startswith("TEMP "):
            removed += 1
        else:
            out.extend(block)
        i = j

    return ("\n".join(out).strip() + "\n"), removed


def _first_flight_transform(artifacts: dict[str, str]) -> tuple[dict[str, str], dict[str, int]]:
    network = artifacts["network.uci"]
    dhcp = artifacts["dhcp.uci"]
    wireless = artifacts["wireless.uci"]

    # Minimum safe boot: keep an inert wg0 stub and remove peer definitions.
    network, wg0_stubbed = _rewrite_wg0_as_stub(network)
    network, removed_wg_peer_sections = _remove_matching_sections(
        network,
        lambda span, _lines: span.stype == "wireguard_wg0",
    )

    # Remove static reservations that still carry placeholder MACs.
    dhcp, removed_placeholder_hosts = _remove_matching_sections(
        dhcp,
        lambda span, lines: span.stype == "host"
        and any("XX:XX:XX:XX:XX:XX" in ln for ln in lines[span.start : span.end + 1]),
    )

    # Disable SSIDs whose keys are still placeholders to avoid known credentials.
    wireless, disabled_wifi_ifaces = _disable_placeholder_wifi_ifaces(wireless)

    transformed = dict(artifacts)
    transformed["network.uci"] = network
    transformed["dhcp.uci"] = dhcp
    transformed["wireless.uci"] = wireless

    stats = {
        "wg0_stubbed": wg0_stubbed,
        "removed_wg_peer_sections": removed_wg_peer_sections,
        "removed_placeholder_hosts": removed_placeholder_hosts,
        "disabled_wifi_ifaces": disabled_wifi_ifaces,
    }
    return transformed, stats


def _find_placeholders(artifacts: dict[str, str]) -> dict[str, list[tuple[int, str]]]:
    hits: dict[str, list[tuple[int, str]]] = {}
    for name, content in artifacts.items():
        for line_no, line in enumerate(content.splitlines(), start=1):
            if any(pattern in line for pattern in PLACEHOLDER_PATTERNS):
                hits.setdefault(name, []).append((line_no, line.strip()))
    return hits


def compile_artifacts(profile: str = "full", allow_placeholders: bool = False) -> int:
    vlan_path = CONF_DIR / "vlan-config.conf"
    dhcp_path = CONF_DIR / "dhcp-config.conf"
    wireless_path = CONF_DIR / "wireless-config.conf"
    firewall_path = CONF_DIR / "firewall-config.conf"

    for p in (vlan_path, dhcp_path, wireless_path, firewall_path):
        if not p.exists():
            print(f"[ERROR] Missing source file: {p}")
            return 1

    vlan_text = _read(vlan_path)
    dhcp_raw = _read(dhcp_path)
    wireless_text = _read(wireless_path)
    firewall_text = _read(firewall_path)
    dhcp_uci = extract_bash_from_markdown(dhcp_raw).strip()
    if not dhcp_uci:
        print("[ERROR] dhcp-config.conf did not contain a ```bash fenced block.")
        return 1

    artifacts = {
        "network.uci": vlan_text.strip() + "\n",
        "dhcp.uci": dhcp_uci + "\n",
        "wireless.uci": wireless_text.strip() + "\n",
        "firewall.sh": firewall_text.strip() + "\n",
    }

    first_flight_stats = {
        "wg0_stubbed": 0,
        "removed_wg_peer_sections": 0,
        "removed_placeholder_hosts": 0,
        "disabled_wifi_ifaces": 0,
        "stripped_temp_firewall_rules": 0,
    }
    if profile == "first-flight":
        artifacts, first_flight_stats = _first_flight_transform(artifacts)

    # Strip TEMP-prefixed firewall rules unconditionally — these are never safe to deploy.
    artifacts["firewall.sh"], stripped_temp_rules = _strip_temp_firewall_rules(artifacts["firewall.sh"])

    effective_allow_placeholders = allow_placeholders or profile == "first-flight"
    placeholder_hits = _find_placeholders(artifacts)
    if placeholder_hits and not effective_allow_placeholders:
        print("[ERROR] Placeholder values remain in deploy artifacts.")
        print("        Replace secrets/MACs before deployment, or run with")
        print("        --allow-placeholders for preview-only artifact generation.")
        for name, hits in placeholder_hits.items():
            print(f"  - {name}: {len(hits)} placeholder line(s)")
            for line_no, text in hits[:8]:
                print(f"      {line_no}: {text}")
            if len(hits) > 8:
                print(f"      ... {len(hits) - 8} more")
        return 1

    vlan_sections = parse_uci_declarative(artifacts["network.uci"])
    fw_sections = parse_uci_commands(artifacts["firewall.sh"], package_hint="firewall")
    dhcp_sections = parse_uci_declarative(artifacts["dhcp.uci"])
    wifi_sections = parse_uci_declarative(artifacts["wireless.uci"])

    vlan_ids = sorted(
        {
            int(v.get("vlan"))
            for v in get_bridge_vlans(vlan_sections)
            if (v.get("vlan") or "").isdigit()
        }
    )
    iface_names = sorted(get_interfaces(vlan_sections).keys())
    zone_names = sorted(get_zones(fw_sections).keys())
    scope_names = sorted(get_dhcp_scopes(dhcp_sections).keys())
    ssids = sorted({w.get("ssid") for w in get_wifi_ifaces(wifi_sections) if w.get("ssid")})

    invariants = _validate_invariants(vlan_sections)

    bad = [k for k, v in invariants.items() if isinstance(v, bool) and not v]
    if bad:
        print("[ERROR] Compile invariant failures:")
        for name in bad:
            print(f"  - {name}")
        return 1

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "profile": profile,
        "target": {
            "router_ip": "192.168.1.1",
            "expected_model": "GL.iNet GL-MT6000",
            "expected_platform": "OpenWrt",
        },
        "counts": {
            "vlan_ids": vlan_ids,
            "vlan_count": len(vlan_ids),
            "interfaces": len(iface_names),
            "firewall_zones": len(zone_names),
            "firewall_rules": len(get_rules(fw_sections)),
            "dhcp_scopes": len(scope_names),
            "wifi_ifaces": len(get_wifi_ifaces(wifi_sections)),
            "ssid_count": len(ssids),
        },
        "names": {
            "interfaces": iface_names,
            "zones": zone_names,
            "dhcp_scopes": scope_names,
            "ssids": ssids,
        },
        "invariants": invariants,
        "stripped_temp_rules": stripped_temp_rules,
        "first_flight_adjustments": first_flight_stats,
    }

    for name, content in artifacts.items():
        _write(OUT_DIR / name, content)
    _write(OUT_DIR / "summary.json", json.dumps(summary, indent=2) + "\n")

    if placeholder_hits and profile == "first-flight":
        print("[WARN] Placeholder values remain but are contained by first-flight transforms.")
    elif placeholder_hits:
        print("[WARN] Placeholder values were allowed for preview-only generation.")
    if stripped_temp_rules:
        print(f"[INFO] Stripped {stripped_temp_rules} TEMP firewall rule(s).")
    if profile == "first-flight":
        print("[INFO] First-flight adjustments applied:")
        for key, value in first_flight_stats.items():
            print(f"  - {key}: {value}")

    print("[OK] Artifacts written:")
    for f in ("network.uci", "dhcp.uci", "wireless.uci", "firewall.sh", "summary.json"):
        print(f"  - {OUT_DIR / f}")
    return 0


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        choices=("full", "first-flight"),
        default="full",
        help="Compile profile: full (strict) or first-flight (minimum safe boot).",
    )
    parser.add_argument(
        "--allow-placeholders",
        action="store_true",
        help="Generate artifacts for preview/audit even when deploy placeholders remain.",
    )
    args = parser.parse_args()
    raise SystemExit(
        compile_artifacts(profile=args.profile, allow_placeholders=args.allow_placeholders)
    )
