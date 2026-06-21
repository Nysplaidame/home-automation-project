---
title: Household Knowledge, Recipes and Food Inventory
description: Defines the system-of-record boundary between Obsidian, Mealie and a future stocktaking service
tags: [architecture-decision, obsidian, mealie, food-inventory]
created: 2026-06-21
modified: 2026-06-21
type: decision
status: accepted
---

# Household Knowledge, Recipes and Food Inventory

## Decision

- **Mealie** is the system of record for recipes, meal planning and
  recipe-derived shopping lists.
- **Obsidian** is the durable knowledge layer: project documentation, runbooks,
  household procedures, maintenance notes, research and human-readable context.
  It may link to Mealie or inventory records, but must not duplicate their live
  transactional state.
- A separate service will own pantry, fridge and freezer quantities, expiry
  dates, purchases and consumption. **Grocy is the leading candidate, not yet
  an approved or deployed component.** Its workflow and Mealie/HA integration
  must be tested before acceptance.
- **Home Assistant and Overwatch** are orchestration and conversational layers,
  not systems of record. Future tools should call scoped Mealie or inventory
  APIs and require confirmation before creating or changing household data.

## Consequences

Recipes should no longer be described as destined for “Obsidian or Mealie”. A
future Overwatch recipe-saving action targets Mealie. Obsidian remains useful
for cooking techniques, appliance notes, dietary policy and other prose that
does not belong in a recipe database.

Grocy is a sensible stocktaking candidate because it models products, locations,
stock, best-before dates, shopping and consumption, but deployment remains a
separate decision. This avoids forcing two overlapping shopping-list models into
production before the household workflow is clear.
