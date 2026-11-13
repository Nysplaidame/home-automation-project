const http = require("http");
const fs = require("fs");
const path = require("path");

const root = path.resolve(__dirname, "../../../dashboards");
const port = Number(process.env.PORT || 4173);

const contentTypes = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".svg": "image/svg+xml",
  ".css": "text/css; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp"
};

function createPreviewServer() { return http.createServer((req, res) => {
  let requested;
  try { requested = decodeURIComponent(new URL(req.url, `http://127.0.0.1:${port}`).pathname); }
  catch (_) { res.writeHead(400); res.end('Invalid path'); return; }
  const vendor = new Map(['three.module.min.js', 'three.core.min.js'].map(name => [`/assets/vendor/${name}`, path.resolve(__dirname, '../../../assets/vendor', name)]));
  const safePath = path.normalize(requested).replace(/^(\.\.[/\\])+/, "");
  const filePath = vendor.get(requested) || path.join(root, safePath === "/" ? "ventsys_solar_screensaver.html" : safePath);

  if ((!vendor.has(requested) && !filePath.startsWith(root + path.sep)) || !['.html', '.js', '.mjs', '.css', '.png', '.jpg', '.jpeg', '.webp', '.svg'].includes(path.extname(filePath))) {
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
}); }

if (require.main === module) createPreviewServer().listen(port, "127.0.0.1", () => {
  console.log(`Screensaver preview: http://127.0.0.1:${port}/ventsys_solar_screensaver.html`);
});
module.exports = { createPreviewServer };
