# Atsumeru

Atsumeru receives only its comics library plus local application data paths.
The live deployment uses the dedicated OMV `media-service` identity and an
explicit `10.240.12.0/24` Docker network. The scoped library write/delete test,
authenticated HTTP response and restart proof passed on 2026-07-29.
Configuration and database paths are included in the docker-host NAS backup
job. The upstream server is primarily an API/client backend rather than a full
browser management UI, so Homepage should describe it accordingly.
