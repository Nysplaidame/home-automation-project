#!/usr/bin/env python3
"""Parser helpers for OpenWrt source specs and generated artifacts."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class UCISection:
    stype: str
    name: Optional[str]
    line_no: int
    options: dict[str, str] = field(default_factory=dict)
    lists: dict[str, list[str]] = field(default_factory=dict)

    def get(self, key: str, default=None):
        return self.options.get(key, default)

    def get_list(self, key: str) -> list[str]:
        return self.lists.get(key, [])


def extract_bash_from_markdown(text: str) -> str:
    """Extract all ```bash fenced blocks and return joined text."""
    lines = text.splitlines()
    out: list[str] = []
    in_block = False
    for line in lines:
        stripped = line.strip().lower()
        if stripped.startswith("```bash"):
            in_block = True
            continue
        if in_block and stripped == "```":
            in_block = False
            continue
        if in_block:
            out.append(line)
    return "\n".join(out)


def parse_uci_declarative(text: str) -> list[UCISection]:
    """Parse config/option/list syntax from UCI-style files."""
    config_re = re.compile(
        r"^\s*config\s+([A-Za-z0-9_-]+)(?:\s+'([^']*)'|\s+\"([^\"]*)\")?\s*(?:#.*)?\s*$"
    )
    option_re = re.compile(
        r"^\s*option\s+([A-Za-z0-9_-]+)\s+(?:'([^']*)'|\"([^\"]*)\"|(\S+))\s*(?:#.*)?\s*$"
    )
    list_re = re.compile(
        r"^\s*list\s+([A-Za-z0-9_-]+)\s+(?:'([^']*)'|\"([^\"]*)\"|(\S+))\s*(?:#.*)?\s*$"
    )

    sections: list[UCISection] = []
    current: Optional[UCISection] = None

    for line_no, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        m = config_re.match(line)
        if m:
            current = UCISection(
                stype=m.group(1),
                name=m.group(2) if m.group(2) is not None else m.group(3),
                line_no=line_no,
            )
            sections.append(current)
            continue

        if current is None:
            continue

        m = option_re.match(line)
        if m:
            current.options[m.group(1)] = m.group(2) or m.group(3) or m.group(4) or ""
            continue

        m = list_re.match(line)
        if m:
            current.lists.setdefault(m.group(1), []).append(
                m.group(2) or m.group(3) or m.group(4) or ""
            )

    return sections


def _expand_shell_for_loops(text: str) -> str:
    """Expand simple one-level loops:
    for ZONE in a b c; do
      ...
    done
    """
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    header_re = re.compile(r"^\s*for\s+([A-Za-z_][A-Za-z0-9_]*)\s+in\s+(.+?)\s*;\s*do\s*$")

    while i < len(lines):
        line = lines[i]
        hm = header_re.match(line)
        if not hm:
            out.append(line)
            i += 1
            continue

        var_name = hm.group(1)
        values = hm.group(2).split()
        i += 1
        body: list[str] = []
        while i < len(lines) and not re.match(r"^\s*done\s*$", lines[i]):
            body.append(lines[i])
            i += 1
        if i < len(lines) and re.match(r"^\s*done\s*$", lines[i]):
            i += 1

        # Use word-boundary regex so $VAR doesn't accidentally match the
        # prefix of $VARNAME. Replacement is via a callable to keep `value`
        # literal — re.sub's replacement string would otherwise interpret
        # backslash sequences like \1 as backreferences.
        var_re = re.compile(
            rf"\$\{{{re.escape(var_name)}\}}|\${re.escape(var_name)}\b"
        )
        for value in values:
            for body_line in body:
                expanded = var_re.sub(lambda _m, v=value: v, body_line)
                out.append(expanded)

    return "\n".join(out)


def parse_uci_commands(text: str, package_hint: str = "firewall") -> list[UCISection]:
    """Parse uci add/set/add_list commands from shell scripts."""
    expanded = _expand_shell_for_loops(text)

    add_re = re.compile(rf"\buci\s+add\s+{re.escape(package_hint)}\s+([A-Za-z0-9_-]+)\b")
    set_re = re.compile(
        rf"\buci\s+set\s+{re.escape(package_hint)}\.@([A-Za-z0-9_-]+)\[-1\]\.([A-Za-z0-9_-]+)\s*=\s*(?:'([^']*)'|\"([^\"]*)\"|(\S+))"
    )
    add_list_re = re.compile(
        rf"\buci\s+add_list\s+{re.escape(package_hint)}\.@([A-Za-z0-9_-]+)\[-1\]\.([A-Za-z0-9_-]+)\s*=\s*(?:'([^']*)'|\"([^\"]*)\"|(\S+))"
    )

    sections: list[UCISection] = []
    current: Optional[UCISection] = None

    for line_no, raw in enumerate(expanded.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        m = add_re.search(line)
        if m:
            current = UCISection(stype=m.group(1), name=None, line_no=line_no)
            sections.append(current)
            continue

        if current is None:
            continue

        m = set_re.search(line)
        if m:
            key = m.group(2)
            val = m.group(3) or m.group(4) or m.group(5) or ""
            current.options[key] = val
            if key == "name":
                current.name = val
            continue

        m = add_list_re.search(line)
        if m:
            key = m.group(2)
            val = m.group(3) or m.group(4) or m.group(5) or ""
            current.lists.setdefault(key, []).append(val)
            continue

    return sections


def load_conf(path: Path) -> list[UCISection]:
    text = path.read_text(encoding="utf-8")
    name = path.name
    if name == "dhcp-config.conf":
        return parse_uci_declarative(extract_bash_from_markdown(text))
    if name == "firewall-config.conf":
        return parse_uci_commands(text, package_hint="firewall")
    return parse_uci_declarative(text)


def get_sections(sections: list[UCISection], stype: str) -> list[UCISection]:
    return [s for s in sections if s.stype == stype]


def get_named_sections(sections: list[UCISection], stype: str) -> dict[str, UCISection]:
    return {s.name: s for s in sections if s.stype == stype and s.name}


def get_interfaces(sections: list[UCISection]) -> dict[str, UCISection]:
    return get_named_sections(sections, "interface")


def get_bridge_vlans(sections: list[UCISection]) -> list[UCISection]:
    return get_sections(sections, "bridge-vlan")


def get_zones(sections: list[UCISection]) -> dict[str, UCISection]:
    return get_named_sections(sections, "zone")


def get_rules(sections: list[UCISection]) -> list[UCISection]:
    return get_sections(sections, "rule")


def get_dhcp_scopes(sections: list[UCISection]) -> dict[str, UCISection]:
    return get_named_sections(sections, "dhcp")


def get_hosts(sections: list[UCISection]) -> list[UCISection]:
    return get_sections(sections, "host")


def get_domains(sections: list[UCISection]) -> list[UCISection]:
    return get_sections(sections, "domain")


def get_wifi_ifaces(sections: list[UCISection]) -> list[UCISection]:
    return get_sections(sections, "wifi-iface")

