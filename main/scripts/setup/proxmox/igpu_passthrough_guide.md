# iGPU Passthrough Guide — Intel Core Ultra 5 125H iGPU → Frigate VM
# Host: Proxmox on MINISFORUM M1 Pro-125H
# Target VM: 101 (frigate-nvr, VLAN 30, 192.168.30.20)
# Goal: OpenVINO AI detection + VA-API hardware video decode in Frigate
#
# WHY THIS APPROACH:
# Frigate needs two things from the GPU:
#   1. VA-API  — hardware FFmpeg decode (4x 1080p streams, lower CPU load)
#   2. OpenVINO — GPU-accelerated AI object detection (person/car/etc)
# Both are served by passing the Intel GPU's PCI device into the Frigate VM.
# This is simpler than VFIO passthrough for discrete GPUs because Intel integrated
# GPUs often sit in a straightforward IOMMU group on small x86 systems.
#
# NOTE:
# The MINISFORUM M1 Pro-125H also includes an Intel NPU. This guide is for the
# existing VM 101 iGPU/OpenVINO path, not NPU passthrough. NPU offload should be
# documented separately because it likely uses `/dev/accel/accel0` and an
# LXC-oriented device mapping rather than PCI GPU passthrough into the VM.
#
# PREREQUISITES:
#   - proxmox_setup_guide.md Phase C complete (intel_iommu=on iommu=pt in grub)
#   - Proxmox host has been REBOOTED after adding those grub flags
#   - Frigate VM (101) exists and Frigate is running (frigate_vm_setup_guide.md)
#   - VM 101 is STOPPED before Phase 3

---

## Phase 1 — Verify IOMMU is active on the Proxmox host

SSH into Proxmox (192.168.10.10) as root:

```bash
# Check IOMMU is enabled in the kernel
dmesg | grep -e DMAR -e IOMMU | head -20
```

You should see lines like:
```
DMAR: IOMMU enabled
DMAR: Intel(R) Virtualization Technology for Directed I/O
```

If you see nothing, the grub flags haven't taken effect. Verify and reboot:
```bash
cat /etc/default/grub | grep GRUB_CMDLINE
# Should contain: intel_iommu=on iommu=pt
# If not, add them and run: update-grub && reboot
```

Also confirm IOMMU groups are populated:
```bash
ls /sys/kernel/iommu_groups/ | wc -l
# Should be > 0 (typically 10-20 groups on this hardware)
```

---

## Phase 2 — Identify the iGPU PCI address and IOMMU group

```bash
# List all GPU-related PCI devices
lspci | grep -i "vga\|display\|3d\|gpu"
# Expected output (address will match — device name may vary):
#   00:02.0 VGA compatible controller: Intel Corporation Meteor Lake-P [Intel Graphics]
```

Note the PCI address. It is commonly `00:02.0` for the integrated GPU, but
verify it on the live Proxmox host before adding passthrough.

Now confirm it has a clean IOMMU group (ideally alone or with only iGPU sub-functions):
```bash
# Show IOMMU group for the iGPU
GPU_ADDR="0000:00:02.0"
GPU_GROUP=$(cat /sys/bus/pci/devices/${GPU_ADDR}/iommu_group/type 2>/dev/null || \
    ls -la /sys/bus/pci/devices/${GPU_ADDR}/iommu_group | grep -o 'iommu_groups/[0-9]*' | grep -o '[0-9]*')
echo "iGPU IOMMU group: $(ls /sys/bus/pci/devices/${GPU_ADDR}/iommu_group/devices/)"
```

What you want to see: only `0000:00:02.0` in the group (iGPU alone).
What causes problems: unrelated devices sharing the same group.

If other devices share the group, passthrough still works on most systems — the
`iommu=pt` flag we set helps isolate groups. Only a problem if a critical
host device (e.g. NVMe controller) shares the group.

---

## Phase 3 — Add iGPU as PCI device to VM 101

**VM 101 must be stopped before this step.**

```bash
qm stop 101
```

**Option A — Web UI (easier)**

`VM 101 → Hardware → Add → PCI Device`

| Field | Value |
|---|---|
| Device | Select the Intel UHD / Xe entry (`00:02.0`) |
| All Functions | ✅ (passes all sub-functions of the device) |
| PCI-Express | ✅ |
| Primary GPU | ❌ (leave unticked — Proxmox console must still work) |
| ROM-Bar | ❌ |

Click **Add**.

**Option B — CLI**

```bash
qm set 101 --hostpci0 0000:00:02.0,pcie=1,x-vga=0
```

Verify the config was applied:
```bash
qm config 101 | grep hostpci
# Should show: hostpci0: 0000:00:02.0,pcie=1
```

Start the VM:
```bash
qm start 101
```

---

## Phase 4 — Install Intel GPU drivers inside the Frigate VM

SSH into the Frigate VM (192.168.30.20):

```bash
# Verify the GPU is visible inside the VM
lspci | grep -i "vga\|display\|intel"
# Should show the Intel UHD / Xe GPU

# Check DRI render node exists
ls -la /dev/dri/
# Should show: card0, renderD128 (and possibly renderD129)
```

If `/dev/dri/` is empty or missing, the PCI passthrough isn't working —
go back and check the Proxmox hostpci config and IOMMU verification.

Install drivers:
```bash
apt-get update
apt-get install -y \
    intel-media-va-driver-non-free \
    intel-opencl-icd \
    vainfo \
    clinfo \
    i965-va-driver

# Add the admin user to the render and video groups
usermod -aG render,video admin

# Verify VA-API works
vainfo
# Should show: VAEntrypointVLD, VAEntrypointEncSlice etc for H.264/H.265
```

If `vainfo` shows no devices, try:
```bash
LIBVA_DRIVER_NAME=iHD vainfo    # modern Intel driver
# or
LIBVA_DRIVER_NAME=i965 vainfo   # legacy driver
```

Use whichever works — note which driver name for the Frigate config later.

---

## Phase 5 — Update Docker Compose to pass GPU to Frigate container

Edit `/opt/frigate/docker-compose.yml` on the Frigate VM.
Find the `frigate:` service and uncomment the devices line:

```yaml
  frigate:
    ...
    devices:
      - /dev/dri/renderD128:/dev/dri/renderD128
    # Also add the video group so the container can access the device:
    group_add:
      - "video"
      - "render"
```

To get the numeric group IDs (Docker requires numbers, not names):
```bash
getent group video | cut -d: -f3     # typically 44
getent group render | cut -d: -f3    # typically 104 or 105
```

Full updated devices + group_add block:
```yaml
    devices:
      - /dev/dri/renderD128:/dev/dri/renderD128
    group_add:
      - "44"     # video — replace with actual output from getent above
      - "104"    # render — replace with actual output from getent above
```

---

## Phase 6 — Update Frigate config.yml for OpenVINO + VA-API

Edit `/opt/frigate/config/config.yml`:

### 6.1 — Replace the CPU detector with OpenVINO

Remove:
```yaml
detectors:
  cpu1:
    type: cpu
    num_threads: 2
```

Replace with:
```yaml
detectors:
  ov:
    type: openvino
    device: GPU
    # Model is bundled with Frigate stable — no separate download needed
    model:
      path: /openvino-model/ssdlite_mobilenet_v2.xml
      labelmap_path: /openvino-model/coco_91cl_bkgr.txt
      input_tensor: nhwc
      input_pixel_format: bgr
      width: 300
      height: 300

model:
  width: 300
  height: 300
```

### 6.2 — Add VA-API hardware decode to every camera

For each camera in config.yml, add `hwaccel_args` under `ffmpeg`:

```yaml
cameras:
  cam_01:
    ffmpeg:
      hwaccel_args: preset-vaapi
      inputs:
        - path: rtsp://admin:{FRIGATE_RTSP_PASSWORD}@192.168.30.21:554/stream1
          roles: [detect, record]
    detect:
      enabled: true
      width: 1920
      height: 1080
      fps: 5
    objects:
      track: [person, car, cat, dog]
```

Repeat `hwaccel_args: preset-vaapi` for cam_02, cam_03, cam_04.

> If VA-API decode causes issues (garbled frames, Frigate restarts), remove
> `hwaccel_args` from problem cameras and keep OpenVINO detection — they are
> independent. Detection on GPU still works without VA-API decode.

---

## Phase 7 — Restart Frigate and verify

```bash
cd /opt/frigate
docker compose restart frigate
docker compose logs -f frigate
```

Watch the logs for these confirmation lines:

```
# OpenVINO detector loaded on GPU:
[detector.ov] openvino GPU available
[detector.ov] loading model...
[detector.ov] model loaded

# VA-API hardware decode active (one line per camera):
[ffmpeg.cam_01] hwaccel: vaapi
```

If you see `Falling back to cpu` for the detector, the GPU device isn't
accessible to the container — check the group_add IDs in docker-compose.yml.

### 7.1 — Verify GPU is doing the work

```bash
# On the Frigate VM — monitor GPU utilisation
intel_gpu_top    # install: apt-get install intel-gpu-tools

# You should see Render/3D and Video engine utilisation > 0% while
# cameras are streaming and detections are occurring
```

### 7.2 — Verify CPU load dropped

```bash
htop
# Compare CPU % before vs after GPU acceleration
# With 4x 1080p streams + CPU detection: expect 60-90% CPU
# With VA-API + OpenVINO GPU detection: expect 10-30% CPU
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `/dev/dri/` empty in VM | IOMMU not active or PCI passthrough not applied | Re-check Phase 1 and 3 |
| `vainfo` shows no devices | Wrong VA driver | Try `LIBVA_DRIVER_NAME=iHD vainfo` vs `i965` |
| OpenVINO falls back to CPU | GPU not accessible to container | Check group_add IDs in docker-compose.yml |
| Garbled frames / decode errors | VA-API driver issue | Remove `hwaccel_args` per-camera; keep OpenVINO |
| Proxmox console black after reboot | `x-vga=1` was set | Edit VM config: `qm set 101 --hostpci0 ...,x-vga=0` |
| VM fails to start after adding PCI device | IOMMU group conflict | Check other devices in the same group (`ls /sys/kernel/iommu_groups/<n>/devices/`) |
| `intel_gpu_top` shows 0% render | Detection running on CPU not GPU | Check Frigate logs for "openvino GPU available" |

### Check which IOMMU group has a problem device

```bash
# Full IOMMU group listing
for g in /sys/kernel/iommu_groups/*/devices/*; do
    group=$(echo $g | cut -d/ -f6)
    device=$(echo $g | cut -d/ -f8)
    printf "Group %3s: %s %s\n" "$group" "$device" "$(lspci -nns $device 2>/dev/null | cut -d' ' -f2-)"
done | sort -n
```

Look for group containing `00:02.0`. If it also contains other devices like
`00:02.1` (those are sub-functions of the same GPU — fine to pass together)
but NOT unrelated devices like NVMe or USB controllers.

---

## Completion checklist

- [ ] IOMMU active on Proxmox host (`dmesg | grep IOMMU` shows enabled)
- [ ] iGPU identified at `00:02.0`, IOMMU group confirmed clean
- [ ] VM 101 stopped before adding PCI device
- [ ] PCI device `00:02.0` added to VM 101 with pcie=1, x-vga=0
- [ ] VM 101 restarted — `/dev/dri/renderD128` visible inside VM
- [ ] `intel-media-va-driver-non-free` and `intel-opencl-icd` installed in VM
- [ ] `vainfo` returns profile list (VA-API working)
- [ ] docker-compose.yml: `devices` + `group_add` lines added
- [ ] config.yml: `detectors` replaced with `openvino` (device: GPU)
- [ ] config.yml: `hwaccel_args: preset-vaapi` added to all cameras
- [ ] Frigate restarted — logs confirm "openvino GPU available"
- [ ] Logs confirm "hwaccel: vaapi" for each camera stream
- [ ] `intel_gpu_top` shows GPU activity during live detection
- [ ] CPU load measurably lower than before passthrough
