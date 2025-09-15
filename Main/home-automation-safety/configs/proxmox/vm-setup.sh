# Proxmox VM Configuration - Placeholder
# Virtual machine setup scripts will be added here


#
# Architecture Context: [[docs/decisions/001-network-architecture]]
# Network Assignment: VLAN 20 (Automation) - 192.168.20.100
# Project Status: [[Main/Home Automation/Readme]]
# Virtualization: MINIX Mini PC hosting Home Assistant + Frigate VMs
#
# Related Documents:
# - [[docs/diagrams/Network Diagram - Revised]] - VM network topology
# - [[configs/openwrt/firewall-config.sh]] - Network access rules for VMs
# - [[configs/home-assistant/configuration.yaml]] - VM 192.168.20.101 config
# - [[configs/frigate/config.yml]] - VM 192.168.20.102 config  
#
# Planned VM Configuration:
# - Proxmox Host: 192.168.20.100 (VLAN 20 - Automation)
# - Home Assistant VM: 192.168.20.101 (controlled internet access)
# - Frigate NVR VM: 192.168.20.102 (no internet, storage access only)  
#
# Hardware: MINIX Mini PC (i3-N350, 16GB RAM, 512GB SSD)
# Network Bridge: VLAN 20 interface for VM networking
# Storage: Local SSD + NAS integration via VLAN 40