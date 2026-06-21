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
- **Grocy** owns pantry, fridge and freezer quantities, expiry dates, purchases
  and consumption. Its optional Mealie/HA integrations remain future work.
- **Home Assistant and Overwatch** are orchestration and conversational layers,
  not systems of record. Future tools should call scoped Mealie or inventory
  APIs and require confirmation before creating or changing household data.

## Consequences

Recipes should no longer be described as destined for “Obsidian or Mealie”. A
future Overwatch recipe-saving action targets Mealie. Obsidian remains useful
for cooking techniques, appliance notes, dietary policy and other prose that
does not belong in a recipe database.

Grocy and Mealie may both expose shopping-list features, but Grocy owns stock
replenishment while Mealie owns recipe-derived planning. Integration should not
silently merge or overwrite either list.
