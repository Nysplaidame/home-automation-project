# VentSys authenticated card draft — 2026-09-07

`ventsys-card.js` is preserved draft source, not a deployable replacement for
the currently accepted dashboard. The card posts same-origin state snapshots
and includes service-call handling, but `ventsys-dashboard.html` does not yet
consume that bridge protocol. The page deliberately remains offline; public
token overrides are ignored. Do not put long-lived HA tokens in `/local/` assets.

The September audit fixed a startup ReferenceError left by the partial auth
migration. Five local browser/mock tests pass for command-free startup, offline
controls and actuator-derived display state. They do not certify authenticated
operation, message authorization or physical safety. No dashboard/card file was
deployed by this audit, and no live HA/MQTT service call was made.

Before promotion: review the exact entity/topic/script allowlists, implement
and test the page/card handshake, origin/source validation, request expiry and
disconnect behavior, confirm no token leaves HA's authenticated context, prove
startup cannot issue a command, then use the existing separately accepted
physical/safety test procedure. Preserve the live asset and its rollback copy
until that work is complete. Current task tracking is in `../TO-DO.md`.
