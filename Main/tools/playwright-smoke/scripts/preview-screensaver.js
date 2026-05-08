const http = require("http");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "../../..");
const port = Number(process.env.PORT || 4173);

const contentTypes = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp"
};

const server = http.createServer((req, res) => {
  const requested = decodeURIComponent(new URL(req.url, `http://127.0.0.1:${port}`).pathname);
  const safePath = path.normalize(requested).replace(/^(\.\.[/\\])+/, "");
  const filePath = path.join(root, safePath === "/" ? "ventsys_solar_screensaver.html" : safePath);

  if (!filePath.startsWith(root)) {
    res.writeHead(403);
    res.end("Forbidden");
    return;
  }

  fs.readFile(filePath, (error, data) => {
    if (error) {
      res.writeHead(404);
      res.end("Not found");
      return;
    }
    res.writeHead(200, { "content-type": contentTypes[path.extname(filePath)] || "application/octet-stream" });
    res.end(data);
  });
});

server.listen(port, "127.0.0.1", () => {
  console.log(`Screensaver preview: http://127.0.0.1:${port}/ventsys_solar_screensaver.html`);
});
