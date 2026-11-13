const { test, expect } = require('@playwright/test');
const fs = require('node:fs');
const path = require('node:path');
test('legacy dashboard URLs lead to authenticated HA without loading credentials', async () => {
  for (const name of ['ventsys-dashboard.html', 'ventsys-card-wrapper.html']) {
    const html = fs.readFileSync(path.resolve(__dirname, '../../../dashboards', name), 'utf8');
    expect(html).toContain('/dashboard-ventsys/0');
    expect(html).not.toContain('ventsys-config.js');
    expect(html).not.toContain('<script');
  }
});
