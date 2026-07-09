export const diagrams = [
  {
    id: 'current-master-architecture',
    title: 'Current Master Architecture',
    section: 'network',
    path: 'network/current-master-architecture.mermaid',
    summary: 'Whole-system placement: router, Proxmox, VMs, docker-host, OMV, services, and physical integrations.',
    tags: ['architecture', 'services', 'placement'],
    source: `flowchart TB
    Operator["Admin laptop / phone"]
    Internet["Internet"]
    Router["OpenWrt router<br/>DHCP, local DNS, firewall, NTP<br/>192.168.10.1"]
    Proxmox["Proxmox host<br/>MINISFORUM M1 Pro-125H<br/>192.168.10.10"]
    EdgeSwitch["Planned managed switch<br/>Zyxel GS1900-8HP<br/>VLAN trunk from router lan3"]

    Internet --- Router
    Operator --> Router
    Router --- Proxmox
    Router -.-> EdgeSwitch`
  },
  {
    id: 'vlan-architecture-clean',
    title: 'VLAN Architecture Clean',
    section: 'network',
    path: 'network/vlan_architecture_clean.mermaid',
    summary: 'VLANs, subnets, router role, physical ports, local AI, and remote access placement.',
    tags: ['vlan', 'router', 'network'],
    source: `flowchart TB
    V10["VLAN 10 Management"]
    V20["VLAN 20 Automation"]
    V30["VLAN 30 NVR"]
    V35["VLAN 35 Printers"]
    V40["VLAN 40 Storage"]
    V50["VLAN 50 HomeIoT"]
    V60["VLAN 60 Monitoring"]
    V70["VLAN 70 DMZ"]
    V99["VLAN 99 Guest"]`
  },
  {
    id: 'remote-access-flow',
    title: 'Remote Access Flow',
    section: 'network',
    path: 'network/remote-access-flow.mermaid',
    summary: 'Tailscale daily access, docker-host host routes, and WireGuard fallback.',
    tags: ['tailscale', 'wireguard', 'remote access'],
    source: `flowchart LR
    Client["Remote client"]
    Tailscale["Tailscale"]
    DockerHost["docker-host"]
    WireGuard["WireGuard fallback"]
    Client --> Tailscale --> DockerHost
    Client -.-> WireGuard`
  },
  {
    id: 'dns-ntp-flow',
    title: 'DNS and NTP Flow',
    section: 'network',
    path: 'network/dns-ntp-flow.mermaid',
    summary: 'Router DNS/NTP authority, AdGuard Home, fallback resolution, and HA time.',
    tags: ['dns', 'ntp', 'adguard'],
    source: `flowchart LR
    Router["OpenWrt"]
    AdGuard["AdGuard Home"]
    Clients["Clients"]
    Clients --> Router --> AdGuard`
  },
  {
    id: 'security-access-flow',
    title: 'Security Access Flow',
    section: 'network',
    path: 'network/security-access-flow.mermaid',
    summary: 'Firewall, ACL, host firewall, service auth, and blocked path intent.',
    tags: ['firewall', 'security', 'acl'],
    source: `flowchart TB
    LAN --> FW["Firewall rules"]
    FW --> Services["Internal services"]
    FW -.-> Blocked["Blocked paths"]`
  },
  {
    id: 'install-sequence',
    title: 'Install Sequence',
    section: 'install',
    path: 'install/install-sequence.mermaid',
    summary: 'Fresh rebuild phase order and validation gates.',
    tags: ['install', 'sequence', 'rebuild'],
    source: `flowchart LR
    A["Phase 1"] --> B["Phase 2"] --> C["Phase 3"] --> D["Phase 4"]`
  },
  {
    id: 'docker-host-service-placement',
    title: 'Docker-host Service Placement',
    section: 'infrastructure',
    path: 'infrastructure/docker-host-service-placement.mermaid',
    summary: 'Docker-host stack layout, tiering, future query-app boundary, and backup placement.',
    tags: ['docker-host', 'services', 'placement'],
    source: `flowchart TB
    DockerHost["docker-host"]
    Tier1["Tier 1"]
    Tier2["Tier 2"]
    Tier3["Tier 3"]`
  },
  {
    id: 'storage-and-backup-flow',
    title: 'Storage and Backup Flow',
    section: 'storage',
    path: 'storage/storage-and-backup-flow.mermaid',
    summary: 'OMV shares, HA/Frigate/Immich storage, backups, and restore drills.',
    tags: ['storage', 'backup', 'omv'],
    source: `flowchart LR
    OMV["OMV NAS"]
    Backups["Backups"]
    Apps["Apps"]
    Apps --> OMV --> Backups`
  },
  {
    id: 'ventsys-control-and-safety-flow',
    title: 'VentSys Control and Safety Flow',
    section: 'ventsys',
    path: 'ventsys/ventsys-control-and-safety-flow.mermaid',
    summary: 'VentSys control loop, MQTT/ESPHome path, airflow, and safety behavior.',
    tags: ['ventsys', 'safety', 'mqtt'],
    source: `flowchart TB
    Sensors --> HA["Home Assistant"]
    HA --> Actuators
    HA -.-> Safety["Safety state"]`
  }
];
