const { test, expect } = require("@playwright/test");
const fs = require("fs");
const path = require("path");

const dashboardPath = path.resolve(__dirname, "../../../dashboards/ventsys-dashboard.html");

test("dashboard startup uses command-free valve renderers", async () => {
  const html = fs.readFileSync(dashboardPath, "utf8");
  const init = html.match(/\/\/ Initialise all butterfly[\s\S]*?\/\/ ── Flow sensor colour/);
  expect(init).not.toBeNull();
  expect(init[0]).toContain("renderValveVisual(id, 0)");
  expect(init[0]).toContain("renderIntakeVisual(1, 0)");
  expect(init[0]).not.toContain("updateValveVisual(id, 0)");

  const valveRenderer = html.match(/function renderValveVisual[\s\S]*?\n  function updateValveVisual/);
  const intakeRenderer = html.match(/function renderIntakeVisual[\s\S]*?\n  function updateIntakeVisual/);
  expect(valveRenderer).not.toBeNull();
  expect(intakeRenderer).not.toBeNull();
  expect(valveRenderer[0]).not.toContain("haPublish(");
  expect(intakeRenderer[0]).not.toContain("haPublish(");
});

test("dashboard renders without a configured HA connection", async ({ page }) => {
  const browserErrors = [];
  page.on("pageerror", (error) => browserErrors.push(error.message));
  await page.goto(`file:///${dashboardPath.replace(/\\/g, "/")}`);
  await expect(page.locator("#current-mode")).toContainText("OFFLINE");
  await expect(page.locator("#valve-main-1-pos")).toContainText("0%");
  expect(browserErrors).toEqual([]);
  await expect(page.locator('body')).not.toContainText('HA TOKEN NOT SET');
});

test("offline controls do not claim that commands succeeded", async ({ page }) => {
  await page.goto(`file:///${dashboardPath.replace(/\\/g, "/")}`);
  const fanButton = page.locator("#fan-toggle");
  const before = await fanButton.textContent();

  await fanButton.evaluate((button) => button.click());

  await expect(fanButton).toHaveText(before);
  await expect(fanButton).toHaveClass(/off/);
  await expect(page.locator("#current-mode")).toContainText("OFFLINE");
});

test("safety modes are derived from complete HA actuator state", async () => {
  const html = fs.readFileSync(dashboardPath, "utf8");
  const startup = html.match(/\/\/ Actuator state is unknown[\s\S]*?\/\/ ── Flow sensor colour/);
  const reconciliation = html.match(/function reconcileSafetyModesFromHa[\s\S]*?\n  function haApplyState/);

  expect(startup).not.toBeNull();
  expect(startup[0]).not.toContain("activeModes.add('sealed')");
  expect(reconciliation).not.toBeNull();
  expect(reconciliation[0]).toContain("allFansOff && allValvesClosed");
  expect(reconciliation[0]).toContain("allFansOn && allValvesOpen");
});

test("live actuator state clears sealed mode and enables blocked-flow warning", async ({ page }) => {
  await page.goto(`file:///${dashboardPath.replace(/\\/g, "/")}`);
  await page.evaluate(() => {
    window._haConnected = true;
    const E = HA_CONFIG.entities;
    const apply = (entityId, state, attributes = {}) => haApplyState(entityId, { state, attributes });
    apply(E.fan_main, "off", { percentage: 50 });
    apply(E.fan_spray, "off", { percentage: 50 });
    [
      E.valve_main1,
      E.valve_main2,
      E.valve_fdm_branch,
      E.valve_fdm_print,
      E.valve_fdm_360,
      E.valve_sla_branch,
      E.valve_sla_print,
      E.valve_sla_360,
    ].forEach((entityId) => apply(entityId, "0"));
  });
  await expect(page.locator("#current-mode")).toContainText("SEALED");

  await page.evaluate(() => haApplyState(HA_CONFIG.entities.fan_main, { state: "on", attributes: { percentage: 50 } }));

  await expect(page.locator("#current-mode")).toContainText("MANUAL");
  await expect(page.locator("#warning-dialog-overlay")).toHaveClass(/active/, { timeout: 5000 });
});
