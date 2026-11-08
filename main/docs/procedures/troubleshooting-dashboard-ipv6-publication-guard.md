---
title: Troubleshooting dashboard IPv6 publication guard
description: Reconciliation and change gate for the pre-existing port 8094 IPv6 return
tags: [security, ipv6, dashboard, firewall]
created: 2026-09-18
type: security-boundary
status: review-required
---

# Troubleshooting dashboard IPv6 publication guard

The Troubleshooting Dashboard is approved for its existing IPv4 management bind
and Homepage HTTPS preview only. Its bridge has IPv6 disabled. A pre-existing
`tailscale0` IPv6 `DOCKER-USER` return for TCP 8094 contradicts the older
blanket-denial description and must not be treated as approved publication.

## Current policy

No new IPv6 listener, route, DNS record, Homepage route, or firewall allowance
is authorized by this document. The desired steady state is that direct port
8094 remains unavailable over IPv6 unless a separately approved release names
the audience, authentication, host bind, reverse-proxy route, monitoring, and
rollback.

## Reconciliation procedure

Before any firewall edit, capture the exact IPv6 rule order, counters, Docker
publish state, interface addresses, bridge IPv6 setting, and reachable paths
from a permitted and denied source. Establish whether the return can actually
reach a listener; do not infer exposure from rule text alone.

If there is no approved IPv6 audience, make one bounded, reversible firewall
change that removes or precedes the exception with the intended deny rule. Save
the prior ruleset, reload only after syntax validation, verify the existing
IPv4/Homepage routes still work, and prove IPv6 denial from the named source.
The change needs a maintenance-window owner because it affects host firewall
policy.

If IPv6 publication is requested later, design it as a separate HTTPS/auth
release—not as an exception to raw port 8094. It must retain browser-local
evidence and the dashboard's no-command/no-credential boundary.

## October 2 read-only evidence and prepared source

At21:21 BST (20:21 UTC), VM103 inspection found:

- Running `troubleshooting-dashboard` publishes container80/TCP only to
  `192.168.20.102:8094`. `ss` reports that IPv4 listener; no IPv6 listener for8094.
- Its `troubleshooting-dashboard` bridge has `EnableIPv6=false`, subnet
  `10.240.32.0/24`, gateway `10.240.32.1`.
- IPv6 DOCKER-USER rule32 is the exact Tailscale RETURN below; rule33 is the
  matching interface-independent DROP. Both counters were zero at inspection.
- `eth0` has only link-local IPv6; `tailscale0` has
  `fd7a:115c:a1e0::6f36:7a12/128` plus link-local IPv6. A tailnet IPv6 address
  exists even though this application has no IPv6 publish binding.
- The host's direct IPv4 HTTP check returns200. Windows management-PC IPv6
  curl to the tailnet address times out (exit28); monitoring VM102's probe
  fails to connect immediately (exit7). Neither establishes a named permitted
  tailnet-client route or proves DROP enforcement. No successful IPv6 dashboard
  connection was observed, but full audience-path denial acceptance stays open.

The tracked `configs/docker-host/system/docker-host-firewall.sh` now stages a
dedicated8094 IPv6 DROP and omits8094 from its Tailscale allow-loop. Existing
RELATED/ESTABLISHED handling and the other22 published-port exceptions remain.
An isolated recording-executable test proves emitted rule order/port scope;
all16 system-helper tests pass. **This source change is not deployed.**

Do not run the whole tracked script to remove one live rule: it flushes and
rebuilds both DOCKER-USER chains, and its IPv4 section does not encode the full
current dashboard8094 management policy. Reconciling persistent source with
the live rules is part of maintenance review, not authority to replace them.

For an approved bounded change, freshly capture the protected IPv6 ruleset,
current order/counters and approved client paths, then confirm the exact
exception and fallback DROP still exist. The specific removal candidate is:

```sh
# Maintenance-gated candidate only; do not execute during read-only inspection.
ip6tables -C DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdstport 8094 -j RETURN
ip6tables -C DOCKER-USER -p tcp -m conntrack --ctorigdstport 8094 -j DROP
ip6tables -D DOCKER-USER -i tailscale0 -p tcp -m conntrack --ctorigdstport 8094 -j RETURN
```

Abort if rules/order differ, duplicates exist or other earlier rules could admit
new8094 traffic. Save the exception's original line number for rollback; only
if chain order remains otherwise unchanged, reinsert the exact RETURN at that
saved position with `ip6tables -I DOCKER-USER <saved-position> ...`. Do not use
the October2 number blindly, append a broad RETURN, or restore an entire stale
ruleset over intervening policy changes. Re-test IPv4/Homepage and named IPv6
client paths, and reconcile persistence without a broad firewall reload before
closing the live task. Established-flow handling remains a separate consideration.

## Related work

- [Troubleshooting Dashboard README](../../apps/troubleshooting-dashboard/README.md)
- [Access matrix](../reference/access-matrix.md)
- [Current live state](../reference/current-live-state.md)
