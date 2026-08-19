---
title: July 2026 Official Vendor Compatibility Review
created: 2026-07-10
modified: 2026-07-10
type: audit-evidence
status: discovery-frozen
---

# Official Vendor Compatibility Review

This review was refreshed on 2026-07-10 from primary vendor documentation. It
is a point-in-time compatibility/security record, not authorization to update.

## Home Assistant

Live Core 2026.7.1 matches the vendor's July patch release. The
[official 2026.7 release notes](https://www.home-assistant.io/blog/2026/07/01/release-20267/)
state that July patch releases are bug-fix releases and identify 2026.7.1 as the
July 3 patch. The
[full 2026.7 changelog](https://www.home-assistant.io/changelogs/core-2026.7)
also includes backup-extraction hardening. No version change was made.

The [official backup guidance](https://www.home-assistant.io/common-tasks/general/)
recommends a copy outside the HA system and ideally off-site. The live NAS-only,
same-estate design does not satisfy the latter recommendation. The
[automatic-backup action documentation](https://www.home-assistant.io/actions/backup.create_automatic/)
confirms that scheduled/action backups use the configured app/folder/location
selection, supporting the finding that the live excluded apps are not silently
included.

## Frigate

Live 0.17.1 is the current release shown by the
[official Frigate release page](https://github.com/blakeblackshear/frigate/releases).
That maintenance release includes fixes restricting the raw-config endpoint to
admins and correcting cross-camera authorization. The estate is therefore on
the release containing those fixes. The same release notes recommend backing
up configuration and `frigate.db` before upgrade and document 0.17 retention
and configuration changes; the source/live detect-state difference remains an
estate issue, not an upstream incompatibility.

## Docker

[Docker's firewall documentation](https://docs.docker.com/engine/networking/packet-filtering-firewalls/)
states that published container traffic is diverted before UFW's normal
INPUT/OUTPUT path. This validates the audit's decision to require router and
`DOCKER-USER` evidence. Disabling Docker's firewall management without a full
replacement is explicitly discouraged.

[Docker's daemon-socket guidance](https://docs.docker.com/engine/security/protect-access/)
states that possession of Docker API credentials/control is effectively root
access to the host. The four socket-mounting services therefore require an
explicit trust decision or a constrained proxy; a read-only mount flag alone
does not make the daemon API read-only.

## Tailscale

The [official route-injection reference](https://tailscale.com/docs/reference/route-injection)
confirms that advertisement, control-plane approval, client acceptance, and an
ACL/grant are distinct requirements. Local observation of four advertised
routes cannot certify approval or access policy. The
[ACL documentation](https://tailscale.com/docs/features/access-control/acls)
recommends grants for new policy while retaining ACL support; either format
must be exported and tested before the remote-access path can pass.

## Proxmox

Live PVE 9.1.9 is within the 9.x generation but behind the vendor's
[PVE 9.2 release](https://proxmox.com/en/about/company-details/press-releases/proxmox-virtual-environment-9-2)
published 2026-05-21. This is an update-review item, not an instruction to
upgrade. Compatibility, backup, guest restart, iGPU mapping and rollback must
be reviewed first.

The [Proxmox container restore documentation](https://pve.proxmox.com/pve-docs-9-beta/pct.1.html)
states that bind/device mount contents are not restored from the CT archive and
must be protected separately. That directly supports treating Frigate NFS
recordings and other external mount data as separate datasets.

## openmediavault

The [OMV release table](https://docs.openmediavault.org/en/latest/releases.html)
identifies OMV 8 on Debian 13 as the stable generation, so the live OMV 8 base
is supported. Point updates remain subject to staged review.

The [OMV FAQ](https://docs.openmediavault.org/en/latest/faq.html)
states that there is no regular configuration backup/restore procedure and
recommends retaining `/etc/openmediavault/config.xml` as a clean-reinstall
reference. The absence of a stored copy is therefore a concrete rebuild gap.

## ESPHome

[ESPHome's pin documentation](https://esphome.io/guides/configuration-types/)
states that strapping pins should be avoided and that warnings should be
suppressed only when the design is known safe. The
[ESPHome FAQ](https://esphome.io/guides/faq/)
explains that external circuitry can change boot mode and recommends avoiding
these pins unless their boot state is fully understood. Successful compilation
does not close the physical acceptance finding.

## Review conclusion

- HA and Frigate live core versions are aligned with the specific current
  release records checked.
- OMV is on the supported major generation.
- Proxmox has a newer minor release available and requires a staged review.
- The material vendor-guidance conflicts are architectural: Docker/UFW,
  Docker-socket privilege, Tailscale route-versus-policy proof, external CT
  mounts, off-site backups, OMV config retention and ESPHome strapping-pin
  safety.
