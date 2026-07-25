# Custom Site Background Themes

These small CSS layers preserve each custom app's own component system while
giving its page canvas a subject-specific background.

| App | Theme | Live source target |
|---|---|---|
| GardenKeeper | foliage, soil and water | `/opt/stacks/gardenkeeper/source/apps/web/src/site-background.css` |
| Household Hub | connected knowledge constellations | `/opt/stacks/household-hub/apps/web/src/site-background.css` |
| Transfer Portal | light transfer-grid and data-route glow | `apps/transferportal/transferportal/app.py` |

Both files are imported after each app's base `styles.css`. Rebuild the
respective Docker stack after deployment. Third-party products are deliberately
excluded. Transfer Portal's source is ready locally but requires the native OMV
deployment procedure before it can become live.
