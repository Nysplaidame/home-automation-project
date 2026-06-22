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
  await expect(page.locator("#current-mode")).toContainText("SEALED");
  await expect(page.locator("#valve-main-1-pos")).toContainText("0%");
  expect(browserErrors).toEqual([]);
});
