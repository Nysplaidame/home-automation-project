import { test, expect, type Page } from "@playwright/test";

type Diagnostics = {
  target: string; system: boolean; replay: boolean; paused: boolean; failed: boolean;
  pathErrorPixels: number | null; canvasCount: number; geometries: number; meshes: number;
  pathSamples: number; moon?: number[]; planet: number[]; position: number[];
};
const diagnostic = (page: Page) => page.evaluate(() => (window as unknown as { observatoryDiagnostics: () => Diagnostics }).observatoryDiagnostics());
async function ready(page: Page): Promise<void> {
  await page.goto("/?reference=1");
  await expect(page.locator("body")).toHaveAttribute("data-ready", "true");
  await expect(page.locator("#failure")).toBeHidden();
  await page.waitForTimeout(100);
}

for (const size of [{ width: 800, height: 480 }, { width: 1024, height: 600 }, { width: 390, height: 844 }]) {
  test(`focus cycle and projected paths at ${size.width}x${size.height}`, async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", error => errors.push(error.message));
    await page.setViewportSize(size);
    await page.emulateMedia({ reducedMotion: "reduce" });
    await ready(page);
    await expect(page.locator("#data-state")).toContainText("not live");
    const expected = [["earth", false], ["earth", true], ["jupiter", false], ["jupiter", true], ["saturn", false], ["saturn", true]] as const;
    for (const [target, system] of expected) {
      await expect(page.locator("body")).toHaveAttribute("data-target", target);
      await expect(page.locator("body")).toHaveAttribute("data-mode", system ? "system" : "portrait");
      await page.waitForTimeout(100);
      const d = await diagnostic(page);
      expect(d.failed).toBe(false);
      expect(d.canvasCount).toBe(1);
      expect(d.planet.every(Number.isFinite)).toBe(true);
      expect(Math.abs(d.planet[0])).toBeLessThan(1);
      expect(Math.abs(d.planet[1])).toBeLessThan(1);
      if (system && target !== "saturn") {
        expect(d.pathErrorPixels).toBeLessThan(1);
        expect(d.pathSamples).toBeGreaterThan(20);
        expect(Math.abs(d.moon![0])).toBeLessThan(1);
        expect(Math.abs(d.moon![1])).toBeLessThan(1);
        await expect(page.locator(".object-label", { hasText: target === "earth" ? "Moon" : "Io" })).toBeVisible();
      }
      await expect(page.getByRole("status")).toContainText("Live safety status unavailable");
      await page.screenshot({ path: `test-results/${size.width}-${target}-${system ? "system" : "portrait"}.png` });
      await page.getByRole("button", { name: "Next focus" }).click();
    }
    await expect(page.locator("body")).toHaveAttribute("data-target", "earth");
    expect(errors).toEqual([]);
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  });
}

test("mouse movement does not wake; click and keyboard controls do not double advance", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await ready(page);
  await page.mouse.move(100, 180);
  await page.mouse.move(350, 250);
  await expect(page.locator("#welcome")).toBeHidden();
  await page.locator("#next").focus();
  await page.keyboard.press("Enter");
  await expect(page.locator("body")).toHaveAttribute("data-target", "earth");
  await expect(page.locator("body")).toHaveAttribute("data-mode", "system");
  await expect(page.locator("#welcome")).toBeHidden();
  await page.locator("canvas").click({ position: { x: 100, y: 100 } });
  await expect(page.locator("#welcome")).toBeVisible();
  await page.getByRole("button", { name: "Return to observatory" }).click();
  await expect(page.locator("#welcome")).toBeHidden();
});

test("focus cycling releases GPU geometry instead of accumulating resources", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await ready(page);
  const before = (await diagnostic(page)).geometries;
  for (let i = 0; i < 24; i++) await page.locator("#next").click();
  await page.waitForTimeout(100);
  const after = await diagnostic(page);
  expect(after.geometries).toBeLessThanOrEqual(before + 1);
  expect(after.canvasCount).toBe(1);
});

test("unavailable data and graphics failure retain offline safety strip", async ({ page }) => {
  await page.route("**/data/*.json", route => route.fulfill({ status: 503, body: "Unavailable" }));
  await page.goto("/?reference=1");
  await expect(page.locator("#failure")).toBeVisible();
  await expect(page.getByRole("status")).toContainText("VentSys offline");
  await page.unroute("**/data/*.json");
  await ready(page);
  await page.locator("canvas").dispatchEvent("webglcontextlost");
  await expect(page.locator("#failure")).toContainText("Graphics context lost");
  await expect(page.getByRole("status")).toContainText("Live safety status unavailable");
});

test("focus camera moves gradually rather than jumping to the new fit", async ({ page }) => {
  await ready(page);
  const initial = (await diagnostic(page)).position;
  await page.locator("#mode").click();
  await page.waitForTimeout(500);
  const early = (await diagnostic(page)).position;
  expect(Math.hypot(...early.map((x, i) => x - initial[i]))).toBeLessThan(0.1);
  await page.waitForTimeout(2000);
  const later = (await diagnostic(page)).position;
  expect(Math.hypot(...later.map((x, i) => x - initial[i]))).toBeGreaterThan(0.1);
});
