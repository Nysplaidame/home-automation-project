export const diagrams = [
  {
    "id": "docker-host-service-placement",
    "title": "Docker-host Service Placement",
    "section": "infrastructure",
    "path": "infrastructure/docker-host-service-placement.mermaid",
    "summary": "Live application stacks, operational tooling, data services, storage, and backup boundaries.",
    "tags": [
      "docker",
      "services",
      "containers",
      "placement"
    ],
    "source": "flowchart TB\n    DockerHost[\"docker-host VM 103<br/>192.168.20.102<br/>6 GiB RAM · 64 GiB disk\"]\n    Compose[\"Compose stacks<br/>/opt/stacks/&lt;service&gt;/\"]\n    Firewall[\"DOCKER-USER policy<br/>management · LAN · HA · monitoring · Tailscale\"]\n    Observability[\"Operations<br/>Dozzle · Telegraf · Watchtower monitor-only\"]\n    BackupJob[\"Daily 03:45 app-data backup<br/>selected data + database dumps\"]\n    OMV[\"OMV backups/docker-host<br/>restore-smoke verified\"]\n\n    DockerHost --> Compose\n    DockerHost --> Firewall\n    DockerHost --> Observability\n    DockerHost --> BackupJob --> OMV\n\n    subgraph Navigation[\"Navigation and utility\"]\n        Homepage[\"Homepage<br/>3001 · central portal\"]\n        Mermaid[\"Mermaid Viewer<br/>8092 · canonical diagrams\"]\n        Gridfinity[\"Gridfinity Layout Tool<br/>8093\"]\n    end\n\n    subgraph Household[\"Household applications\"]\n        Immich[\"Immich<br/>2283 · OMV media\"]\n        Mealie[\"Mealie<br/>9925\"]\n        Grocy[\"Grocy<br/>9283\"]\n        Garden[\"GardenKeeper<br/>8090 API · 8091 UI\"]\n        Hub[\"Household Hub<br/>8100 UI · 8101 API\"]\n        Bambuddy[\"Bambuddy<br/>8000\"]\n        LiveSync[\"Obsidian LiveSync<br/>5984\"]\n    end\n\n    subgraph NetworkServices[\"Network and messaging\"]\n        AdGuard[\"AdGuard Home<br/>53 DNS · 8080 admin\"]\n        Tailscale[\"Tailscale host service<br/>four advertised /32 routes\"]\n        Ntfy[\"ntfy<br/>8085\"]\n        SearXNG[\"SearXNG<br/>8087\"]\n        Whoogle[\"Whoogle<br/>8088\"]\n    end\n\n    subgraph DataServices[\"Private application data services\"]\n        ImmichData[\"Immich PostgreSQL · Redis · ML\"]\n        GardenData[\"GardenKeeper PostgreSQL · Redis · worker\"]\n        HubData[\"Household Hub PostgreSQL · Redis · Qdrant · API\"]\n    end\n\n    Compose --> Navigation\n    Compose --> Household\n    Compose --> NetworkServices\n    Compose --> DataServices\n    Firewall --> Navigation\n    Firewall --> Household\n    Firewall --> NetworkServices\n    Household --> DataServices\n    Immich -->|\"library\"| OMV\n    BackupJob -.-> Mealie\n    BackupJob -.-> Grocy\n    BackupJob -.-> Garden\n    BackupJob -.-> LiveSync\n\n    Secrets[\"Secrets boundary<br/>live .env files and databases stay off Git\"]\n    Templates[\"Rebuildable templates<br/>configs/docker-host/\"]\n    Templates --> Compose\n    Secrets -.-> Compose\n\n    classDef host fill:#f4b860,stroke:#8a5a12,color:#241704\n    classDef app fill:#78b7d0,stroke:#245b70,color:#071e27\n    classDef data fill:#b8a1e3,stroke:#5b4391,color:#1b1230\n    classDef policy fill:#78c6a3,stroke:#276749,color:#08251a\n    class DockerHost host\n    class Homepage,Mermaid,Gridfinity,Immich,Mealie,Grocy,Garden,Hub,Bambuddy,LiveSync,AdGuard,Ntfy,SearXNG,Whoogle app\n    class ImmichData,GardenData,HubData,OMV data\n    class Firewall,BackupJob,Secrets,Templates policy"
  },
  {
    "id": "proxmox-guests-and-backups",
    "title": "Proxmox Guests and Backups",
    "section": "infrastructure",
    "path": "infrastructure/proxmox-guests-and-backups.mermaid",
    "summary": "Production guests, rollback guests, shared iGPU paths, and OMV backup schedules.",
    "tags": [
      "proxmox",
      "vm",
      "lxc",
      "backup",
      "gpu"
    ],
    "source": "flowchart TB\n    Proxmox[\"Proxmox VE 9<br/>MINISFORUM M1 Pro-125H<br/>192.168.10.10\"]\n\n    subgraph Production[\"Production guests\"]\n        HA[\"VM 100 · home-assistant<br/>VLAN 20 · .101<br/>2 vCPU · 6 GiB · 32 GiB\"]\n        Monitor[\"VM 102 · monitoring<br/>VLAN 60 · .10<br/>2 vCPU · 3 GiB · 32 GiB\"]\n        Docker[\"VM 103 · docker-host<br/>VLAN 20 · .102<br/>2 vCPU · 6 GiB · 64 GiB\"]\n        Frigate[\"CT 111 · frigate-nvr<br/>VLAN 30 · .20<br/>2 vCPU · 6 GiB · 32 GiB\"]\n        LLM[\"CT 114 · llm-host<br/>VLAN 20 · .104<br/>4 vCPU · 20 GiB · 100 GiB\"]\n    end\n\n    subgraph Rollback[\"Powered-off rollback guests\"]\n        OldFrigate[\"VM 101 · old Frigate\"]\n        OldLLM[\"VM 104 · old llm-host\"]\n    end\n\n    Proxmox --> Production\n    Proxmox -.-> Rollback\n\n    GPU[\"Shared Intel iGPU<br/>renderD128 + card0<br/>no PCI passthrough\"]\n    GPU --> Frigate\n    GPU --> LLM\n\n    VMBackup[\"VM backup job<br/>100 · 102 · 103<br/>daily 02:00 · snapshot · ZSTD\"]\n    CTBackup[\"LXC backup job<br/>111 · 114<br/>daily 04:00 · snapshot · ZSTD<br/>tmpdir /var/tmp\"]\n    Retention[\"Retention<br/>7 daily + 6 monthly\"]\n    OMV[\"OMV omv-backups NFS<br/>192.168.40.50\"]\n    Restore[\"Restore evidence<br/>guest jobs verified after tmpdir fix\"]\n\n    HA --> VMBackup\n    Monitor --> VMBackup\n    Docker --> VMBackup\n    Frigate --> CTBackup\n    LLM --> CTBackup\n    VMBackup --> Retention --> OMV\n    CTBackup --> Retention\n    OMV --> Restore\n\n    classDef guest fill:#78c6a3,stroke:#276749,color:#08251a\n    classDef rollback fill:#334155,stroke:#94a3b8,color:#e2e8f0,stroke-dasharray: 5 5\n    classDef backup fill:#b8a1e3,stroke:#5b4391,color:#1b1230\n    class HA,Monitor,Docker,Frigate,LLM guest\n    class OldFrigate,OldLLM rollback\n    class VMBackup,CTBackup,Retention,OMV,Restore backup"
  },
  {
    "id": "install-sequence",
    "title": "Install and Recovery Sequence",
    "section": "install",
    "path": "install/install-sequence.mermaid",
    "summary": "Fresh deployment order with validation and safety gates.",
    "tags": [
      "install",
      "recovery",
      "sequence"
    ],
    "source": "flowchart TB\n    Start[\"START-HERE<br/>read safety model and assumptions\"]\n    P00[\"00 Operator basics<br/>inventory, command contexts, secrets\"]\n    P01[\"01 Router/OpenWrt<br/>VLANs, DHCP, DNS, firewall, NTP, WireGuard fallback\"]\n    P02[\"02 Proxmox host<br/>install, bridge, VMs\"]\n    P03[\"03 Home Assistant<br/>HAOS, Mosquitto, ESPHome, VentSys base\"]\n    P04[\"04 Frigate<br/>CT 111, first-camera baseline\"]\n    P05[\"05 Docker-host<br/>Docker, Compose policy, Tailscale\"]\n    P05A[\"05A Local AI<br/>llm-host, llama.cpp, Wyoming voice\"]\n    P06[\"06 OMV NAS<br/>shares, users, storage health\"]\n    P07[\"07 Tier 1 apps<br/>AdGuard, Immich, Homepage, Dozzle\"]\n    P08[\"08 Tier 2 apps<br/>live/setup-pending + candidates\"]\n    P09[\"09 Tier 3/evaluate<br/>risk gates before deploy\"]\n    P10[\"10 Backups/monitoring/maintenance<br/>restore drills\"]\n    P11[\"11 Physical integrations<br/>VentSys, printers, cameras\"]\n    P12[\"12 Validation/troubleshooting<br/>end-to-end checks\"]\n\n    Start --> P00 --> P01 --> P02 --> P03 --> P04 --> P05 --> P05A --> P06 --> P07 --> P08 --> P09 --> P10 --> P11 --> P12\n\n    Gate1[\"Gate: router validation passes\"]\n    Gate2[\"Gate: backups configured before risky apps\"]\n    Gate3[\"Gate: safety behavior tested before unattended operation\"]\n\n    P01 --> Gate1\n    Gate1 --> P02\n    P05A --> P10\n    P07 --> Gate2\n    Gate2 --> P08\n    P11 --> Gate3\n    Gate3 --> P12"
  },
  {
    "id": "current-master-architecture",
    "title": "Logical Architecture",
    "section": "network",
    "path": "network/current-master-architecture.mermaid",
    "summary": "Current logical relationships across networking, compute, apps, storage, monitoring, and remote access.",
    "tags": [
      "architecture",
      "logical",
      "services",
      "network"
    ],
    "source": "flowchart TB\n    Operator[\"Trusted operator<br/>Management VLAN / mobile Tailscale\"]\n    Internet[\"Internet\"]\n    Router[\"GL-MT6000 OpenWrt<br/>192.168.10.1<br/>VLAN gateway, firewall, DHCP, DNS, NTP\"]\n    Switch[\"Zyxel GS1900-8HP<br/>192.168.10.12<br/>802.1Q trunk + PoE access ports\"]\n    Proxmox[\"Proxmox VE 9<br/>MINISFORUM M1 Pro-125H<br/>192.168.10.10\"]\n\n    Internet --- Router\n    Operator --> Router\n    Router ---|\"lan1 VLAN trunk\"| Proxmox\n    Router ---|\"lan3 VLANs 1/10/30/40\"| Switch\n\n    subgraph Compute[\"Production compute\"]\n        HA[\"VM 100 · Home Assistant OS<br/>192.168.20.101<br/>HTTPS 8123 · MQTT TLS 8883\"]\n        Monitoring[\"VM 102 · Monitoring<br/>192.168.60.10<br/>Grafana · Kuma · InfluxDB\"]\n        DockerHost[\"VM 103 · docker-host<br/>192.168.20.102<br/>Compose · Tailscale routing\"]\n        Frigate[\"CT 111 · Frigate NVR<br/>192.168.30.20<br/>OpenVINO · VA-API · HTTPS 8971\"]\n        LLMHost[\"CT 114 · local AI<br/>192.168.20.104<br/>llama.cpp · Open WebUI · Wyoming\"]\n        Rollback[\"VM 101 / VM 104<br/>powered-off rollback only\"]\n    end\n\n    Proxmox --- HA\n    Proxmox --- Monitoring\n    Proxmox --- DockerHost\n    Proxmox --- Frigate\n    Proxmox --- LLMHost\n    Proxmox -.-> Rollback\n\n    subgraph HouseholdApps[\"docker-host household applications\"]\n        Immich[\"Immich<br/>photos and videos\"]\n        Mealie[\"Mealie<br/>recipes and meal plans\"]\n        Grocy[\"Grocy<br/>stock and shopping\"]\n        Garden[\"GardenKeeper<br/>garden state and tasks\"]\n        Hub[\"Household Hub<br/>knowledge and research\"]\n        Bambuddy[\"Bambuddy<br/>Bambu P1S integration\"]\n    end\n\n    subgraph PlatformApps[\"docker-host platform and tools\"]\n        Homepage[\"Home Operations portal\"]\n        AdGuard[\"AdGuard Home\"]\n        Dozzle[\"Dozzle logs\"]\n        Search[\"SearXNG + Whoogle\"]\n        Ntfy[\"ntfy notifications\"]\n        LiveSync[\"Obsidian LiveSync\"]\n        Tools[\"Mermaid Viewer<br/>Gridfinity Layout Tool\"]\n        Watch[\"Watchtower monitor-only<br/>Telegraf metrics\"]\n    end\n\n    DockerHost --- HouseholdApps\n    DockerHost --- PlatformApps\n\n    subgraph Storage[\"Storage VLAN 40\"]\n        OMV[\"OpenMediaVault NAS<br/>192.168.40.50<br/>NFS · SMB · backups · CCTV · Immich\"]\n    end\n\n    Switch ---|\"port 8 · VLAN 40 access\"| OMV\n    OMV -->|\"HA backups\"| HA\n    OMV -->|\"recordings\"| Frigate\n    OMV -->|\"media + app backups\"| DockerHost\n    OMV -->|\"VM/CT backups\"| Proxmox\n\n    subgraph Physical[\"Physical integrations\"]\n        Camera[\"ANNKE C500<br/>192.168.30.21\"]\n        FutureCameras[\"Future exterior cameras<br/>192.168.30.22-24+\"]\n        Printer[\"Bambu P1S<br/>192.168.35.200\"]\n        VentSys[\"VentSys ESPHome fleet<br/>VLAN 50 · hardware adoption pending\"]\n    end\n\n    Switch -->|\"port 2 · VLAN 30 PoE\"| Camera\n    Switch -.-> FutureCameras\n    Camera -->|\"RTSP main/sub streams\"| Frigate\n    FutureCameras -.-> Frigate\n    Printer --> Bambuddy\n    VentSys -->|\"MQTT / ESPHome\"| HA\n\n    HA -->|\"Frigate integration\"| Frigate\n    HA -->|\"conversation + voice\"| LLMHost\n    DockerHost -->|\"chat + embeddings\"| LLMHost\n    Monitoring -.->|\"health + metrics\"| HA\n    Monitoring -.-> DockerHost\n    Monitoring -.-> Frigate\n    Monitoring -.-> LLMHost\n    Monitoring -.-> OMV\n\n    subgraph Remote[\"Remote access\"]\n        Tailnet[\"Tailscale tailnet<br/>daily access\"]\n        TailRouter[\"docker-host tailscale0<br/>100.94.122.18\"]\n        HostRoutes[\"Approved narrow routes<br/>HA .101 · Frigate .20 · OMV .50 · Monitoring .10\"]\n        WireGuard[\"WireGuard<br/>dormant split-tunnel fallback\"]\n    end\n\n    Operator --> Tailnet --> TailRouter\n    TailRouter --> DockerHost\n    TailRouter --> HostRoutes\n    HostRoutes --> HA\n    HostRoutes --> Frigate\n    HostRoutes --> OMV\n    HostRoutes --> Monitoring\n    Operator -.-> WireGuard -.-> Router\n\n    classDef edge fill:#f4b860,stroke:#8a5a12,color:#241704\n    classDef compute fill:#78c6a3,stroke:#276749,color:#08251a\n    classDef app fill:#78b7d0,stroke:#245b70,color:#071e27\n    classDef storage fill:#b8a1e3,stroke:#5b4391,color:#1b1230\n    classDef remote fill:#ef9a9a,stroke:#963f3f,color:#350b0b\n    class Router,Switch edge\n    class Proxmox,HA,Monitoring,DockerHost,Frigate,LLMHost compute\n    class Immich,Mealie,Grocy,Garden,Hub,Bambuddy,Homepage,AdGuard,Dozzle,Search,Ntfy,LiveSync,Tools,Watch app\n    class OMV storage\n    class Tailnet,TailRouter,HostRoutes,WireGuard remote"
  },
  {
    "id": "dns-ntp-flow",
    "title": "DNS and NTP Flow",
    "section": "network",
    "path": "network/dns-ntp-flow.mermaid",
    "summary": "Router authority, AdGuard filtering, public fallback, and restricted-device time flow.",
    "tags": [
      "dns",
      "ntp",
      "adguard"
    ],
    "source": "flowchart TB\n    Clients[\"LAN, management, automation, printer, guest clients\"]\n    Restricted[\"Restricted VLAN clients<br/>NVR, storage, IoT\"]\n    Router[\"OpenWrt router<br/>dnsmasq + DHCP + local DNS + NTP<br/>192.168.10.1\"]\n    AdGuard[\"AdGuard Home on docker-host<br/>192.168.20.102<br/>DNS filtering\"]\n    Quad9[\"Quad9 public DNS<br/>9.9.9.9 preferred fallback\"]\n    Cloudflare[\"Cloudflare public DNS<br/>secondary fallback\"]\n    HA[\"Home Assistant<br/>time source can point at router NTP\"]\n    ESPHome[\"ESPHome / VentSys devices<br/>router-derived time through HA and/or direct NTP when allowed\"]\n\n    Clients --> Router\n    Restricted --> Router\n    Router --> AdGuard\n    AdGuard --> Quad9\n    AdGuard --> Cloudflare\n    Router -.->|\"automatic public DNS fallback if AdGuard unavailable\"| Quad9\n    Router -.->|\"secondary fallback\"| Cloudflare\n\n    Router --> HA\n    Router --> ESPHome\n    HA -.->|\"manages ESPHome devices and schedules\"| ESPHome\n\n    LocalNames[\"Local hostnames and DHCP leases<br/>router remains authority\"]\n    Router --- LocalNames\n\n    Blocked[\"No Google DNS fallback<br/>no client DNS bypass when enforcement is enabled\"]\n    Clients -.->|\"policy\"| Blocked\n    Restricted -.->|\"policy\"| Blocked"
  },
  {
    "id": "physical-port-and-cabling",
    "title": "Physical Ports and Cabling",
    "section": "network",
    "path": "network/physical-port-and-cabling.mermaid",
    "summary": "Live router, Proxmox trunk, managed-switch ports, camera, NAS, and Wi-Fi attachment.",
    "tags": [
      "physical",
      "ports",
      "switch",
      "cabling"
    ],
    "source": "flowchart LR\n    Upstream[\"Upstream modem/router<br/>internet handoff\"] --> WAN\n\n    subgraph Router[\"GL-MT6000 OpenWrt · 192.168.10.1\"]\n        WAN[\"WAN<br/>upstream DHCP\"]\n        LAN1[\"lan1<br/>tagged Proxmox trunk\"]\n        LAN2[\"lan2<br/>management/recovery\"]\n        LAN3[\"lan3<br/>tagged switch trunk<br/>VLANs 1/10/30/40\"]\n        LAN4[\"lan4<br/>management/admin access\"]\n        LAN5[\"lan5<br/>LAN/recovery access\"]\n        WiFi[\"Wi-Fi<br/>HomeMain · HomeAdmin · HomePrinters<br/>HomeIoT · HomeGuest\"]\n    end\n\n    LAN1 --> Proxmox[\"MINISFORUM Proxmox host<br/>192.168.10.10<br/>VLAN-aware guest bridge\"]\n    LAN3 --> SW1\n\n    subgraph Switch[\"Zyxel GS1900-8HP · 192.168.10.12\"]\n        SW1[\"Port 1<br/>router trunk\"]\n        SW2[\"Port 2<br/>PoE · VLAN 30 access\"]\n        SW3[\"Ports 3-7<br/>future PoE cameras\"]\n        SW8[\"Port 8<br/>VLAN 40 access\"]\n    end\n\n    SW2 --> Camera[\"ANNKE C500 cam-01<br/>192.168.30.21\"]\n    SW3 -.-> FutureCameras[\"Future exterior cameras<br/>VLAN 30\"]\n    SW8 --> OMV[\"OpenMediaVault NAS<br/>192.168.40.50\"]\n    WiFi --> Admin[\"Admin workstation<br/>HomeAdmin · VLAN 10\"]\n    WiFi --> Users[\"Household devices<br/>HomeMain · VLAN 1\"]\n    WiFi --> Printer[\"Bambu P1S<br/>HomePrinters · VLAN 35\"]\n    WiFi -.-> VentSys[\"Future VentSys devices<br/>HomeIoT · VLAN 50\"]\n\n    Proxmox --> HA[\"VM 100 HA · VLAN 20\"]\n    Proxmox --> Monitor[\"VM 102 monitoring · VLAN 60\"]\n    Proxmox --> Docker[\"VM 103 docker-host · VLAN 20\"]\n    Proxmox --> Frigate[\"CT 111 Frigate · VLAN 30\"]\n    Proxmox --> LLM[\"CT 114 local AI · VLAN 20\"]\n\n    classDef live fill:#78c6a3,stroke:#276749,color:#08251a\n    classDef future fill:#334155,stroke:#94a3b8,color:#e2e8f0,stroke-dasharray: 5 5\n    class WAN,LAN1,LAN3,WiFi,Proxmox,SW1,SW2,SW8,Camera,OMV,Admin,Users,Printer,HA,Monitor,Docker,Frigate,LLM live\n    class SW3,FutureCameras,VentSys future"
  },
  {
    "id": "remote-access-flow",
    "title": "Remote Access Flow",
    "section": "network",
    "path": "network/remote-access-flow.mermaid",
    "summary": "Tailscale daily access, approved host routes, and dormant WireGuard fallback.",
    "tags": [
      "tailscale",
      "wireguard",
      "remote"
    ],
    "source": "flowchart LR\n    RemoteUser[\"Remote operator<br/>laptop or phone\"]\n    Tailnet[\"Tailscale tailnet<br/>daily remote layer\"]\n    DockerHost[\"docker-host VM 103<br/>Tailscale node<br/>192.168.20.102\"]\n    HA[\"Home Assistant<br/>192.168.20.101/32\"]\n    Frigate[\"Frigate HTTPS<br/>192.168.30.20/32\"]\n    OMV[\"OMV NAS<br/>192.168.40.50/32\"]\n    Monitoring[\"Grafana + Kuma<br/>192.168.60.10/32\"]\n    DockerServices[\"docker-host services<br/>MagicDNS / Tailscale identity\"]\n    Router[\"OpenWrt router<br/>WireGuard server\"]\n    WGClient[\"WireGuard client<br/>dormant fallback\"]\n\n    RemoteUser --> Tailnet\n    Tailnet --> DockerHost\n    DockerHost --> DockerServices\n    DockerHost -.->|\"advertised host route\"| HA\n    DockerHost -.->|\"HTTPS 8971 host route\"| Frigate\n    DockerHost -.->|\"advertised host route\"| OMV\n    DockerHost -.->|\"ports 3000/3001 host route\"| Monitoring\n\n    RemoteUser -.->|\"only if Tailscale unavailable\"| WGClient\n    WGClient -.->|\"split tunnel fallback\"| Router\n    Router -.->|\"limited fallback access\"| HA\n    Router -.->|\"OMV host access only where needed\"| OMV\n\n    Blocked1[\"No broad VLAN 40 route\"]\n    Blocked2[\"No daily WireGuard dependency\"]\n    Blocked3[\"No direct public app exposure by default\"]\n\n    DockerHost -.->|\"blocked by policy\"| Blocked1\n    Router -.->|\"blocked by policy\"| Blocked2\n    DockerServices -.->|\"blocked by policy\"| Blocked3\n\n    classDef allowed fill:#e8f7ee,stroke:#2f855a,stroke-width:1px\n    classDef fallback fill:#fff7e6,stroke:#b7791f,stroke-width:1px\n    classDef blocked fill:#ffe8e8,stroke:#c53030,stroke-width:1px\n\n    class RemoteUser,Tailnet,DockerHost,HA,Frigate,OMV,Monitoring,DockerServices allowed\n    class Router,WGClient fallback\n    class Blocked1,Blocked2,Blocked3 blocked"
  },
  {
    "id": "security-access-flow",
    "title": "Security Access Flow",
    "section": "network",
    "path": "network/security-access-flow.mermaid",
    "summary": "Zone policy, service authentication, host firewalls, and deliberately blocked paths.",
    "tags": [
      "security",
      "firewall",
      "acl"
    ],
    "source": "flowchart TB\n    User[\"Trusted user devices<br/>VLAN 1\"]\n    Router[\"OpenWrt firewall<br/>zone policy and DHCP/DNS\"]\n    Mgmt[\"Management<br/>VLAN 10\"]\n    Automation[\"Automation<br/>VLAN 20\"]\n    NVR[\"NVR<br/>VLAN 30\"]\n    Printers[\"Printers<br/>VLAN 35\"]\n    Storage[\"Storage<br/>VLAN 40\"]\n    IoT[\"IoT sensors<br/>VLAN 50\"]\n    Monitoring[\"Monitoring<br/>VLAN 60\"]\n    DMZ[\"DMZ<br/>VLAN 70\"]\n    Guest[\"Guest<br/>VLAN 99\"]\n    Tailscale[\"Tailscale ACLs<br/>daily remote\"]\n    HostFW[\"Host firewalls / UFW<br/>Linux services\"]\n    ServiceAuth[\"Service auth<br/>HA 2FA, app logins, tokens\"]\n    LocalAI[\"llm-host CT 114<br/>llama.cpp + Wyoming<br/>approved HA entities only\"]\n\n    User --> Router\n    Router --> Mgmt\n    Router --> Automation\n    Router --> NVR\n    Router --> Printers\n    Router --> Storage\n    Router --> IoT\n    Router --> Monitoring\n    Router --> DMZ\n    Router --> Guest\n\n    Tailscale --> Automation\n    Tailscale --> Storage\n    Automation --> HostFW\n    Automation --> LocalAI\n    Storage --> HostFW\n    HostFW --> ServiceAuth\n    LocalAI --> ServiceAuth\n\n    Automation -.->|\"MQTT / ESPHome only\"| IoT\n    NVR -.->|\"camera streams only\"| Printers\n    NVR -.->|\"recording/archive only\"| Storage\n    Monitoring -.->|\"health checks and metrics only\"| Automation\n    Monitoring -.->|\"AI service checks only\"| LocalAI\n    Monitoring -.->|\"health checks and metrics only\"| NVR\n    Monitoring -.->|\"health checks and metrics only\"| Storage\n\n    GuestX[\"Guest cannot reach internal VLANs\"]\n    IoTX[\"IoT cannot initiate broad access\"]\n    StorageX[\"Storage has no broad internet\"]\n    NVRX[\"NVR has no broad internet\"]\n    PrinterX[\"Printers limited to required OTA/cloud paths\"]\n\n    Guest -.->|\"blocked\"| GuestX\n    IoT -.->|\"blocked\"| IoTX\n    Storage -.->|\"blocked\"| StorageX\n    NVR -.->|\"blocked\"| NVRX\n    Printers -.->|\"limited\"| PrinterX"
  },
  {
    "id": "vlan_architecture_clean",
    "title": "VLAN Architecture",
    "section": "network",
    "path": "network/vlan_architecture_clean.mermaid",
    "summary": "All network segments, subnets, core hosts, physical trunks, and remote-access placement.",
    "tags": [
      "vlan",
      "subnet",
      "router"
    ],
    "source": "flowchart TB\n    Internet[\"Internet\"]\n    Router[\"OpenWrt router<br/>GL-MT6000<br/>192.168.10.1<br/>DHCP, local DNS, firewall, NTP\"]\n    Internet --- Router\n\n    subgraph Ports[\"Physical ports\"]\n        LAN1[\"LAN1 trunk<br/>Proxmox VLAN trunk\"]\n        LAN2[\"LAN2 management access\"]\n        LAN3[\"LAN3 managed switch trunk<br/>VLANs 1,10,30,40 tagged\"]\n        LAN4[\"LAN4 management/admin PC<br/>VLAN 10 untagged\"]\n        LAN5[\"LAN5 LAN PC / recovery<br/>VLAN 1 untagged\"]\n        EdgeSwitch[\"Zyxel GS1900-8HP<br/>switch mgmt VLAN 10<br/>camera/NAS/extender access ports\"]\n        WiFi[\"Router Wi-Fi SSIDs\"]\n    end\n\n    Router --- LAN1\n    Router --- LAN2\n    Router --- LAN3\n    Router --- LAN4\n    Router --- LAN5\n    Router --- WiFi\n    LAN3 --- EdgeSwitch\n\n    subgraph VLANs[\"Current VLAN and subnet plan\"]\n        V1[\"VLAN 1 LAN<br/>192.168.1.0/24<br/>trusted users\"]\n        V10[\"VLAN 10 Management<br/>192.168.10.0/24<br/>router, Proxmox\"]\n        V20[\"VLAN 20 Automation<br/>192.168.20.0/24<br/>Home Assistant, docker-host, llm-host\"]\n        V30[\"VLAN 30 NVR<br/>192.168.30.0/24<br/>Frigate, cameras\"]\n        V35[\"VLAN 35 Printers<br/>192.168.35.0/24<br/>Bambu P1S, future printers\"]\n        V40[\"VLAN 40 Storage<br/>192.168.40.0/24<br/>OMV NAS\"]\n        V50[\"VLAN 50 IoT<br/>192.168.50.0/24<br/>ESPHome and VentSys devices\"]\n        V60[\"VLAN 60 Monitoring<br/>192.168.60.0/24<br/>Kuma, Grafana, InfluxDB\"]\n        V70[\"VLAN 70 DMZ<br/>192.168.70.0/24<br/>reserved controlled public edge\"]\n        V99[\"VLAN 99 Guest<br/>192.168.99.0/24<br/>guest Wi-Fi\"]\n    end\n\n    Router --- V1\n    Router --- V10\n    Router --- V20\n    Router --- V30\n    Router --- V35\n    Router --- V40\n    Router --- V50\n    Router --- V60\n    Router --- V70\n    Router --- V99\n\n    subgraph Core[\"Core hosts\"]\n        Proxmox[\"Proxmox host<br/>192.168.10.10\"]\n        HA[\"Home Assistant VM 100<br/>192.168.20.101\"]\n        Frigate[\"Frigate CT 111<br/>192.168.30.20\"]\n        DockerHost[\"docker-host VM 103<br/>192.168.20.102<br/>Compose apps + Tailscale subnet router\"]\n        LLMHost[\"llm-host CT 114<br/>192.168.20.104<br/>local AI inference\"]\n        OMV[\"OMV NAS<br/>192.168.40.50\"]\n    end\n\n    V10 --- Proxmox\n    Proxmox --- HA\n    Proxmox --- Frigate\n    Proxmox --- DockerHost\n    Proxmox --- LLMHost\n    V40 --- OMV\n\n    subgraph Remote[\"Remote access\"]\n        Tailnet[\"Tailscale tailnet<br/>daily access\"]\n        WireGuard[\"WireGuard fallback<br/>dormant split tunnel\"]\n    end\n\n    Tailnet --> DockerHost\n    DockerHost -.->|\"host route\"| HA\n    DockerHost -.->|\"host route\"| Frigate\n    DockerHost -.->|\"host route\"| OMV\n    DockerHost -.->|\"host route\"| V60\n    WireGuard -.->|\"fallback only; no broad storage subnet\"| Router\n\n    classDef router fill:#f8f3d4,stroke:#8a6d00,stroke-width:2px\n    classDef vlan fill:#edf7ff,stroke:#2b6cb0,stroke-width:1px\n    classDef host fill:#eef8ee,stroke:#2f855a,stroke-width:1px\n    classDef remote fill:#fff0f6,stroke:#b83280,stroke-width:1px\n\n    class Router router\n    class V1,V10,V20,V30,V35,V40,V50,V60,V70,V99 vlan\n    class Proxmox,HA,Frigate,DockerHost,OMV host\n    class Tailnet,WireGuard remote"
  },
  {
    "id": "storage-and-backup-flow",
    "title": "Storage and Backup Flow",
    "section": "storage",
    "path": "storage/storage-and-backup-flow.mermaid",
    "summary": "Live OMV-backed recordings, media, guest backups, application data, and restore verification.",
    "tags": [
      "storage",
      "backup",
      "omv",
      "restore"
    ],
    "source": "flowchart LR\n    HA[\"Home Assistant<br/>VM 100\"]\n    Frigate[\"Frigate<br/>CT 111\"]\n    DockerHost[\"docker-host<br/>VM 103\"]\n    Immich[\"Immich<br/>on docker-host\"]\n    Apps[\"Mealie / Grocy / LiveSync / GardenKeeper<br/>on docker-host\"]\n    OMV[\"OMV NAS<br/>192.168.40.50<br/>NFS/SMB shares\"]\n    Proxmox[\"Proxmox host<br/>omv-backups NFS storage\"]\n    Vault[\"Project vault<br/>Obsidian repo\"]\n    Offsite[\"Future offsite copy<br/>manual or automated\"]\n\n    HA -->|\"daily HA backups<br/>nas_backups\"| OMV\n    Frigate -->|\"live NFS recordings<br/>Proxmox host mount + CT bind mount\"| OMV\n    Immich -->|\"library and upload storage\"| OMV\n    Apps -->|\"daily 03:45 data/dump copy<br/>backups/docker-host\"| OMV\n    DockerHost -->|\"templates and stack configs<br/>Git + app-data plan\"| Apps\n    Proxmox -->|\"VM/CT vzdump backups<br/>7 daily + 6 monthly\"| OMV\n    Vault -.->|\"planned rsync/robocopy backup\"| OMV\n    OMV -.->|\"periodic copy after restore plan exists\"| Offsite\n\n    SMART[\"OMV SMART monitoring<br/>disk health alerts\"]\n    Restore[\"Restore drills<br/>HA, Proxmox guests, app data, router configs\"]\n\n    OMV --> SMART\n    OMV --> Restore\n    Proxmox --> Restore"
  },
  {
    "id": "ventsys-control-and-safety-flow",
    "title": "VentSys Control and Safety",
    "section": "ventsys",
    "path": "ventsys/ventsys-control-and-safety-flow.mermaid",
    "summary": "Control, telemetry, airflow, emergency actions, and fail-safe relationships.",
    "tags": [
      "ventsys",
      "safety",
      "mqtt",
      "esphome"
    ],
    "source": "flowchart TB\n    HA[\"Home Assistant<br/>VM 100<br/>automation authority\"]\n    MQTT[\"Mosquitto MQTT<br/>TLS 8883 target\"]\n    ESPHome[\"ESPHome add-on<br/>firmware and adoption\"]\n\n    subgraph Devices[\"VentSys devices on VLAN 50\"]\n        Fan[\"Fan controllers<br/>inline and booth fans\"]\n        Sensors[\"Sensor arrays<br/>temperature, humidity, VOC, smoke, pressure\"]\n        Valves[\"Valve controllers<br/>branch, enclosure, 360-degree valves\"]\n        Plugs[\"Smart plugs<br/>printer power cutoff\"]\n    end\n\n    subgraph Physical[\"Physical airflow\"]\n        FDM[\"FDM enclosure\"]\n        SLA[\"SLA enclosure\"]\n        Booth[\"Spray booth\"]\n        Duct[\"PrintAirPipe ducting\"]\n        Exhaust[\"Inline fan to window exhaust\"]\n    end\n\n    HA --> MQTT\n    ESPHome --> Devices\n    Devices --> MQTT\n    MQTT --> HA\n\n    Sensors --> HA\n    HA --> Fan\n    HA --> Valves\n    HA --> Plugs\n\n    FDM --> Duct\n    SLA --> Duct\n    Booth --> Duct\n    Duct --> Exhaust\n    Fan --> Exhaust\n    Valves --> Duct\n    Sensors --> FDM\n    Sensors --> SLA\n    Sensors --> Booth\n\n    subgraph Safety[\"Safety behavior\"]\n        Emergency[\"Emergency shutdown sequence\"]\n        Manual[\"Manual override path\"]\n        Failsafe[\"Device failsafe defaults<br/>safe fan/valve behavior on HA loss\"]\n    end\n\n    Sensors -.->|\"alarm threshold\"| Emergency\n    HA -.->|\"automation trigger\"| Emergency\n    Emergency --> Plugs\n    Emergency --> Fan\n    Emergency --> Valves\n    Manual --> Fan\n    Manual --> Valves\n    Devices -.->|\"network or HA loss\"| Failsafe"
  }
];
