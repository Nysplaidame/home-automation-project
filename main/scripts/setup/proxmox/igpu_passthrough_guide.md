# Shared Intel iGPU Mapping for Proxmox LXCs

The production design keeps the Intel Meteor Lake iGPU on the Proxmox host and
maps its DRM devices into multiple unprivileged LXCs. This is device sharing,
not PCI passthrough; `intel_iommu=on` is not required.

## Host facts

- Render node: `/dev/dri/renderD128`
- Card node: `/dev/dri/card1`
- CT render group: GID `992`
- CT video group: GID `44`

Run on the Proxmox host:

```bash
pct set 111 --dev0 path=/dev/dri/renderD128,gid=992,mode=0660
pct set 111 --dev1 path=/dev/dri/card1,gid=44,mode=0660
pct set 114 --dev0 path=/dev/dri/renderD128,gid=992,mode=0660
pct set 114 --dev1 path=/dev/dri/card1,gid=44,mode=0660
```

Both containers require `features: nesting=1,keyctl=1` for Docker.

## Validation

Inside each LXC:

```bash
ls -ln /dev/dri
vainfo --display drm --device /dev/dri/renderD128
```

Frigate validation:

```bash
docker exec frigate ps aux | grep '[d]etector:ov'
```

Ollama validation:

```bash
docker logs ollama 2>&1 | grep -E 'Vulkan|offloaded [0-9]+/[0-9]+ layers'
```

The production result is concurrent Frigate OpenVINO and Ollama Vulkan use.
Do not revive the archived PCI-passthrough guide for VM 101.
