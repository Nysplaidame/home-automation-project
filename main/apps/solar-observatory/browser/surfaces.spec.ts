import { test, expect } from "@playwright/test";

test("local maps decode, remain bounded across focus cycles and sky fills the viewport", async ({ page }) => {
  const external: string[] = [];
  page.on("request", request => { if (!request.url().startsWith("http://127.0.0.1:")) external.push(request.url()); });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/?reference=1");
  await expect(page.locator("body")).toHaveAttribute("data-ready", "true");
  await expect(page.locator("body")).toHaveAttribute("data-surfaces", "ready");
  await expect(page.locator("#view-note")).toContainText("approximate IAU orientation");
  expect(await page.locator("#sky").evaluate((img: HTMLImageElement) => img.complete && img.naturalWidth > 1000)).toBe(true);
  const sky = await page.locator("#sky").boundingBox();
  expect(sky).toEqual(await page.locator("#viewport").boundingBox());
  // Warm every material/render path before comparing total renderer allocations.
  for (let i = 0; i < 6; i++) { await page.locator("#next").click(); await page.waitForTimeout(80); }
  const baseline = await page.evaluate(() => (window as any).observatoryDiagnostics().textures);
  for (let i = 0; i < 24; i++) await page.locator("#next").click();
  await page.waitForTimeout(150);
  const textures = await page.evaluate(() => (window as any).observatoryDiagnostics().textures);
  expect(textures).toBeGreaterThan(0);
  expect(textures).toBeLessThanOrEqual(baseline);
  expect(external).toEqual([]);
});

test("failed surface requests retain astronomy and the independent safety display", async ({ page }) => {
  await page.route("**/assets/earth.jpg", route => route.fulfill({ status: 503, body: "Unavailable" }));
  await page.goto("/?reference=1");
  await expect(page.locator("body")).toHaveAttribute("data-ready", "true");
  await expect(page.locator("body")).toHaveAttribute("data-surfaces", "partial");
  await expect(page.locator("#view-note")).toContainText("fallback");
  await expect(page.locator("#failure")).toBeHidden();
  await expect(page.getByRole("status")).toContainText("VentSys offline");
  await page.locator("#next").click();
  await expect(page.locator("body")).toHaveAttribute("data-mode", "system");
});

test("late maps do not attach to disposed focus materials", async ({ page }) => {
  let release!: () => void;
  const gate = new Promise<void>(resolve => { release = resolve; });
  await page.route("**/assets/earth.jpg", async route => { await gate; await route.continue(); });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.goto("/?reference=1");
  await expect(page.locator("body")).toHaveAttribute("data-ready", "true");
  await page.locator("#target").selectOption("saturn");
  release();
  await expect(page.locator("body")).toHaveAttribute("data-surfaces", "ready");
  await expect(page.locator("body")).toHaveAttribute("data-target", "saturn");
  await expect(page.locator("#view-note")).toContainText("matte geometry");
  await page.locator("#target").selectOption("earth");
  await expect(page.locator("#view-note")).toContainText("NASA surface map");
  await expect(page.locator("#failure")).toBeHidden();
});
