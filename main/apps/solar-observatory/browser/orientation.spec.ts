import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { Quaternion, Vector3 } from "three";

const samples = JSON.parse(readFileSync(new URL("../tests/fixtures/orientations.json", import.meta.url), "utf8")).samples;

test("rendered Earth and Moon attitude follows reference epoch without rotating their orbit frame", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  const rotations: Quaternion[] = [];
  for (const utc of ["2026-10-04T00:00:00Z", "2026-10-04T02:00:00Z"]) {
    await page.goto(`/?reference=1&time=${encodeURIComponent(utc)}`);
    await expect(page.locator("body")).toHaveAttribute("data-ready", "true");
    await page.locator("#mode").click();
    await page.waitForTimeout(100);
    const d = await page.evaluate(() => (window as any).observatoryDiagnostics());
    expect(d.orientationAvailable).toBe(true);
    expect(d.pathErrorPixels).toBeLessThan(1);
    for (const body of ["earth", "moon"]) {
      const expected = samples.find((s: any) => s.body === body && s.utc === utc).axes;
      const rotation = new Quaternion().fromArray(body === "earth" ? d.planetRotation : d.moonRotation);
      const prime = new Vector3(1, 0, 0).applyQuaternion(rotation);
      const north = new Vector3(0, 1, 0).applyQuaternion(rotation);
      expect(prime.distanceTo(new Vector3(expected.x[0], expected.x[2], -expected.x[1]))).toBeLessThan(1e-10);
      expect(north.distanceTo(new Vector3(expected.z[0], expected.z[2], -expected.z[1]))).toBeLessThan(1e-10);
      if (body === "earth") rotations.push(rotation);
    }
    await expect(page.getByRole("status")).toContainText("VentSys offline");
  }
  expect(rotations[0].angleTo(rotations[1])).toBeGreaterThan(0.5);
  expect(rotations[0].angleTo(rotations[1])).toBeLessThan(0.54);
});

test("unsupported attitude date keeps geometry and safety available but labels the fallback", async ({ page }) => {
  // Synthetic future trajectory timestamps isolate orientation-coverage failure.
  await page.route("**/data/reference.json", async route => {
    const response = await route.fetch();
    const data = await response.json();
    const offset = Date.parse("2028-10-04T00:00:00Z") - Date.parse("2026-10-04T00:00:00Z");
    for (const segment of data.segments) for (const sample of segment.samples) sample.utcMs += offset;
    await route.fulfill({ json: data });
  });
  await page.goto("/?reference=1&time=2028-10-04T01:00:00Z");
  await expect(page.locator("body")).toHaveAttribute("data-ready", "true");
  await expect(page.locator("body")).toHaveAttribute("data-surfaces", "ready");
  await expect(page.locator("#view-note")).toContainText("orientation unavailable");
  await expect(page.locator("#failure")).toBeHidden();
  await expect(page.getByRole("status")).toContainText("VentSys offline");
  expect(await page.evaluate(() => (window as any).observatoryDiagnostics().orientationAvailable)).toBe(false);
});
