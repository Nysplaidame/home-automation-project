# Calibre-Web

Calibre-Web receives write access only to the dedicated Calibre library root.
Its application configuration remains local under `./config` and joins the
docker-host app-data backup. Do not point it at the legacy mixed `Media` tree.

The live deployment uses the dedicated OMV `media-service` identity and an
explicit `10.240.11.0/24` Docker network. The scoped library write/delete test,
HTTP redirect and restart proof passed on 2026-07-29. Application configuration
is included in the docker-host NAS backup job.
