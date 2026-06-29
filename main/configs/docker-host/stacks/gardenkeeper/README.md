# GardenKeeper Docker-Host Stack

Template for the live GardenKeeper stack at:

```text
/opt/stacks/gardenkeeper/
```

Expected live layout:

```text
/opt/stacks/gardenkeeper/
  docker-compose.yml
  .env
  source/            # GardenKeeper application repository
  postgres-data/     # generated, do not commit
  redis-data/        # generated, do not commit
```

Copy `env.example` to `.env`, generate a unique database password, and keep
live secrets out of Git.

Default ports:

- Web UI: `8091/tcp`
- API: `8090/tcp`

The web container serves the built Vite app through nginx and proxies `/api` and
`/health` to the API container. The API runs migrations on startup when
`AUTO_RUN_MIGRATIONS=true`.
