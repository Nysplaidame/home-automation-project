# Jellyfin

Jellyfin runs on docker-host without hardware transcoding in its first phase.
Configuration and cache stay beside this Compose file; approved OMV libraries
are mounted read-only. Do not mount `/mnt/omv/media`, `incoming`, `quarantine`,
Immich's live library or backup paths into this container.

The live deployment uses the dedicated OMV `media-service` identity
(`1007:100`) and an explicit `10.240.10.0/24` Docker network. The NFS mount,
read-only library boundary, HTTP health check and restart proof passed on
2026-07-29. Keep hardware transcoding disabled until shared-iGPU capacity is
reviewed.
