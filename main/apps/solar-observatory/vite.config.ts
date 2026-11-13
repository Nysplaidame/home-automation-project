import { defineConfig } from "vite";
import { fileURLToPath } from "node:url";

export default defineConfig({
  base: "./", server: { host: "127.0.0.1", port: 4175, strictPort: true },
  build: { rolldownOptions: { input: {
    index: fileURLToPath(new URL("./index.html", import.meta.url)),
    mock: fileURLToPath(new URL("./mock-host.html", import.meta.url)),
    "observatory-card": fileURLToPath(new URL("./src/observatory-card.ts", import.meta.url)),
  }, output: { entryFileNames: chunk => chunk.name === "observatory-card" ? "observatory-card.js" : "assets/[name]-[hash].js" } } },
});
