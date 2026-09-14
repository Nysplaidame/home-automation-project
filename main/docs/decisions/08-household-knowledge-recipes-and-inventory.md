---
title: Household Knowledge, Recipes and Food Inventory
description: Defines ownership and voice routing across household knowledge, recipes, inventory, and garden operations
tags: [architecture-decision, obsidian, mealie, food-inventory, grocy, gardenkeeper, voice]
created: 2026-06-21
modified: 2026-07-12
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
  not systems of record. Tools should call scoped Mealie or inventory APIs.
  Voice access may add/list Grocy shopping-list items, but stock purchase,
  consumption, correction, inventory counts, deletion, and completion actions
  require a future confirmation-gated workflow.
- **GardenKeeper** is the system of record for plants, garden observations,
  garden schedules, and garden tasks. Its assistant endpoint is deterministic;
  it does not call a model and confirmation-gates ambiguous or destructive task
  changes.
- **Household Hub** owns indexed household knowledge and research workflows. Its
  Home Assistant surface is read-only and cannot mutate GardenKeeper, Mealie,
  Grocy, or Home Assistant.

## Voice tool routing

| Request | Tool owner | Rule |
|---|---|---|
| Current garden state or garden task operation | GardenKeeper | Use `garden_tasks`; preserve its confirmation options and token |
| General gardening or household advice with local provenance | Household Hub | Use `household_knowledge_query`; results are advisory and read-only |
| Recipe already saved | Mealie | Query Mealie directly |
| New recipe research | Household Hub | Use `household_recipe_research`; importing remains a separate explicit action |
| Shopping-list operation | Grocy | Add/list only under the existing voice policy |
| General current information | SearXNG | Use `web_search`; do not treat results as household state |
| Home state or control | Home Assistant | Use the native Assist API and its exposed-entity policy |

The local model on CT 114 interprets language and selects tools. It is not a
system of record and must not be given direct database credentials. Home
Assistant carries separate least-privilege credentials for GardenKeeper and
Household Hub so one integration cannot impersonate the other.

## Consequences

Recipes should no longer be described as destined for “Obsidian or Mealie”. A
future Overwatch recipe-saving action targets Mealie. Obsidian remains useful
for cooking techniques, appliance notes, dietary policy and other prose that
does not belong in a recipe database.

Grocy and Mealie may both expose shopping-list features, but Grocy owns stock
replenishment while Mealie owns recipe-derived planning. Integration should not
silently merge or overwrite either list.
