const { test, expect } = require("@playwright/test");
const http = require("http");
const fs = require("fs");
const path = require("path");
const { PNG } = require("pngjs");

test("screensaver renders with canvas and safety strip", async ({ page }) => {
  const browserErrors = [];
  page.on("console", (message) => {
    if (message.type() === "error" && !message.text().includes("favicon")) browserErrors.push(message.text());
  });
  page.on("pageerror", (error) => browserErrors.push(error.message));
  const root = path.resolve(__dirname, "../../..");
  const server = http.createServer((req, res) => {
    const requested = decodeURIComponent(new URL(req.url, "http://127.0.0.1").pathname);
    const safePath = path.normalize(requested).replace(/^(\.\.[/\\])+/, "");
    const filePath = path.join(root, safePath === "/" ? "ventsys_solar_screensaver.html" : safePath);
    if (!filePath.startsWith(root)) {
      res.writeHead(403);
      res.end("Forbidden");
      return;
    }
    fs.readFile(filePath, (err, data) => {
      if (err) {
        res.writeHead(404);
        res.end("Not found");
        return;
      }
      const ext = path.extname(filePath);
      res.writeHead(200, { "content-type": ext === ".js" ? "text/javascript" : ext === ".html" ? "text/html" : "application/octet-stream" });
      res.end(data);
    });
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const { port } = server.address();

  try {
    await page.goto(`http://127.0.0.1:${port}/ventsys_solar_screensaver.html`);
    await page.waitForTimeout(1800);

    await expect(page.locator("#scene")).toBeVisible();
    await expect(page.locator("#status-main")).toContainText("VentSys:");
    await expect(page.locator("#ha-chip")).toContainText("HA");

    await page.locator("#focus-control").click();
    await expect(page.locator("#caption")).toHaveClass(/visible/);
    await expect(page.locator("#focus-scene")).toHaveClass(/visible/);
    await page.waitForTimeout(1200);

    const screenshot = await page.screenshot({ fullPage: false });
    const png = PNG.sync.read(screenshot);
    let brightPixels = 0;
    for (let i = 0; i < png.data.length; i += 4) {
      const r = png.data[i];
      const g = png.data[i + 1];
      const b = png.data[i + 2];
      if (r + g + b > 90) brightPixels++;
    }
    expect(brightPixels).toBeGreaterThan(7000);
    expect(browserErrors).toEqual([]);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});
