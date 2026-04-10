#!/bin/bash
# Proxmox VM Creation Script
# Host: 192.168.10.10 — VLAN 10 (Management)
# Run from Proxmox shell after completing proxmox_setup_guide.md Phases A-C
#
# Creates:
#   VM 100 — Home Assistant OS    (VLAN 20, 192.168.20.101)
#   VM 101 — Frigate NVR Debian   (VLAN 30, 192.168.30.20)
#
# Prerequisites:
#   - HAOS qcow2 image imported per proxmox_setup_guide.md Phase D
#   - Debian 12 ISO at /var/lib/vz/template/iso/debian-12-netinst.iso
#   - EFI vars template at /usr/share/OVMF/OVMF_VARS.fd (part of ovmf pkg)

set -e
set -u

STORAGE="local-lvm"
ISO_STORAGE="local"

echo "=== Proxmox VM Creation ==="
echo "Creating VM 100 (Home Assistant) and VM 101 (Frigate NVR)"
echo ""

# ============================================================================
# VM 100 — Home Assistant OS
# ============================================================================

echo "--- Creating VM 100: Home Assistant OS ---"

# Check HAOS image was imported
if ! pvesm list local-lvm | grep -q "vm-100-disk"; then
    echo "ERROR: HAOS disk image not yet imported to local-lvm."
    echo "Follow proxmox_setup_guide.md Phase D to import the qcow2 first, then re-run."
    exit 1
fi

# Create VM shell
qm create 100 \
    --name home-assistant \
    --machine q35 \
    --bios ovmf \
    --ostype l26 \
    --sockets 1 \
    --cores 2 \
    --cpu host \
    --memory 4096 \
    --balloon 0 \
    --scsihw virtio-scsi-single \
    --boot order=scsi0 \
    --onboot 1 \
    --startup order=1 \
    --tablet 0 \
    --vga serial0 \
    --serial0 socket \
    --net0 virtio,bridge=vmbr0,tag=20

# Add EFI disk
# FIX #29: `:1` allocates a 1GB LVM volume for the EFI vars disk, which is
# wasteful on thin-provisioned storage — the EFI vars image is only ~128KB.
# The correct allocation is `4M` (4 mebibytes), which is what the Proxmox GUI
# uses by default and what the efitype=4m parameter implies. No functional
# breakage from using `:1`, but it reserves ~8000x more space than necessary.
qm set 100 \
    --efidisk0 ${STORAGE}:4M,efitype=4m,pre-enrolled-keys=0

# The HAOS disk was imported as vm-100-disk-1 by the qm importdisk command
# in proxmox_setup_guide.md. Attach it here with performance tuning.
qm set 100 \
    --scsi0 ${STORAGE}:vm-100-disk-1,cache=writeback,discard=on,ssd=1

echo "✓ VM 100 created"
echo ""
echo "NOTE: After first boot, note the net0 MAC address:"
echo "  qm config 100 | grep net0"
echo "Then add it to configs/openwrt/dhcp-config.conf home-assistant entry."
echo ""

# ============================================================================
# VM 101 — Frigate NVR (Debian 12)
# ============================================================================

echo "--- Creating VM 101: Frigate NVR (Debian 12) ---"

# Check Debian ISO exists
DEBIAN_ISO=$(ls /var/lib/vz/template/iso/debian-12*.iso 2>/dev/null | head -1)
if [ -z "$DEBIAN_ISO" ]; then
    echo "ERROR: No Debian 12 ISO found at /var/lib/vz/template/iso/"
    echo "Download from https://www.debian.org/distrib/netinst"
    echo "  wget -O /var/lib/vz/template/iso/debian-12-netinst-amd64.iso https://cdimage.debian.org/debian-cd/current/amd64/iso-cd/debian-12-netinst-amd64.iso"
    exit 1
fi
DEBIAN_ISO_NAME=$(basename "$DEBIAN_ISO")
echo "Using ISO: $DEBIAN_ISO_NAME"

qm create 101 \
    --name frigate-nvr \
    --machine q35 \
    --bios ovmf \
    --ostype l26 \
    --sockets 1 \
    --cores 2 \
    --cpu host \
    --memory 4096 \
    --balloon 0 \
    --scsihw virtio-scsi-single \
    --boot order=scsi0 \
    --onboot 1 \
    --startup order=2 \
    --tablet 0 \
    --net0 virtio,bridge=vmbr0,tag=30

# EFI disk — same fix as VM 100
qm set 101 \
    --efidisk0 ${STORAGE}:4M,efitype=4m,pre-enrolled-keys=0

# 64GB system disk (Debian + Docker + local Frigate storage)
qm set 101 \
    --scsi0 ${STORAGE}:64,cache=writeback,discard=on,ssd=1

# Attach ISO for installation
qm set 101 \
    --ide2 ${ISO_STORAGE}:iso/${DEBIAN_ISO_NAME},media=cdrom

echo "✓ VM 101 created"
echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo "============================================"
echo "VM CREATION COMPLETE"
echo "============================================"
echo ""
qm list | grep -E "(VMID|100|101)"
echo ""
echo "NEXT STEPS:"
echo ""
echo "VM 100 — Home Assistant:"
echo "  1. Start: qm start 100"
echo "  2. Monitor boot via console: qm terminal 100"
echo "  3. Follow ha_vm_setup_guide.md from Phase 1"
echo "  4. Note MAC: qm config 100 | grep net0"
echo ""
echo "VM 101 — Frigate NVR:"
echo "  1. Start: qm start 101"
echo "  2. Open console in Proxmox web UI to complete Debian install"
echo "  3. Follow frigate_vm_setup_guide.md from Phase 2"
echo "  4. Note MAC: qm config 101 | grep net0"
echo "  5. Remove ISO after install: qm set 101 --delete ide2"
echo ""
echo "IMPORTANT: After both VMs are up, note their MAC addresses:"
echo "  qm config 100 | grep net0"
echo "  qm config 101 | grep net0"
echo "Add the MACs to configs/openwrt/dhcp-config.conf (home-assistant and"
echo "frigate-nvr host entries), then re-apply the DHCP config section to the"
echo "router per Phase 3 of router_setup_complete.md for static reservations."
echo ""
echo "iGPU PASSTHROUGH for Frigate (after confirming IOMMU active):"
echo "  See frigate_vm_setup_guide.md Phase 6"
