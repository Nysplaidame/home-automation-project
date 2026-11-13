import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./browser",
  timeout: 45000,
  workers: 1,
  use: { baseURL: "http://127.0.0.1:4176", browserName: "chromium", viewport: { width: 800, height: 480 }, screenshot: "only-on-failure" },
  webServer: { command: "npm run stage:data && npx vite --host 127.0.0.1 --port 4176 --strictPort", url: "http://127.0.0.1:4176", reuseExistingServer: false, timeout: 60000 },
});
