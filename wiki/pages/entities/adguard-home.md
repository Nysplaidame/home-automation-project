---
title: "AdGuard Home"
category: entity
tags: [dns, adblocking, docker, docker-host]
created: 2026-05-23
updated: 2026-05-30
sources: [project-readme, project-todo]
status: active
---

# AdGuard Home

**Type:** service - DNS filtering/adblocking
**Status:** Live Tier 1 docker-host service
**Related:** [[entities/docker-host]], [[entities/gl-mt6000]]

## Overview

AdGuard Home is the selected network-wide DNS filtering service. It runs on
[[entities/docker-host]] under `/opt/stacks/adguard-home/`. OpenWrt remains the
DHCP, local DNS, and firewall authority.

## Key Properties

- Host: docker-host `192.168.20.102`
- DNS port: 53/tcp+udp
- Admin UI: 8080
- Router dnsmasq forwards to AdGuard first, then falls back to Quad9 and Cloudflare

## Change Log

- 2026-05-30: Updated from planned to live docker-host Tier 1 service.
- 2026-05-23: Page created from canonical DNS/adblocking decision.
