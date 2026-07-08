---
title: Grocy Install Manual
description: Live household food-stock and expiry-tracking service
tags: [install, docker-host, grocy, food-inventory]
created: 2026-06-21
modified: 2026-07-07
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

Current live check on 2026-07-07:

- Container `grocy` was up on docker-host.
- `curl -I http://127.0.0.1:9283/` returned `HTTP/1.1 302 Found`, matching a
  login/session redirect rather than a dead service.
- A database checkpoint was created before seeding:
  `/opt/stacks/grocy/config/data/grocy.db.pre-household-seed-20260707T125250Z`.
- Core household model was seeded:
  - Locations: `Pantry`, `Fridge`, `Freezer`, `Cleaning`, `Garage/Workshop`.
  - Quantity units: existing `Piece`/`Pack`, plus `each`, `box`, `bottle`,
    `jar`, `g`, `kg`, `ml`, and `L`.
  - Product groups: `Dry goods`, `Chilled`, `Frozen`, `Cleaning`,
    `Household consumables`, and `Printer/workshop consumables`.
- OMV app-data backup run `20260707T125454Z` captured the seeded database.
- Home Assistant voice/Assist shopping-list API access was deployed and
  backup run `20260707T132647Z` captured the Grocy API-key state.

## Operator setup

Do this from a trusted browser on HomeAdmin/LAN or over the approved docker-host
Tailscale path:

1. Open `http://grocy.home.local:9283/`.
2. Sign in.
3. Add a small pilot set first: 5-10 common products with barcodes/expiry where
   available, then test purchase, consume, inventory correction, and expiry
   views.

Completion proof:

- Grocy still returns a login redirect instead of an error.
- Locations, units, and product groups exist.
- At least one pilot product can be purchased, consumed, and corrected.
- `/opt/stacks/grocy/config` is included in the docker-host backup plan.

## Backup

Back up `/opt/stacks/grocy/config` through the docker-host app-data backup layer
to OMV `backups/docker-host`. This directory contains the Grocy application
state, including the database used by the LinuxServer container.

Consistency rule:

- Stop the `grocy` container before file-level restore.
- Before large data-model changes, take a manual copy or app export as a
  named checkpoint.

Restore smoke:

```sh
cd /opt/stacks/grocy
docker compose stop grocy
# restore /opt/stacks/grocy/config from the selected backup
docker compose up -d
curl -I http://127.0.0.1:9283/
```

## Home Assistant voice access

Home Assistant exposes Grocy to Assist through the repo custom integration
`configs/home-assistant/custom_components/grocy_llm/`. The integration registers
LLM tools for two low-risk shopping-list actions only:

- add an item to the Grocy shopping list
- list unchecked Grocy shopping-list items

Do not use voice tools for purchase, consume, stock correction, inventory
counts, product deletion, or marking items completed until a confirmation-gated
workflow exists.

Live state on 2026-07-07:

- HA `/config/configuration.yaml` includes `grocy_llm` and adds
  `grocy_household` to the local LLM exposed API list.
- HA `/config/secrets.yaml` contains `grocy_api_key`.
- The dedicated Grocy key is named `home-assistant-voice`; a live copy is on
  docker-host at `/root/grocy-home-assistant-voice-api-key.txt` with root-only
  permissions. Store the value in Bitwarden as part of the hardening pass.
- docker-host firewall allows HA `192.168.20.101` and the HA Supervisor network
  `172.30.32.0/23` to reach Grocy `9283/tcp`.
- HA config check passed, HA restarted cleanly, and logs showed no Grocy custom
  component errors.
- HA-to-Grocy API proof succeeded by creating a temporary product, adding it to
  the shopping list, deleting the temporary product, and confirming the shopping
  list was empty afterward.

Manual Assist phrases to test:

- "Add bananas to the shopping list."
- "What's on the Grocy shopping list?"

## Completion checklist

- [x] UI responds.
- [x] Core household locations, quantity units, and product groups configured.
- [ ] Pilot product purchase/consume/correction and expiry workflow tested.
- [x] `/opt/stacks/grocy/config` backup path verified.
- [x] Restore smoke tested to a temporary path or controlled service stop.
- [x] HA Assist backend/API path proved for add/list shopping-list actions.
