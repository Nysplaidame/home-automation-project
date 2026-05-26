// @ts-check
const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests",
  timeout: 30000,
  reporter: [["list"]],
  use: {
    browserName: "chromium",
    viewport: { width: 800, height: 480 },
    screenshot: "only-on-failure",
    trace: "retain-on-failure"
  }
});
