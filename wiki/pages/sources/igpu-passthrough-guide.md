---
title: "iGPU Passthrough Guide — Intel i3-N350 → Frigate VM"
category: source
tags: [igpu, proxmox, frigate, openvino, vaapi, hardware-acceleration]
created: 2026-04-07
updated: 2026-04-07
status: stable
---

# Source: iGPU Passthrough Guide

**Original file:** `scripts/setup/proxmox/igpu_passthrough_guide.md`
**Date ingested:** 2026-04-07
**Type:** setup guide

## Summary

7-phase guide for passing the Intel i3-N350's Xe iGPU through to Frigate VM (VM 101) for VA-API hardware video decode and OpenVINO AI object detection. Expected result: CPU load drops from 60–90% to 10–30% with 4× 1080p streams.

## Key Takeaways

- **Prerequisite:** `intel_iommu=on iommu=pt` in GRUB must be set AND the host rebooted before starting
- **PCI address:** almost certainly `00:02.0` on the N350; verify with `lspci | grep -i vga`
- **IOMMU group check:** iGPU should be alone in its group (only `00:02.0`); sub-functions like `00:02.1` sharing the group are fine — unrelated devices (NVMe, USB) sharing it are a problem
- **VM must be STOPPED** before adding PCI device: `qm stop 101` then `qm set 101 --hostpci0 0000:00:02.0,pcie=1,x-vga=0`
- **`x-vga=0` is critical** — setting `x-vga=1` blackscreens the Proxmox console after reboot
- **Drivers inside VM:** `intel-media-va-driver-non-free` + `intel-opencl-icd`; verify with `vainfo`; try `LIBVA_DRIVER_NAME=iHD vainfo` if default fails
- **docker-compose.yml:** uncomment `- /dev/dri/renderD128:/dev/dri/renderD128` under `devices:`, add `group_add:` with numeric IDs for `video` (typically 44) and `render` (typically 104+)
- **Frigate config.yml:** replace `cpu1` detector with `openvino` detector (`device: GPU`); add `hwaccel_args: preset-vaapi` to all camera `ffmpeg:` blocks
- **OpenVINO model:** bundled with Frigate stable — no separate download needed; path `/openvino-model/ssdlite_mobilenet_v2.xml`
- **Verification:** `intel_gpu_top` (install `intel-gpu-tools`) shows GPU activity; Frigate logs show "openvino GPU available" and "hwaccel: vaapi" per camera
- **VA-API is independent of OpenVINO** — if decode causes garbled frames, remove `hwaccel_args` per camera while keeping OpenVINO detection

## Entities Mentioned

[[entities/frigate]], [[entities/proxmox]], [[entities/minix-neo-z350]]

## Contradictions / Updates

None — first iGPU guide ingested. Completes the Frigate setup picture (previously the compose file had GPU lines pre-commented with a "Phase 6" note).
