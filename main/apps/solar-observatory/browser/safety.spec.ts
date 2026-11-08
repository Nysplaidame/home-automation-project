import { test, expect, type Page, type FrameLocator } from "@playwright/test";

async function openHost(page: Page): Promise<FrameLocator> {
  // Leave room for the external simulation toolbar as well as the 7-inch display.
  await page.setViewportSize({ width: 800, height: 660 });
  await page.goto("/mock-host.html");
  const child = page.frameLocator("iframe");
  await expect(child.locator("body")).toHaveAttribute("data-ready", "true");
  await expect(child.locator("body")).toHaveAttribute("data-safety", "offline");
  return child;
}

test("mock host forwards read-only state and alerts interrupt a moving camera", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", error => errors.push(error.message));
  const child = await openHost(page);
  await page.getByRole("button", { name: "Connect mock", exact: true }).click();
  await expect(child.locator("#safety-title")).toHaveText("Mock HA connected");
  await expect(child.locator("#safety-note")).toContainText("Monitoring incomplete");
  await expect(child.locator("#safety-tag")).toHaveText("SIMULATION");
  await child.locator("#mode").click();
  await page.waitForTimeout(500);
  await page.getByRole("button", { name: "Trigger failsafe" }).click();
  await expect(child.locator("body")).toHaveAttribute("data-safety", "critical");
  await expect(child.locator("#welcome")).toBeVisible();
  await expect(child.locator("#resume")).toBeDisabled();
  await expect(child.locator("#next")).toBeDisabled();
  await expect(child.locator("#welcome-title")).toContainText("Simulation");
  await page.screenshot({ path: "test-results/mock-failsafe.png" });
  await page.getByRole("button", { name: "Disconnect mock" }).click();
  await expect(child.locator("body")).toHaveAttribute("data-safety", "offline");
  await expect(child.locator("#welcome-title")).toContainText("Status lost");
  await expect(child.locator("#resume")).toBeDisabled();
  await page.getByRole("button", { name: "Reload display" }).click();
  await expect(child.locator("body")).toHaveAttribute("data-ready", "true");
  await expect(child.locator("#welcome-title")).toContainText("Status lost");
  await expect(child.locator("#resume")).toBeDisabled();
  await page.getByRole("button", { name: "Clear failsafe" }).click();
  await expect(child.locator("#resume")).toBeDisabled();
  await page.getByRole("button", { name: "Connect mock", exact: true }).click();
  await expect(child.locator("#welcome-title")).toContainText("Failsafe cleared");
  await expect(child.locator("#resume")).toBeEnabled();
  await expect(child.locator("#welcome")).toBeVisible();
  await child.locator("#resume").click();
  await expect(child.locator("#welcome")).toBeHidden();
  expect(await page.evaluate(() => (window as any).mockHostDiagnostics().commandCalls)).toBe(0);
  expect(errors).toEqual([]);
});

test("lost delivery expires state while unchanged heartbeats keep it current", async ({ page }) => {
  test.setTimeout(60000);
  const child = await openHost(page);
  await page.getByRole("button", { name: "Connect mock", exact: true }).click();
  await expect(child.locator("body")).toHaveAttribute("data-safety", "connected");
  // Exercise actual postMessage scheduling across documents; mocked per-frame
  // clocks can diverge and are not an adequate integration freshness proof.
  await page.waitForTimeout(16000);
  await expect(child.locator("body")).toHaveAttribute("data-safety", "connected");
  await page.getByRole("button", { name: "Pause delivery" }).click();
  await page.waitForTimeout(16000);
  await expect(child.locator("body")).toHaveAttribute("data-safety", "offline");
  await expect(child.locator("#safety-note")).toHaveText("Live safety status unavailable");
  await page.getByRole("button", { name: "Resume delivery" }).click();
  await expect(child.locator("body")).toHaveAttribute("data-safety", "connected");
});

test("reload changes session and old envelopes cannot restore trust", async ({ page }) => {
  const child = await openHost(page);
  await page.getByRole("button", { name: "Connect mock", exact: true }).click();
  await expect(child.locator("body")).toHaveAttribute("data-safety", "connected");
  const oldSession = await child.locator("html").getAttribute("data-observatory-session");
  await page.getByRole("button", { name: "Reload display" }).click();
  await expect(child.locator("html")).not.toHaveAttribute("data-observatory-session", oldSession!);
  await expect(child.locator("body")).toHaveAttribute("data-safety", "connected");
  await page.evaluate(sessionId => {
    const frame = document.querySelector("observatory-readonly-card")!.shadowRoot!.querySelector("iframe")!;
    frame.contentWindow!.postMessage({ version: 1, type: "state_snapshot", sessionId, sequence: 99,
      issuedAtMs: Date.now(), expiresAtMs: Date.now() + 15000,
      state: { failsafe: "off", fan: "on", monitoring: "available" },
    }, location.origin);
  }, oldSession);
  await expect(child.locator("body")).toHaveAttribute("data-safety", "offline");
});

test("wrong source and origin cannot change status; malformed trusted messages clear it", async ({ page }) => {
  const child = await openHost(page);
  await page.getByRole("button", { name: "Connect mock", exact: true }).click();
  await expect(child.locator("body")).toHaveAttribute("data-safety", "connected");
  const frame = page.frames().find(f => f.url().includes("bridge=read-only-v1"))!;
  await frame.evaluate(() => {
    window.postMessage({ type: "offline" }, location.origin);
    window.dispatchEvent(new MessageEvent("message", { origin: "https://wrong.test", source: parent, data: { type: "offline" } }));
  });
  await expect(child.locator("body")).toHaveAttribute("data-safety", "connected");
  await page.evaluate(() => {
    const frame = document.querySelector("observatory-readonly-card")!.shadowRoot!.querySelector("iframe")!;
    frame.contentWindow!.postMessage({ type: "service-call", entity: "fan.inline_fan" }, location.origin);
  });
  await expect(child.locator("body")).toHaveAttribute("data-safety", "offline");
  expect(await page.evaluate(() => (window as any).mockHostDiagnostics().commandCalls)).toBe(0);
});

test("alerts remain visible after WebGL failure and no command API is contacted", async ({ page }) => {
  const forbiddenRequests: string[] = [];
  page.on("request", request => { if (/\/api\/(services|websocket)/.test(request.url())) forbiddenRequests.push(request.url()); });
  const child = await openHost(page);
  await page.getByRole("button", { name: "Connect mock", exact: true }).click();
  await child.locator("canvas").dispatchEvent("webglcontextlost");
  await expect(child.locator("#failure")).toBeVisible();
  await page.getByRole("button", { name: "Trigger failsafe" }).click();
  await expect(child.locator("#welcome-title")).toContainText("failsafe reported");
  await expect(child.locator("#safety-title")).toHaveText("Failsafe active");
  await expect(child.locator("#resume")).toBeDisabled();
  expect(forbiddenRequests).toEqual([]);
  expect(await page.evaluate(() => (window as any).mockHostDiagnostics().commandCalls)).toBe(0);
});

test("only minimal fields cross the frame boundary; child command requests are ignored", async ({ page }) => {
  const child = await openHost(page);
  const frame = page.frames().find(f => f.url().includes("bridge=read-only-v1"))!;
  await frame.evaluate(() => {
    (window as any).received = [];
    window.addEventListener("message", event => { (window as any).received.push(event.data); });
    parent.postMessage({ type: "service-call", kind: "mqtt-publish", topic: "ventsys/test", payload: "on" }, location.origin);
  });
  await page.getByRole("button", { name: "Connect mock", exact: true }).click();
  await expect(child.locator("body")).toHaveAttribute("data-safety", "connected");
  const messages = await frame.evaluate(() => (window as any).received as Record<string, unknown>[]);
  const snapshots = messages.filter(m => m.type === "state_snapshot");
  expect(snapshots.length).toBeGreaterThan(0);
  for (const message of snapshots) {
    expect(Object.keys(message).sort()).toEqual(["expiresAtMs", "issuedAtMs", "sequence", "sessionId", "state", "type", "version"]);
    expect(Object.keys(message.state as object).sort()).toEqual(["failsafe", "fan", "monitoring"]);
  }
  expect(JSON.stringify(messages)).not.toContain("private-test-value");
  expect(await page.evaluate(() => (window as any).mockHostDiagnostics().commandCalls)).toBe(0);
});

test("host rejects external, credential-bearing and unexpected frame URLs", async ({ page }) => {
  await openHost(page);
  const rejected = await page.evaluate(() => {
    const card = document.querySelector("observatory-readonly-card") as HTMLElement & { setConfig: (config: { observatory_url: string }) => void };
    return ["https://outside.test/index.html", "javascript:alert(1)", "/index.html?token=forbidden", "/index.html#secret", "/other-page.html"].map(url => {
      try { card.setConfig({ observatory_url: url }); return false; } catch { return true; }
    });
  });
  expect(rejected).toEqual([true, true, true, true, true]);
});
