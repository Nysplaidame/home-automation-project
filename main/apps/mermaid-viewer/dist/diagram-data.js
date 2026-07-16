export const diagrams = [
  {
    id: 'current-master-architecture',
    title: 'Logical Architecture',
    section: 'network',
    path: 'network/current-master-architecture.mermaid',
    summary: 'Logical VLANs, Proxmox guests, services, storage, and local/remote access paths.',
    tags: ['architecture', 'services', 'placement'],
    source: `flowchart TB
    Internet["Internet"] --> Router["GL.iNet GL-MT6000 OpenWrt<br/>DHCP, local DNS, firewall, NTP"]
    Router --> Proxmox["proxmox / MINISFORUM mini PC<br/>192.168.10.10; 8006,22"]
    Rollback["VM 101 Frigate and VM 104 llm-host<br/>powered off; rollback only"]
    Proxmox -.-> Rollback
    LAN["VLAN 1 HomeMain<br/>192.168.1.0/24; HomeMain 2.4/5 GHz"]
    Admin["VLAN 10 Management<br/>192.168.10.0/24; HomeAdmin / HomeAdmin-2G"]
    Printers["VLAN 35 Printers<br/>192.168.35.0/24; HomePrinters"]
    IoT["VLAN 50 HomeIoT<br/>192.168.50.0/24; HomeIoT 2.4 GHz"]
    DMZ["VLAN 70 DMZ<br/>192.168.70.0/24; HomeDMZ disabled"]
    Guest["VLAN 99 Guest<br/>192.168.99.0/24; HomeGuest internet-only"]
    Router --- LAN
    Router --- Admin
    Router --- Printers
    Router --- IoT
    Router --- DMZ
    Router --- Guest
    subgraph Automation["VLAN 20 Automation | 192.168.20.0/24"]
      HA["home-assistant VM 100<br/>.101:8123 HTTPS, 8883 MQTT"]
      Docker["docker-host VM 103<br/>.102"]
      LLM["llm-host CT 114<br/>.104"]
      OpenWebUI["Open WebUI<br/>.104:3002<br/>openwebui.home.local"]
      Voice["llama.cpp 8081/8082<br/>Whisper 10200; Piper 10300; OpenWakeWord 10400"]
    end
    subgraph NVR["VLAN 30 NVR | 192.168.30.0/24"]
      Frigate["frigate-nvr CT 111<br/>.20:8971,5000,8554,8555"]
      Camera["cam-01-annke-c500<br/>.21"]
    end
    subgraph Storage["VLAN 40 Storage | 192.168.40.0/24"]
      OMV["omvnas .50<br/>80,22,445,2049,8088"]
    end
    subgraph Monitoring["VLAN 60 Monitoring | 192.168.60.0/24"]
      Monitor["monitoring VM 102 .10<br/>Grafana 3000; Kuma 3001; InfluxDB 8086"]
    end
    Proxmox --> HA
    Proxmox --> Docker
    Proxmox --> LLM
    Proxmox --> Frigate
    Proxmox --> Monitor
    Camera -->|"RTSP"| Frigate
    HA -->|"LLM / voice"| LLM
    LLM --- OpenWebUI
    LLM --- Voice
    OMV -->|"NFS recordings"| Frigate
    OMV -->|"NFS backups/media"| HA
    subgraph DockerBox["docker-host containers"]
      AdGuard["AdGuard Home\n53/8080"]
      Immich["Immich\n2283"]
      Homepage["Homepage\n3001"]
      Dozzle["Dozzle\n8081"]
      Viewer["Mermaid Viewer\n8092"]
      Bambuddy["Bambuddy\n8000"]
      Ntfy["ntfy\n8085"]
      Mealie["Mealie\n9925"]
      Grocy["Grocy\n9283"]
      LiveSync["Obsidian LiveSync\n5984/8443"]
      Garden["GardenKeeper\n8090/8091"]
      Search["SearXNG 8087\nWhoogle 8088"]
      Ops["Watchtower monitor-only\nTelegraf -> 8086"]
    end
    Docker --- AdGuard
    Docker --- Immich
    Docker --- Homepage
    Docker --- Dozzle
    Docker --- Viewer
    Docker --- Bambuddy
    Docker --- Ntfy
    Docker --- Mealie
    Docker --- Grocy
    Docker --- LiveSync
    Docker --- Garden
    Docker --- Search
    Docker --- Ops
    Mobile["Android phone<br/>100.105.216.6 observed"] --> Tailnet["Tailscale overlay<br/>DERP London relay currently"] --> Tail["docker-host tailscale0<br/>100.94.122.18"] --> Docker
    Tail --> Routes["Approved: HA .101; OMV .50; Monitoring .10<br/>Frigate .20 advertised, approval pending"]
    Tail -.-> Setup["tailscale up: accept DNS false; hostname docker-host;<br/>advertise only four /32 routes; IP forwarding + ACL/UFW/OpenWrt port rules"]
    Routes --> HA
    Routes --> OMV
    Routes --> Monitor
    Routes -.->|"HTTPS 8971 only after approval"| Frigate
    classDef core fill:#e8a349,stroke:#6e4315,color:#1c1c1c
    classDef compute fill:#81b29a,stroke:#2f6654,color:#102c24
    classDef app fill:#9ec1cf,stroke:#376a7a,color:#102a32
    classDef remote fill:#f1a6a6,stroke:#8e3b3b,color:#3d1010
    class Router core
    class Proxmox,HA,Docker,LLM,Frigate,Monitor compute
    class OpenWebUI,Voice,AdGuard,Immich,Homepage,Dozzle,Viewer,Bambuddy,Ntfy,Mealie,Grocy,LiveSync,Garden,Search,Ops app
    class Mobile,Tailnet,Tail,Routes remote`
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
    id: 'physical-port-and-cabling',
    title: 'Physical Devices, Ports, and Cabling',
    section: 'network',
    path: 'network/physical-port-and-cabling.mermaid',
    summary: 'Physical device inventory, router/GS1900 port map, Wi-Fi endpoints, and CCTV capacity.',
    tags: ['ports', 'cabling', 'switch', 'cctv', 'poe'],
    source: `flowchart LR
    Upstream["Upstream router/modem"] --> WAN
    subgraph RouterPorts["router: GL.iNet GL-MT6000"]
      direction TB
      WAN["wan: live upstream DHCP"]
      LAN1["lan1: live tagged trunk"]
      LAN2["lan2: unconnected VLAN 10"]
      LAN3["lan3: live tagged trunk"]
      LAN4["lan4: live OMV NAS VLAN 40"]
      LAN5["lan5: unconnected VLAN 1"]
    end
    LAN1 --> Proxmox["proxmox / MINISFORUM mini PC\n192.168.10.10"]
    LAN3 --> SW1
    subgraph SwitchPorts["gs1900-switch: ports top to bottom"]
      direction TB
      SW1["1: router trunk"]
      SW2["2: live PoE camera"]
      SW3["3-7: future PoE cameras"]
      SW8["8: spare VLAN 40 storage"]
    end
    SW2 --> Camera1["cam-01-annke-c500\n192.168.30.21"]
    SW3 -.-> Cameras["cam-02 through cam-06"]
    LAN4 --> OMV["omvnas\n192.168.40.50"]
    LAN2 -.-> Admin["Admin workstation"]
    LAN5 -.-> Recovery["Recovery laptop"]`
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
    id: 'proxmox-guests-and-backups',
    title: 'Proxmox Guests and Backups',
    section: 'infrastructure',
    path: 'infrastructure/proxmox-guests-and-backups.mermaid',
    summary: 'MINISFORUM Proxmox host, all production and rollback guests, shared iGPU, and OMV backup jobs.',
    tags: ['proxmox', 'vm', 'lxc', 'backup', 'gpu'],
    source: `flowchart TB
    Proxmox["proxmox / MINISFORUM M1 Pro<br/>192.168.10.10:8006"]
    HA["VM 100 home-assistant\nVLAN 20 .101\n2c/6 GiB/32 GiB"]
    Frigate["CT 111 frigate-nvr\nVLAN 30 .20\n2c/6 GiB/32 GiB"]
    Monitor["VM 102 monitoring\nVLAN 60 .10\n2c/3 GiB/32 GiB"]
    Docker["VM 103 docker-host\nVLAN 20 .102\n2c/6 GiB/64 GiB"]
    LLM["CT 114 llm-host\nVLAN 20 .104\n4c/20 GiB/100 GiB"]
    Rollback["VM 101 Frigate / VM 104 LLM\npowered off rollback only"]
    Proxmox --> HA
    Proxmox --> Frigate
    Proxmox --> Monitor
    Proxmox --> Docker
    Proxmox --> LLM
    Proxmox -.-> Rollback
    GPU["Shared Intel iGPU\nrenderD128 + card0"] --> Frigate
    GPU --> LLM
    VMBackup["VMs 100,102,103\ndaily 02:00; snapshot + ZSTD\nkeep 7 daily / 6 monthly"]
    CTBackup["CTs 111,114\ndaily 04:00; snapshot + ZSTD\ntmpdir /var/tmp; same retention"]
    OMV["omvnas / omv-backups\nNFS on 192.168.40.50"]
    HA --> VMBackup
    Monitor --> VMBackup
    Docker --> VMBackup
    Frigate --> CTBackup
    LLM --> CTBackup
    VMBackup --> OMV
    CTBackup --> OMV`
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
