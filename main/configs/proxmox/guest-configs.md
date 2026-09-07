# Current Proxmox Guest Inventory

Verified 2026-07-07. Use `qm config` for VMs and `pct config` for LXCs.

2026-09-04 API audit: production guests are running; rollback VMs 101/104 are
stopped. VM 103 was found at 1024 MiB and restored to **4 cores / 6144 MiB**
with a graceful shutdown/start; guest agent and application health recovered.
The host reports 64 GB installed, superseding older 32 GB hardware notes.

| ID | Kind | Name | VLAN/IP | CPU/RAM/Disk | Startup | State |
|---:|---|---|---|---|---|---|
| 100 | VM | home-assistant | 20 / 192.168.20.101 | 2c / 6 GiB configured, 4 GiB until guest restart / 32 GiB | order 1, onboot | live |
| 101 | VM | frigate-nvr | disconnected rollback identity | 2c / 4 GiB / 64 GiB | off | rollback only |
| 102 | VM | monitoring | 60 / 192.168.60.10 | 2c / 3 GiB configured, 2 GiB until guest restart / 32 GiB | order 3, onboot | live |
| 103 | VM | docker-host | 20 / 192.168.20.102 | 4c / 6 GiB configured and running 2026-09-04 / 64 GiB | order 3, onboot | live, recovered |
| 104 | VM | llm-host | disconnected rollback identity | 4c / 10 GiB / 160 GiB | off | rollback only |
| 111 | LXC | frigate-nvr | 30 / 192.168.30.20 | 2c / 6 GiB / 32 GiB | order 2, onboot | live |
| 114 | LXC | llm-host | 20 / 192.168.20.104 | 4c / 20 GiB / 100 GiB | order 4, onboot | live |

## Shared GPU entries

Both CT 111 and CT 114:

```text
dev0: path=/dev/dri/renderD128,gid=993,mode=0660
dev1: path=/dev/dri/card0,gid=44,mode=0660
features: nesting=1,keyctl=1
unprivileged: 1
swap: 0
```

The former pre-LXC inventory is archived under
`_archive/2026-06-20-pre-lxc-and-handoffs/` and must not be used to recreate
VM 101/104 as production guests.
