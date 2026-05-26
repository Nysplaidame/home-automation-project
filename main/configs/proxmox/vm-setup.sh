#!/bin/bash
# Proxmox VM Creation Script
# Host: 192.168.10.10 — VLAN 10 (Management)
# Run from Proxmox shell after completing proxmox_setup_guide.md Phases A-C
#
# Creates:
#   VM 100 — Home Assistant OS    (VLAN 20, 192.168.20.101)
#   VM 101 — Frigate NVR Debian   (VLAN 30, 192.168.30.20)
#   VM 103 — Docker host Debian   (VLAN 20, 192.168.20.102)
#
# A6-7 fix: VM 103 added (was missing — audit finding #7).
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
echo "Creating VM 100 (Home Assistant), VM 101 (Frigate NVR), VM 103 (Docker host)"
echo ""

# ============================================================================
# VM 100 — Home Assistant OS
# ============================================================================

echo "--- Creating VM 100: Home Assistant OS ---"

# Create VM shell first if it does not already exist.
if qm status 100 >/dev/null 2>&1; then
    echo "VM 100 already exists - reusing existing shell."
else
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
fi

# Import HAOS disk if needed and attach the imported unused disk before adding
# the EFI vars disk. This avoids accidentally attaching the tiny EFI volume as
# scsi0 on reruns or fresh installs.
if qm config 100 | grep -q '^scsi0:'; then
    echo "VM 100 scsi0 disk already attached - leaving existing disk in place."
else
    HAOS_DISK=$(qm config 100 | awk -F': ' '/^unused[0-9]+: local-lvm:vm-100-disk/ && $0 !~ /size=4M/ {print $2}' | cut -d',' -f1 | sed 's/^local-lvm://' | tail -1)
    if [ -z "$HAOS_DISK" ]; then
        HAOS_IMAGE=$(ls /var/lib/vz/template/iso/haos_ova-*.qcow2 2>/dev/null | head -1)
        if [ -z "$HAOS_IMAGE" ]; then
            echo "ERROR: No HAOS qcow2 found at /var/lib/vz/template/iso/haos_ova-*.qcow2"
            echo "Download/extract HAOS per proxmox_setup_guide.md Phase D1, then re-run."
            exit 1
        fi
        echo "Importing HAOS image: $(basename "$HAOS_IMAGE")"
        qm importdisk 100 "$HAOS_IMAGE" local-lvm --format raw
        HAOS_DISK=$(qm config 100 | awk -F': ' '/^unused[0-9]+: local-lvm:vm-100-disk/ && $0 !~ /size=4M/ {print $2}' | cut -d',' -f1 | sed 's/^local-lvm://' | tail -1)
    fi

    if [ -z "$HAOS_DISK" ]; then
        echo "ERROR: Could not find imported HAOS disk as an unused VM 100 disk."
        exit 1
    fi
    qm set 100 \
        --scsi0 ${STORAGE}:${HAOS_DISK},cache=writeback,discard=on,ssd=1
fi

# Add EFI disk if needed.
# Proxmox 9's `qm set --efidisk0` CLI accepts a numeric allocation here and
# rounds it to the `efitype=4m` vars disk size. A literal `local-lvm:4M` is
# rejected as an invalid volume name.
if qm config 100 | grep -q '^efidisk0:'; then
    echo "VM 100 EFI disk already present - leaving existing EFI disk in place."
else
    qm set 100 \
        --efidisk0 ${STORAGE}:1,efitype=4m,pre-enrolled-keys=0
fi

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
    --efidisk0 ${STORAGE}:1,efitype=4m,pre-enrolled-keys=0

# 64GB system disk (Debian + Docker + local Frigate storage)
qm set 101 \
    --scsi0 ${STORAGE}:64,cache=writeback,discard=on,ssd=1

# Attach ISO for installation
qm set 101 \
    --ide2 ${ISO_STORAGE}:iso/${DEBIAN_ISO_NAME},media=cdrom

echo "✓ VM 101 created"
echo ""

# ============================================================================
# VM 103 — Docker host (Debian)
# A6-7 fix: VM 103 was missing from this script (audit finding #7).
# Central trusted Docker host for lightweight internal app containers.
# Runs on VLAN 20 (Automation / trusted app services) at 192.168.20.102.
# First workload: Bambuddy under /opt/stacks/bambuddy.
# See: scripts/setup/proxmox/docker_host_setup_guide.md for full setup.
# ============================================================================

echo "--- Creating VM 103: Docker host (Debian) ---"

# Reuse Debian ISO found above
if [ -z "$DEBIAN_ISO" ]; then
    DEBIAN_ISO=$(ls /var/lib/vz/template/iso/debian-12*.iso 2>/dev/null | head -1)
    if [ -z "$DEBIAN_ISO" ]; then
        echo "ERROR: No Debian 12 ISO found. Download and retry."
        exit 1
    fi
    DEBIAN_ISO_NAME=$(basename "$DEBIAN_ISO")
fi

qm create 103 \
    --name docker-host \
    --machine q35 \
    --bios ovmf \
    --ostype l26 \
    --sockets 1 \
    --cores 1 \
    --cpu host \
    --memory 1024 \
    --balloon 0 \
    --scsihw virtio-scsi-single \
    --boot order=scsi0 \
    --onboot 1 \
    --startup order=3 \
    --tablet 0 \
    --net0 virtio,bridge=vmbr0,tag=20

qm set 103 \
    --efidisk0 ${STORAGE}:1,efitype=4m,pre-enrolled-keys=0

# 16GB system disk — sufficient for Debian minimal + lightweight Docker stacks
qm set 103 \
    --scsi0 ${STORAGE}:16,cache=writeback,discard=on,ssd=1

qm set 103 \
    --ide2 ${ISO_STORAGE}:iso/${DEBIAN_ISO_NAME},media=cdrom

echo "✓ VM 103 created"
echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo "============================================"
echo "VM CREATION COMPLETE"
echo "============================================"
echo ""
qm list | grep -E "(VMID|100|101|103)"
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
echo "VM 103 — Docker host:"
echo "  1. Start: qm start 103"
echo "  2. Open console in Proxmox web UI to complete Debian install"
echo "  3. Follow scripts/setup/proxmox/docker_host_setup_guide.md"
echo "  4. Note MAC: qm config 103 | grep net0"
echo "  5. Remove ISO after install: qm set 103 --delete ide2"
echo ""
echo "IMPORTANT: After all VMs are up, note their MAC addresses and add to"
echo "  configs/openwrt/dhcp-config.conf (home-assistant, frigate-nvr,"
echo "  and docker-host entries), then re-apply the DHCP config to the"
echo "  router per scripts/setup/router/phase_3_dhcp_configuration.md."
echo ""
echo "iGPU PASSTHROUGH for Frigate (after confirming IOMMU active):"
echo "  See frigate_vm_setup_guide.md Phase 6"
