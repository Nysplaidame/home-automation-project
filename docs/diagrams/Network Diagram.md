```mermaid
graph TB
    Internet([Internet]) --> Router[GL.iNet GL-MT6000<br/>OpenWrt<br/>192.168.1.1]
    
    %% VLANs
    Router --> VLAN10[VLAN 10 - Management<br/>192.168.10.0/24]
    Router --> VLAN20[VLAN 20 - Automation<br/>192.168.20.0/24]
    Router --> VLAN30[VLAN 30 - CCTV<br/>192.168.30.0/24]
    Router --> VLAN40[VLAN 40 - Storage<br/>192.168.40.0/24]
    Router --> VLAN50[VLAN 50 - IoT Sensors<br/>192.168.50.0/24]
    
    %% Management VLAN Internet Access
    VLAN10 --> Admin[Admin Laptop<br/>192.168.10.10]
    VLAN10 --> Mobile[Mobile Devices<br/>192.168.10.20-30]
    
    %% Automation VLAN Controlled Internet
    VLAN20 --> Proxmox[MINIX Mini PC<br/>Proxmox Host<br/>192.168.20.100]
    Proxmox --> HomeAssistant[Home Assistant VM<br/>192.168.20.101]
    Proxmox --> Frigate[Frigate NVR VM<br/>192.168.20.102]
    
    %% CCTV VLAN No Internet
    VLAN30 --> POESwitch[POE Switch<br/>192.168.30.10]
    POESwitch --> Cam1[Camera 1<br/>192.168.30.21]
    POESwitch --> Cam2[Camera 2<br/>192.168.30.22]
    POESwitch --> Cam3[Camera 3<br/>192.168.30.23]
    POESwitch --> Cam4[Camera 4<br/>192.168.30.24]
    
    %% Storage VLAN No Internet
    VLAN40 --> RaspberryPi[Raspberry Pi NAS<br/>192.168.40.50]
    
    %% IoT Sensors VLAN No Internet
    VLAN50 --> TempSensor1[Temp/Humidity 1<br/>192.168.50.31]
    VLAN50 --> TempSensor2[Temp/Humidity 2<br/>192.168.50.32]
    VLAN50 --> SmokeSensor1[Smoke Detector 1<br/>192.168.50.41]
    VLAN50 --> SmokeSensor2[Smoke Detector 2<br/>192.168.50.42]
    VLAN50 --> VOCSensor1[VOC Sensor 1<br/>192.168.50.51]
    VLAN50 --> VOCSensor2[VOC Sensor 2<br/>192.168.50.52]
    VLAN50 --> PressureSensor1[Pressure Sensor 1<br/>192.168.50.61]
    VLAN50 --> PressureSensor2[Pressure Sensor 2<br/>192.168.50.62]
    VLAN50 --> SmartPlug1[Smart Plug SLA<br/>192.168.50.71]
    VLAN50 --> SmartPlug2[Smart Plug FDM<br/>192.168.50.72]
    VLAN50 --> ServoController[Servo Controller<br/>192.168.50.80]
    
    %% Firewall Rules Display
    Router --> FirewallRules[Firewall Rules:<br/>VLAN 20: Admin Full Internet<br/>VLAN 20: HA Controlled Internet<br/>VLAN 30: No Internet<br/>VLAN 40: No Internet<br/>VLAN 50: No Internet]
    
    %% Inter-VLAN Communication
    HomeAssistant -.->|Read Camera Feeds| VLAN30
    HomeAssistant -.->|Read/Write Storage| VLAN40
    HomeAssistant -.->|Control All Sensors| VLAN50
    Frigate -.->|Store Footage| RaspberryPi
    Admin -.->|Management Access| VLAN30
    Admin -.->|Management Access| VLAN40
    Admin -.->|Management Access| VLAN50
    
    %% Remote Access Data Flow
    Router --> VPN[WireGuard VPN<br/>Secure Remote Access]
    VPN -.->|Encrypted Tunnel| RemoteAccess[Remote Mobile<br/>HA App + Camera Access]
    RemoteAccess -.->|Via HA Dashboard| CameraFeeds[Camera Feeds<br/>Through Frigate]
    
    %% Styling
    classDef vlan fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    classDef device fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef critical fill:#ffebee,stroke:#b71c1c,stroke-width:3px
    classDef security fill:#e8f5e8,stroke:#2e7d32,stroke-width:2px
    
    class VLAN20,VLAN30,VLAN40,VLAN50 vlan
    class HomeAssistant,Frigate,RaspberryPi device
    class SmartPlug1,SmartPlug2,SmartPlug3,SmokeSensor1,SmokeSensor2,BambuP1S critical
    class VPN,RemoteAccess,FirewallRules,CameraFeeds security
```


## Document References & Architecture  
- **Architecture Decision:** [[docs/decisions/001-network-architecture]] - Design rationale  
- **Firewall Implementation:** [[configs/openwrt/firewall-config.sh]] - Security rules for this topology
- **Project Context:** [[docs/session-states/session_state_20250909]] - Original design session

## Configuration Dependencies
This network diagram drives the configuration requirements for:
- [[configs/openwrt/vlan-config.conf]] - VLAN interface setup (pending)
- [[configs/openwrt/main-config.conf]] - Router configuration (pending)
- [[configs/home-assistant/configuration.yaml]] - HA VLAN 20 integration (pending)  
- [[configs/frigate/config.yml]] - NVR VLAN 30 configuration (pending)
- [[configs/esphome/printairpipe-controller.yaml]] - IoT VLAN 50 sensors (pending)

## Implementation Status
- ✅ **Network Architecture** - 4-VLAN design complete per [[docs/decisions/001-network-architecture]]
- ✅ **Security Rules** - Firewall policies defined in [[configs/openwrt/firewall-config.sh]]
- 🚧 **Router Setup** - VLAN interfaces pending configuration  
- 🚧 **Device Assignment** - IP allocation per diagram specifications pending

**Next Implementation:** Configure VLAN interfaces using [[configs/openwrt/vlan-config.conf]]