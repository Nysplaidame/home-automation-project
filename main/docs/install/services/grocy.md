---
title: Grocy Install Manual
description: Live household food-stock and expiry-tracking service
tags: [install, docker-host, grocy, food-inventory]
created: 2026-06-21
modified: 2026-06-21
type: install-guide
status: live
---

# Grocy Install Manual

Grocy runs on docker-host at `http://grocy.home.local:9283/` using the pinned
LinuxServer image for Grocy 4.6.0. Persistent state is under
`/opt/stacks/grocy/config`.

```sh
mkdir -p /opt/stacks/grocy/config
cp /path/to/repo/main/configs/docker-host/stacks/grocy/docker-compose.yml \
  /opt/stacks/grocy/docker-compose.yml
cd /opt/stacks/grocy
docker compose up -d
```

The initial login is `admin` / `admin`; replace it immediately and store the
new credential in Bitwarden. Back up the complete `config` directory. Grocy is
the system of record for stock quantities, locations, purchases, consumption
and expiry dates. Recipes remain in Mealie.

