const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '../../../dashboards');
async function openCard(page, options = {}) {
  await page.route('**/*', route => {
    const url = new URL(route.request().url());
    if (url.pathname === '/harness') return route.fulfill({ contentType: 'text/html', body: '<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>VentSys fixture</title><style>body{margin:0;background:#080f18}ventsys-dashboard-card{display:block;max-width:1400px;margin:auto}</style></head><body><script type="module" src="/ventsys-card.js"></script></body></html>' });
    const name = url.pathname.slice(1);
    if (!/^ventsys-[a-z-]+\.(js|mjs|css|svg)$/.test(name) || !fs.existsSync(path.join(root,name))) return route.fulfill({ status: 404, body: '' });
    return route.fulfill({ contentType: name.endsWith('.css') ? 'text/css' : name.endsWith('.svg') ? 'image/svg+xml' : 'text/javascript', body: fs.readFileSync(path.join(root,name),'utf8') });
  });
  await page.goto('http://ventsys.test/harness');
  await page.evaluate(async options => {
    const model = await import('/ventsys-model.mjs?v=20261027-1');
    const stamp = new Date(Date.now()-1000).toISOString();
    const state = (value, unit='', attributes={}) => ({ state: String(value), last_updated: stamp, attributes: {unit_of_measurement:unit,...attributes} });
    const states = { 'input_boolean.ventsys_failsafe': state('off'), 'script.ventsys_mode_fire_safe': state('off'), 'script.ventsys_normal_command': state('off'), 'script.ventsys_set_operating_mode':state('off'), 'script.ventsys_test_valves':state('off'), 'script.ventsys_record_intake_reference':state('off'), 'binary_sensor.garage_ventsys_sla_360_intake_valve_pwm_commanded_active':state('off'), 'binary_sensor.garage_ventsys_fdm_360_intake_valve_pwm_commanded_active':state('off'), 'input_text.ventsys_operating_state':state(JSON.stringify({fdm:'off',sla:'off',booth:'off',revision:0})), 'input_text.ventsys_operating_result':state('No operating requests') };
    for (const d of model.DEVICE_LIST) states[d.native[0] || d.entity] = state(d.fan ? 'off' : d.expectedRange ? 45 : 50, '', { min:d.expectedRange?.min ?? 0,max:d.expectedRange?.max ?? 100,percentage:50 });
    for (const zone of Object.values(model.SENSORS)) for (const [kind,ids] of Object.entries(zone)) if (Array.isArray(ids)) states[ids[0]] = state(({temperature:21.4,humidity:44,baro:1013,differential:-8,gas:90000,wheel:2,smoke:'off'})[kind], ({temperature:'°C',humidity:'%',baro:'hPa',differential:'Pa',gas:'Ω',wheel:'rounds/s',smoke:''})[kind]);
    window.calls = [];
    window.fixture = { states, connection:{ connected:options.connected !== false }, callService:async (...args) => { window.calls.push(args); if(window.rejectCommand) throw new Error('Synthetic failure'); } };
    window.card = document.createElement('ventsys-dashboard-card');window.card.setConfig({type:'custom:ventsys-dashboard-card',layout:options.layout || 'standard'});document.body.append(window.card);window.card.hass=window.fixture;
  }, options);
  await page.locator('ventsys-dashboard-card #device-name').waitFor({state:options.layout === 'touch' ? 'attached' : 'visible'});
  await page.locator('ventsys-dashboard-card #diagram').waitFor();
  return page.locator('ventsys-dashboard-card');
}
module.exports = { openCard };
