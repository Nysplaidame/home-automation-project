# Docker-host Alloy log collector

Alloy ships docker-host Docker logs and Bambuddy's dedicated application logs to
Loki on the monitoring VM. It has no published UI or port.

Live path: `/opt/stacks/alloy/` on docker-host.

The runtime `certs/` directory is intentionally absent from this repository. It
contains the private mTLS client key, client certificate, and CA certificate.
Loki accepts ingestion only from `192.168.20.102:3100` and requires that client
certificate. Do not replace this with unauthenticated HTTP.

After recovery, validate with:

```sh
cd /opt/stacks/alloy
docker compose ps
docker compose logs --tail=50
```

Open Grafana and select the **Loki** data source in **Explore**. Queries such
as `{host="docker-host"}` show all collected docker-host logs; use
`{job="bambuddy", source="application"}` for Bambuddy's detailed server log.
