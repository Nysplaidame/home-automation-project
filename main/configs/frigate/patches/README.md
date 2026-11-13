# Configuration publisher lifecycle repair

`config_updater.py` is a tracked local overlay for the pinned Frigate0.17.1
image. The ConfigSubscriber implementation is unchanged from upstream.
ConfigPublisher now creates, polls, sends and destroys its ZeroMQ PUB socket
on one dedicated owner thread. API/MQTT callers use a bounded64-entry queue
and await send completion; multipart messages cannot interleave. Idle event
polling every100ms drains native attach/termination bookkeeping. Shutdown
is idempotent, bounded and joins the owner; no periodic malloc_trim is used.

Compose mounts `/opt/frigate/patches/config_updater.py` read-only over
`/opt/frigate/frigate/comms/config_updater.py`. Upload this file before using
the updated Compose definition; otherwise Docker may create a directory at
the absent bind source. Do not copy the file into a running container as the
only deployment: recreation would discard that change.

The overlay is version-coupled. Before changing the pinned image, compare
upstream transport APIs, either remove it after an equivalent upstream fix
passes the lifecycle tests or port/retest it. A version upgrade alone does
not establish repair.

Source basis:
https://github.com/blakeblackshear/frigate/blob/v0.17.1/frigate/comms/config_updater.py

Tests: [[../../../scripts/validation/frigate_publisher_lifecycle_test.py]].
The normal suite uses unique isolated IPC endpoints; `--churn` adds3600
reconnects against the actual class. `--live-churn` explicitly creates12000
read-only subscriptions to the live endpoint and measures main-process RSS;
it sends no configuration changes. Do not run the live test during unrelated
heavy work when RSS interpretation would be ambiguous.

Deployment and rollback: [[../../../docs/install/phases/04-frigate]].
