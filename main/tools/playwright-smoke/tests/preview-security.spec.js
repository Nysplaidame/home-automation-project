const { test, expect } = require('@playwright/test');
const { createPreviewServer } = require('../scripts/preview-screensaver');
test('preview serves only dashboard content and explicit vendor assets', async ({ request }) => {
  const server = createPreviewServer();
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}`;
  try {
    expect((await request.get(base + '/assets/vendor/three.module.min.js')).status()).toBe(200);
    expect((await request.get(base + '/tools/router-deploy/keys/private_key')).status()).toBe(403);
    expect((await request.get(base + '/tools/router-deploy/deploy.ps1')).status()).toBe(403);
    expect((await request.get(base + '/%ZZ')).status()).toBe(400);
  } finally { await new Promise(resolve => server.close(resolve)); }
});
