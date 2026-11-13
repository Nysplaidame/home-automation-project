// Run before deploying Homepage navigation or listener changes.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '..');
const js = fs.readFileSync(path.join(root, 'config/custom.js'), 'utf8');
const functions = js.slice(js.indexOf('  function getFrameHref('), js.indexOf('  function getPreviewDock('));
const ports = new Set([...Array.from({length: 30}, (_, i) => 8180 + i), 8211, 8212]);
for (const host of ['homepage.home.local', '192.168.20.102', '100.94.122.18']) {
  const context = {URL, window: {location: {hostname: host}}, PREVIEW_PROXY_PORT_SET: ports,
    PREVIEW_PROXY_PORTS: new Map([['192.168.20.102:8000', 8207]])};
  vm.createContext(context);
  vm.runInContext(functions, context);
  for (const port of [8180, 8188, 8190, 8202, 8207, 8209, 8211]) {
    const href = `https://homepage.home.local:${port}/nested/path?q=one#two`;
    const actual = context.getDirectHref({id: 'portal-example'}, href);
    assert.equal(actual, `https://${host}:${port}/nested/path?q=one#two`);
    assert.equal(actual, context.getFrameHref(href));
  }
  for (const service of ['troubleshooting', 'qbittorrent']) {
    const href = `https://homepage.home.local/portal-preview/${service}/`;
    assert.equal(context.getDirectHref({id: `portal-${service}`}, href), href);
  }
  assert.equal(context.getFrameHref('http://192.168.20.102:8000/'), `https://${host}:8207/`);
  assert.equal(context.getDirectHref({id:'portal-ventsys'}, 'https://homepage.home.local:8188/dashboard-ventsys/0'), `https://${host}:8188/dashboard-ventsys/0`);
}
const yaml = fs.readFileSync(path.join(root, 'config/services.yaml'), 'utf8');
for (const match of yaml.matchAll(/^\s+href:\s+(\S+)/gm)) {
  const url = new URL(match[1]);
  assert.equal(url.protocol, 'https:');
  assert.ok(['homepage.home.local', 'vault.home.local'].includes(url.hostname));
  assert.notEqual(url.port, '8181', '8181 belongs to native Tailscale Serve');
}
const nginx = fs.readFileSync(path.join(root, 'preview-proxy/nginx.conf'), 'utf8');
assert.match(nginx, /listen 8207 ssl;/);
assert.match(nginx, /listen 192\.168\.20\.102:8181 ssl;/);
assert.doesNotMatch(nginx, /listen (?:100\.94\.122\.18:)?8181 ssl;/);
assert.doesNotMatch(js, /DIRECT_SERVICE_(?:ORIGINS|OVERRIDES)/);
const grocy = nginx.slice(nginx.indexOf('    listen 8198 ssl;'), nginx.indexOf('  server { listen 8199'));
assert.match(grocy, /proxy_set_header Host \$http_host;/);
assert.doesNotMatch(grocy, /include \/etc\/nginx\/proxy-common\.conf/);
console.log('PASS: standalone/preview parity, paths, LAN/tailnet origins, scoped URLs, listener ownership');
