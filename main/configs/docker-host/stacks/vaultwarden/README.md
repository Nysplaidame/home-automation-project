# Vaultwarden

The raw HTTP listener is bound to docker-host loopback only. Production access
must use the dedicated `vault.home.local` certificate and fixed TLS reverse
proxy. Public sign-ups remain disabled and the administrator endpoint remains
disabled when `ADMIN_TOKEN` is blank.

The production container is live on an explicit `10.240.30.0/24` Docker
network, while its raw listener remains loopback-only on `127.0.0.1:8222`.
`vault.home.local` terminates with its own local-CA certificate at the fixed
Homepage Nginx proxy; HTTPS, HSTS and the no-framing policy were verified on
2026-07-29.

Two isolated restore proofs passed before onboarding: a clean production
SQLite backup, followed by a disposable registered account restored into a
second temporary container with integrity, exact account count and HTTP health
checks. All temporary containers, networks and restored data were removed.
Production sign-ups and the admin endpoint remain disabled. Do not import real
credentials until live DNS is deployed and the owner account, 2FA, recovery
codes and emergency-access policy are completed. Recovery codes and live tokens
never belong in this directory or Git.
