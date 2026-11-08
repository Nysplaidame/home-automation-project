const { test, expect } = require('@playwright/test');
const { openCard } = require('./ventsys-fixture.cjs');

test('startup and hydration cannot send commands; foreign messages have no command API', async ({ page }) => {
  const errors=[];page.on('pageerror',e=>errors.push(e.message));await openCard(page);
  await page.evaluate(()=>window.postMessage({channel:'ventsys-ha-bridge',type:'service-call',kind:'mqtt-publish',topic:'ventsys/fan/control',payload:'on'},'*'));
  await expect(page.locator('#connection')).toHaveText('HA connected');
  expect(await page.evaluate(()=>window.calls)).toEqual([]);expect(errors).toEqual([]);
});
test('offline controls cannot claim a successful operation', async ({ page }) => {
  await openCard(page,{connected:false});await expect(page.locator('#mode')).toHaveText('Offline');await expect(page.locator('#position-number')).toBeDisabled();await expect(page.locator('#device-value')).toHaveText('—');
  expect(await page.evaluate(()=>window.calls)).toEqual([]);
});
test('alarm popup lists latched boards and acknowledges only a healthy, inactive board', async ({ page }) => {
  await openCard(page);
  await page.evaluate(() => {
    const prefix = 'garage_ventsys_sla_pipe_air_sensor';
    const state = value => ({state:value,attributes:{friendly_name:'VentSys SLA Pipe Air Sensor alarm_latched'}});
    window.fixture.states[`binary_sensor.${prefix}_alarm_latched`] = state('on');
    window.fixture.states[`binary_sensor.${prefix}_co_detected`] = state('off');
    window.fixture.states[`binary_sensor.${prefix}_sensor_fault`] = state('off');
    window.fixture.states[`button.${prefix}_acknowledge_alarms`] = state('unknown');
    window.card.hass = {...window.fixture};
  });
  await expect(page.locator('#open-alarm-menu')).toContainText('(1)');
  await page.locator('#open-alarm-menu').click();
  await expect(page.locator('#latched-alarm-list')).toContainText('VentSys SLA Pipe Air Sensor');
  await page.evaluate(() => { window.fixture.states['binary_sensor.garage_ventsys_sla_pipe_air_sensor_co_detected'].state='on'; window.card.hass={...window.fixture}; });
  await expect(page.locator('#latched-alarm-list button')).toBeDisabled();
  await page.evaluate(() => { window.fixture.states['binary_sensor.garage_ventsys_sla_pipe_air_sensor_co_detected'].state='off'; window.card.hass={...window.fixture}; });
  await page.locator('#latched-alarm-list button').click();
  expect(await page.evaluate(() => window.calls)).toEqual([['button','press',{entity_id:'button.garage_ventsys_sla_pipe_air_sensor_acknowledge_alarms'}]]);
});
test('touch status menu exposes the alarm popup', async ({ page }) => {
  await openCard(page, {layout:'touch'});
  await page.locator('[data-touch-menu="status"]').click();
  await page.locator('#open-alarm-menu').click();
  await expect(page.locator('#alarm-menu')).toBeVisible();
  await expect(page.locator('#latched-alarm-list')).toContainText('No latched VentSys alarms');
});
test('CO detection with sensor fault displays an unverified red incident and source outline', async ({ page }) => {
  await openCard(page);
  await page.evaluate(() => {
    const prefix='garage_ventsys_sla_pipe_air_sensor';
    const make = value => ({state:value,attributes:{friendly_name:'VentSys SLA Pipe Air Sensor co_detected'}});
    window.fixture.states[`binary_sensor.${prefix}_co_detected`]=make('on');
    window.fixture.states[`binary_sensor.${prefix}_co_sensor_fault`]=make('on');
    window.card.hass={...window.fixture};
  });
  await expect(page.locator('#incident-symbol')).toContainText('2 active incidents');
  await expect(page.locator('#incident-list')).toContainText('unverified signal');
  await expect(page.locator('.sensor-zone[data-zone="sla"]')).toHaveAttribute('data-severity','red');
  await expect(page.locator('#events li[data-severity="red"]')).toHaveCount(1);
});
test('100% command opens one confirmation and a newer controller report', async ({ page }) => {
  await openCard(page);await page.locator('#position-number').fill('100');await page.locator('#position-number').press('Tab');
  await expect(page.locator('dialog[aria-labelledby="confirm-title"]')).toBeVisible();expect(await page.evaluate(()=>window.calls)).toEqual([]);
  await page.locator('#confirm-command').click();await expect(page.locator('#command-status')).toContainText('Pending');await expect(page.locator('#device-value')).toHaveText('50');
  expect(await page.evaluate(()=>window.calls)).toEqual([['script','ventsys_dashboard_command',{kind:'position',target:'main1',value:100}]]);
  await page.evaluate(()=>{const id='number.ventsys_main_duct_valve_1_valve_position';window.fixture.states[id]={...window.fixture.states[id],state:'100'};window.card.hass={...window.fixture};});
  await expect(page.locator('#command-status')).toContainText('Pending');
  await page.evaluate(()=>{const id='number.ventsys_main_duct_valve_1_valve_position';window.fixture.states[id]={...window.fixture.states[id],last_updated:new Date().toISOString()};window.card.hass={...window.fixture};});
  await expect(page.locator('#command-status')).toContainText('Confirmed by controller');
});
test('cancel sends no command and returns focus', async ({ page }) => {
  await openCard(page);await page.locator('#position-number').fill('75');await page.locator('#position-number').press('Tab');await page.locator('#cancel-command').click();expect(await page.evaluate(()=>window.calls)).toEqual([]);await expect(page.locator('dialog[aria-labelledby="confirm-title"]')).not.toBeVisible();
});
test('rejected request remains failed without changing reported position', async ({ page }) => {
  await openCard(page);await page.evaluate(()=>window.rejectCommand=true);await page.locator('#position-number').fill('75');await page.locator('#position-number').press('Tab');await page.locator('#confirm-command').click();await expect(page.locator('#command-status')).toContainText('Failed');await expect(page.locator('#device-value')).toHaveText('50');
});
test('missing confirmation expires, releases lock and permits retry', async ({ page }) => {
  await openCard(page);await page.clock.install();await page.locator('#position-number').fill('75');await page.locator('#position-number').press('Tab');await page.locator('#confirm-command').click();await page.clock.fastForward(12500);await expect(page.locator('#command-status')).toContainText('Timed out');await expect(page.locator('#position-number')).toBeEnabled();
});
test('disconnect clears displayed data and marks pending outcome unknown', async ({ page }) => {
  await openCard(page);await page.locator('#position-number').fill('75');await page.locator('#position-number').press('Tab');await page.locator('#confirm-command').click();await page.evaluate(()=>{window.fixture.connection.connected=false;window.card.hass={...window.fixture};});await expect(page.locator('#command-status')).toContainText('outcome unknown');await expect(page.locator('#device-value')).toHaveText('—');await expect(page.locator('[data-sensor="fdm-humidity"]')).toHaveText('Offline');
});
test('removal and remount do not retain the authenticated caller or send a request', async ({ page }) => {
  await openCard(page);await page.evaluate(()=>{window.card.remove();document.body.append(window.card);});await expect(page.locator('#connection')).toHaveText('Offline');expect(await page.evaluate(()=>window.calls)).toEqual([]);
});
test('unavailable native device cannot be masked by retained MQTT', async ({ page }) => {
  await openCard(page);await page.evaluate(()=>{window.fixture.states['number.ventsys_main_duct_valve_1_valve_position'].state='unavailable';window.fixture.states['number.main_duct_valve_1']={state:'100',attributes:{}};window.card.hass={...window.fixture};});await expect(page.locator('#device-value')).toHaveText('—');await expect(page.locator('#position-number')).toBeDisabled();
});
test('firmware endpoints are enforced before sending', async ({ page }) => {
  await openCard(page);await page.evaluate(()=>{window.fixture.states['number.ventsys_main_duct_valve_1_valve_position'].attributes.max=60;window.card.hass={...window.fixture};});await page.locator('#position-number').fill('100');await page.locator('#position-number').press('Tab');await expect(page.locator('#command-status')).toContainText('accepts controller targets');expect(await page.evaluate(()=>window.calls)).toEqual([]);
});
test('fallback clear cannot overwrite a smoke alarm; units stay separate', async ({ page }) => {
  await openCard(page);await page.evaluate(()=>{window.fixture.states['binary_sensor.garage_fdm_enclosure_sensor_fdm_enclosure_sensor_smoke_detected'].state='on';window.fixture.states['sensor.fdm_smoke']={state:'clear',last_updated:new Date().toISOString(),attributes:{}};window.card.hass={...window.fixture};});await expect(page.locator('[data-smoke="fdm"]')).toContainText('SMOKE DETECTED');await expect(page.locator('[data-sensor="fdm-baro"]')).toHaveText('1013 hPa');await expect(page.locator('[data-sensor="fdm-differential"]')).toHaveText('-8 Pa');await expect(page.locator('[data-sensor="fdm-gas"]')).toHaveText('90 kΩ');
});
test('sensor becomes stale and clears the value', async ({ page }) => {
  await openCard(page);await page.clock.install();await page.clock.fastForward(301000);await expect(page.locator('[data-sensor="fdm-humidity"]')).toHaveText('Stale');
});
test('failsafe locks controls, including an already-open confirmation', async ({ page }) => {
  await openCard(page);await page.locator('#position-number').fill('75');await page.locator('#position-number').press('Tab');await page.evaluate(()=>{window.fixture.states['input_boolean.ventsys_failsafe'].state='on';window.card.hass={...window.fixture};});await page.locator('#confirm-command').click();expect(await page.evaluate(()=>window.calls)).toEqual([]);await expect(page.locator('#command-status')).toContainText('Failsafe');
});
test('keyboard selection and labelled controls work', async ({ page }) => {
  await openCard(page);await page.locator('[data-device="sla_branch"]').focus();await page.keyboard.press('Enter');await expect(page.locator('#device-name')).toHaveText('SLA branch');await expect(page.getByLabel('Requested position')).toBeVisible();
});
test('all schematic devices are selectable and valve graphics follow reported values', async ({ page }) => {
  await openCard(page);
  await expect(page.locator('#diagram [data-select]')).toHaveCount(10);
  await page.locator('#diagram [data-select="main2"]').click();await expect(page.locator('#device-name')).toHaveText('Main duct 2');
  await page.evaluate(()=>{window.fixture.states['number.garage_ventsys_main_duct_valve_2_valve_position'].state='0';window.card.hass={...window.fixture};});
  await expect(page.locator('#ellipse-main-2')).toHaveAttribute('transform','rotate(90 1020 123)');
  await page.evaluate(()=>{window.fixture.states['number.garage_ventsys_main_duct_valve_2_valve_position'].state='100';window.card.hass={...window.fixture};});
  await expect(page.locator('#ellipse-main-2')).toHaveAttribute('transform','rotate(0 1020 123)');
});
test('mobile layout scrolls without horizontal clipping', async ({ page }) => {
  await page.setViewportSize({width:390,height:844});await openCard(page);const dimensions=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight}));expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.width);expect(dimensions.height).toBeGreaterThan(844);await expect(page.locator('[data-zone="ambient"]')).toBeAttached();
});
test('360 readback and acknowledgement stay with the corrected physical role', async ({ page }) => {
  await openCard(page);
  await page.evaluate(() => {
    window.fixture.states['number.ventsys_sla_360_intake_valve_valve_position'].state='41';
    window.fixture.states['number.ventsys_fdm_360_intake_valve_valve_position'].state='57';
    window.card.hass={...window.fixture};
  });
  await page.locator('[data-device="fdm_360"]').click();
  await expect(page.locator('#device-value')).toHaveText('36.7');
  await expect(page.locator('#position-slider')).toHaveAttribute('min','0');
  await expect(page.locator('#position-slider')).toHaveAttribute('max','100');
  await expect(page.locator('#fault-list')).not.toContainText('calibration');
  await page.locator('#position-number').fill('50');await page.locator('#position-number').press('Tab');await page.locator('#confirm-command').click();
  expect(await page.evaluate(()=>window.calls)).toEqual([['script','ventsys_dashboard_command',{kind:'position',target:'fdm_360',value:45}]]);
  await page.evaluate(()=>{const id='number.ventsys_fdm_360_intake_valve_valve_position';window.fixture.states[id]={...window.fixture.states[id],state:'45',last_updated:new Date().toISOString()};window.card.hass={...window.fixture};});
  await expect(page.locator('#command-status')).toContainText('Pending');
  await expect(page.locator('#device-value')).toHaveText('36.7');
  await page.evaluate(()=>{const id='number.ventsys_sla_360_intake_valve_valve_position';window.fixture.states[id]={...window.fixture.states[id],state:'45',last_updated:new Date().toISOString()};window.card.hass={...window.fixture};});
  await expect(page.locator('#command-status')).toContainText('Confirmed');
});

test('external dispatcher activity blocks review but not confirmation of our own request', async ({ page }) => {
  await openCard(page);
  await page.evaluate(()=>{window.fixture.states['script.ventsys_normal_command'].state='on';window.card.hass={...window.fixture};});
  await expect(page.locator('#position-number')).toBeDisabled();
  await expect(page.locator('#device-help')).toContainText('Another VentSys command');
  expect(await page.evaluate(()=>window.calls)).toEqual([]);
  await page.evaluate(()=>{window.fixture.states['script.ventsys_normal_command'].state='off';window.card.hass={...window.fixture};});
  await page.locator('#position-number').fill('75');await page.locator('#position-number').press('Tab');await page.locator('#confirm-command').click();
  await page.evaluate(()=>{window.fixture.states['script.ventsys_normal_command'].state='on';window.card.hass={...window.fixture};});
  await expect(page.locator('#command-status')).toContainText('Pending');
  await page.evaluate(()=>{const id='number.ventsys_main_duct_valve_1_valve_position';window.fixture.states[id]={...window.fixture.states[id],state:'75',last_updated:new Date().toISOString()};window.card.hass={...window.fixture};});
  await expect(page.locator('#command-status')).toContainText('Confirmed');
});

test('fire takeover interrupts pending confirmation before a matching report can claim success', async ({ page }) => {
  await openCard(page);
  await page.locator('#position-number').fill('75');await page.locator('#position-number').press('Tab');await page.locator('#confirm-command').click();
  await page.evaluate(()=>{const id='number.ventsys_main_duct_valve_1_valve_position';window.fixture.states[id]={...window.fixture.states[id],state:'75',last_updated:new Date().toISOString()};window.fixture.states['script.ventsys_mode_fire_safe'].state='on';window.card.hass={...window.fixture};});
  await expect(page.locator('#command-status')).toContainText('Interrupted');
  await expect(page.locator('#command-status')).toContainText('Fire response');
  await expect(page.locator('#command-status')).toHaveClass('failed');
  await expect(page.locator('#fault-title')).toContainText('Fire response running');
  await expect(page.locator('#faults')).toHaveClass('alarm');
  await expect(page.locator('#position-number')).toBeDisabled();
  await page.evaluate(()=>{window.fixture.states['script.ventsys_mode_fire_safe'].state='off';window.card.hass={...window.fixture};});
  await expect(page.locator('#command-status')).toContainText('Interrupted');
  expect(await page.evaluate(()=>window.calls.length)).toBe(1);
});

test('unknown failsafe interrupts pending requests without waiting for timeout', async ({ page }) => {
  await openCard(page);
  await page.locator('#position-number').fill('75');await page.locator('#position-number').press('Tab');await page.locator('#confirm-command').click();
  await page.evaluate(()=>{window.fixture.states['input_boolean.ventsys_failsafe'].state='unavailable';window.card.hass={...window.fixture};});
  await expect(page.locator('#command-status')).toContainText('Interrupted');
  await expect(page.locator('#command-status')).toContainText('Failsafe status is unavailable');
  await expect(page.locator('#position-number')).toBeDisabled();
});

test('missing backend blocks controls and a dispatcher race is checked again at send', async ({ page }) => {
  await openCard(page);
  await page.evaluate(()=>{delete window.fixture.states['script.ventsys_normal_command'];window.card.hass={...window.fixture};});
  await expect(page.locator('#position-number')).toBeDisabled();
  await expect(page.locator('#device-help')).toContainText('dispatcher is unavailable');
  await page.evaluate(()=>{window.fixture.states['script.ventsys_normal_command']={state:'off'};window.card.hass={...window.fixture};});
  await page.locator('#position-number').fill('75');await page.locator('#position-number').press('Tab');
  await page.evaluate(()=>{window.fixture.states['script.ventsys_normal_command'].state='on';window.card.hass={...window.fixture};});
  await page.locator('#confirm-command').click();
  await expect(page.locator('#command-status')).toContainText('Another VentSys command');
  expect(await page.evaluate(()=>window.calls)).toEqual([]);
});

test('environment compares three independent zones and clears unavailable or offline readings', async ({ page }) => {
  await openCard(page);
  await page.evaluate(async()=>{
    const {SENSORS}=await import('/ventsys-model.mjs?v=20261027-1');
    for (const [zone,value] of [['ambient',18],['fdm',24],['sla',29]]) window.fixture.states[SENSORS[zone].temperature[0]].state=String(value);
    window.card.hass={...window.fixture};
  });
  await expect(page.locator('#environment-box')).toContainText('ENVIRONMENT');
  await expect(page.locator('#env-ambient-temperature')).toHaveText('18');
  await expect(page.locator('#env-fdm-temperature')).toHaveText('24');
  await expect(page.locator('#env-sla-temperature')).toHaveText('29');
  await expect(page.locator('#env-sla-baro')).toHaveText('1013');
  await expect(page.locator('#env-sla-gas')).toHaveText('90');
  await page.evaluate(async()=>{const {SENSORS}=await import('/ventsys-model.mjs?v=20261027-1');window.fixture.states[SENSORS.fdm.temperature[0]].state='unavailable';window.fixture.states[SENSORS.sla.smoke[0]].state='on';window.card.hass={...window.fixture};});
  await expect(page.locator('#env-fdm-temperature')).toHaveText('—');
  await expect(page.locator('#env-sla-smoke')).toHaveText('ALARM');
  await page.evaluate(()=>{window.fixture.connection.connected=false;window.card.hass={...window.fixture};});
  await expect(page.locator('#env-ambient-temperature')).toHaveText('—');
  await expect(page.locator('#env-sla-smoke')).toHaveText('ALARM');
});

test('system log shows actual session events and environment cells fit their columns', async ({ page }) => {
  await page.setViewportSize({width:1440,height:1000});await openCard(page);
  await expect(page.locator('#svg-log-box')).toContainText('SYSTEM LOG');
  await expect(page.locator('#log-msg-1')).toHaveText('Ready · no commands sent');
  const cells=await page.locator('#environment-box text[id]').evaluateAll(nodes=>nodes.map(node=>({id:node.id,x:node.getBBox().x,width:node.getBBox().width})));
  for(const cell of cells){expect(cell.x).toBeGreaterThan(105);expect(cell.x+cell.width).toBeLessThan(407);}
  await page.locator('#diagram').screenshot({path:require('node:path').join(require('node:os').tmpdir(),'ventsys-environment-desktop.png')});
  await page.locator('#position-number').fill('75');await page.locator('#position-number').press('Tab');await page.locator('#confirm-command').click();
  await expect(page.locator('#log-msg-1')).toContainText('Requested Main duct 1');
  await expect(page.locator('#log-ts-1')).toHaveText(/\d\d:\d\d:\d\d/);
  await page.setViewportSize({width:390,height:844});
  await page.locator('#diagram').screenshot({path:require('node:path').join(require('node:os').tmpdir(),'ventsys-environment-mobile.png')});
  expect(await page.evaluate(()=>document.documentElement.scrollWidth)).toBeLessThanOrEqual(390);
});

test('grouped modes send immediately and preserve unrelated requested intent',async({page})=>{
  await openCard(page);
  await page.evaluate(()=>{window.fixture.states['input_text.ventsys_operating_state'].state=JSON.stringify({fdm:'print',sla:'purge',booth:'enclosure',revision:8});window.card.hass={...window.fixture};});
  await expect(page.locator('#operating-intents')).toContainText('FDM print · SLA purge Medium · Booth on');
  await page.locator('[data-mode-zone="sla"][data-operation="enclosure"]').click();
  expect(await page.evaluate(()=>window.calls)).toEqual([['script','ventsys_set_operating_mode',{zone:'sla',operation:'enclosure',revision:8}]]);
  await expect(page.locator('dialog[aria-labelledby="confirm-title"]')).not.toBeVisible();
  await expect(page.locator('#mode-select')).toHaveCount(0);await expect(page.locator('#mode-review')).toHaveCount(0);
});

test('missing path controller blocks whole mode without skipping devices',async({page})=>{
  await openCard(page);
  await page.evaluate(()=>{window.fixture.states['number.ventsys_e2_branch_valve_valve_position'].state='unavailable';window.card.hass={...window.fixture};});
  await page.locator('[data-mode-zone="sla"][data-operation="purge"]').click();await expect(page.locator('[data-purge-strength="6"]')).toBeDisabled();await expect(page.locator('#confirm-description')).toContainText('SLA branch');await page.locator('#cancel-command').click();
  await expect(page.locator('[data-mode-zone="both"][data-operation="print"]')).toBeDisabled();
  await expect(page.locator('[data-mode-zone="fdm"][data-operation="print"]')).toBeEnabled();
  expect(await page.evaluate(()=>window.calls)).toEqual([]);
});

test('active intent prevents conflicting manual change and single popup follows value commit',async({page})=>{
  await openCard(page);
  await page.evaluate(()=>{window.fixture.states['input_text.ventsys_operating_state'].state=JSON.stringify({fdm:'off',sla:'print',booth:'off',revision:1});window.card.hass={...window.fixture};});
  await page.locator('#position-number').fill('0');await page.locator('#position-number').press('Tab');
  await expect(page.locator('dialog[aria-labelledby="confirm-title"]')).not.toBeVisible();await expect(page.locator('#command-status')).toContainText('active mode');
  expect(await page.evaluate(()=>window.calls)).toEqual([]);
  await page.locator('#position-number').fill('100');await expect(page.locator('dialog[aria-labelledby="confirm-title"]')).not.toBeVisible();await page.locator('#position-number').press('Tab');
  await expect(page.locator('dialog[aria-labelledby="confirm-title"]')).toBeVisible();await expect(page.locator('#position-review')).toHaveCount(0);
  await expect(page.locator('.summary')).not.toContainText('Physical');await expect(page.locator('.device-panel')).not.toContainText('Physical');
});

for(const level of [2,4,6,8,10]) test(`purge popup selects level ${level} without weakening the other enclosure`,async({page})=>{
  await page.setViewportSize({width:800,height:480});await openCard(page);
  await page.evaluate(()=>{window.fixture.states['input_text.ventsys_operating_state'].state=JSON.stringify({fdm:'off',sla:'purge',booth:'off',sla_strength:10,fdm_strength:0,revision:3});window.card.hass={...window.fixture};});
  await page.locator('[data-mode-zone="fdm"][data-operation="purge"]').click();
  await expect(page.locator('#purge-strength-options')).toBeVisible();expect(await page.evaluate(()=>window.calls)).toEqual([]);
  if(level===6) await page.screenshot({path:require('node:path').join(require('node:os').tmpdir(),'ventsys-purge-popup-800.png')});
  await page.locator(`[data-purge-strength="${level}"]`).click();
  expect(await page.evaluate(()=>window.calls[0])).toEqual(['script','ventsys_set_operating_mode',{zone:'fdm',operation:'purge',revision:3,strength:level}]);
  expect(await page.evaluate(()=>window.card._pending.expected.fan_main_speed)).toBe(100);
});

test('purge cancellation never sends a command and stale popup is blocked',async({page})=>{
 await openCard(page);await page.locator('[data-mode-zone="both"][data-operation="purge"]').click();await page.locator('#cancel-command').click();expect(await page.evaluate(()=>window.calls)).toEqual([]);
 await page.locator('[data-mode-zone="fdm"][data-operation="purge"]').click();
 await page.evaluate(()=>{window.fixture.states['input_text.ventsys_operating_state'].state=JSON.stringify({fdm:'off',sla:'off',booth:'off',revision:1});window.card.hass={...window.fixture};});
 await expect(page.locator('[data-purge-strength="6"]')).toBeDisabled();await expect(page.locator('#confirm-description')).toContainText('intents changed');
 expect(await page.evaluate(()=>window.calls)).toEqual([]);
});


test('setup test reviews available valves, skips absent devices, never commands fans or sets a mode',async({page})=>{
 await page.setViewportSize({width:800,height:480});await openCard(page,{layout:"touch"});await page.locator('[data-touch-menu="modes"]').click();await page.evaluate(()=>{for(const id of ['fan.inline_fan','fan.spray_booth_fan','number.ventsys_sla_print_valve_valve_position','number.ventsys_main_duct_valve_1_valve_position']) window.fixture.states[id].state='unavailable';window.card.hass={...window.fixture};});
 await expect(page.locator('[data-mode-zone="sla"][data-operation="enclosure"]')).toBeDisabled();
 await page.locator('#setup-mode').check();await page.locator('[data-mode-zone="sla"][data-operation="enclosure"]').click();
 await expect(page.locator('#confirm-title')).toContainText('Setup/test');await expect(page.locator('#confirm-description')).toContainText('SLA print valve, Main duct 1');
 await expect(page.locator('#confirm-note')).toContainText('Fans are not commanded');expect(await page.evaluate(()=>window.calls)).toEqual([]);
 await page.screenshot({path:require('node:path').join(require('node:os').tmpdir(),'ventsys-setup-test-preview.png')});
 await page.locator('#confirm-command').click();expect(await page.evaluate(()=>window.calls[0])).toEqual(['script','ventsys_test_valves',{zone:'sla',operation:'enclosure',revision:0,included:['sla_branch','sla_360']}]);
 expect(await page.evaluate(()=>window.fixture.states['input_text.ventsys_operating_state'].state)).toContain('"sla":"off"');
});

test('setup confirmation is frozen and rechecks lost controllers; cancellation sends nothing',async({page})=>{
 await openCard(page);await page.locator('#setup-mode').check();await page.locator('[data-mode-zone="fdm"][data-operation="print"]').click();await page.locator('#cancel-command').click();expect(await page.evaluate(()=>window.calls)).toEqual([]);
 await page.locator('[data-mode-zone="fdm"][data-operation="print"]').click();await page.evaluate(()=>{window.fixture.states['number.ventsys_e1_branch_valve_valve_position'].state='unavailable';window.card.hass={...window.fixture};});await page.locator('#confirm-command').click();expect(await page.evaluate(()=>window.calls)).toEqual([]);await expect(page.locator('#command-status')).toContainText('unavailable');
});

test('setup cannot override an active mode or a running fan',async({page})=>{
 await openCard(page);await page.locator('#setup-mode').check();
 await page.evaluate(()=>{window.fixture.states['fan.inline_fan'].state='on';window.card.hass={...window.fixture};});await expect(page.locator('[data-mode-zone="fdm"][data-operation="print"]')).toBeDisabled();await expect(page.locator('#mode-help')).toContainText('Stop running fans');
 await page.evaluate(()=>{window.fixture.states['fan.inline_fan'].state='off';window.fixture.states['input_text.ventsys_operating_state'].state=JSON.stringify({fdm:'print',sla:'off',booth:'off',revision:1});window.card.hass={...window.fixture};});await expect(page.locator('#mode-help')).toContainText('Stop operating modes');expect(await page.evaluate(()=>window.calls)).toEqual([]);
});

test('wheel arrows animate only fresh positive flow and gas/RPM use integers',async ({page})=>{
 await openCard(page);
 await page.evaluate(()=>{
  for(const key of ['sensor.ventsys_fdm_airflow_sensor_flow_meter_wheel_speed']) window.fixture.states[key].state='2.123';
  window.fixture.states['sensor.garage_fdm_enclosure_sensor_fdm_enclosure_sensor_iaq_gas_resistance'].state='90555';
  window.card.hass={...window.fixture};
 });
 await expect(page.locator('#flow1-rate')).toHaveText('127 RPM');
 await expect(page.locator('#bme1-iaq')).toHaveText('91');
 await expect(page.locator('#flow1-arrow-bot')).toHaveClass(/flow-moving/);
 expect(await page.locator('#flow1-arrow-top').evaluate(e=>getComputedStyle(e).animationDelay)).toBe('0.8s');
 await page.evaluate(()=>{window.fixture.states['sensor.ventsys_fdm_airflow_sensor_flow_meter_wheel_speed'].state='0';window.card.hass={...window.fixture};});
 await expect(page.locator('#flow1-arrow-bot')).not.toHaveClass(/flow-moving/);
 await page.evaluate(()=>{window.fixture.connection.connected=false;window.card.hass={...window.fixture};});
 await expect(page.locator('#flow1-rate')).toHaveText('—');
});


test('sensor availability and airflow colour follow independent entity states',async({page})=>{
 await openCard(page);
 await page.evaluate(async()=>{const {SENSORS}=await import('/ventsys-model.mjs?v=20261104-4'); for(const kind of ['temperature','humidity','baro','gas','smoke']) for(const id of SENSORS.sla[kind] || []) if(window.fixture.states[id]) window.fixture.states[id].state='unavailable'; window.fixture.states[SENSORS.fdm.gas[0]].state='unavailable'; window.fixture.states[SENSORS.fdm.wheel[0]].state='0'; window.card.hass={...window.fixture};});
 await expect(page.locator('#bme2-label')).toHaveCSS('opacity','0.35');
 await expect(page.locator('#bme1-label')).toHaveCSS('opacity','1');
 await expect(page.locator('#flow1-arrow-bot')).toHaveCSS('fill','rgb(255, 34, 0)');
 await expect(page.locator('#flow1-arrow-bot')).toHaveCSS('opacity','1');
 await page.evaluate(async()=>{const {SENSORS}=await import('/ventsys-model.mjs?v=20261104-4');window.fixture.states[SENSORS.fdm.wheel[0]].state='1';window.card.hass={...window.fixture};});
 await expect(page.locator('#flow1-arrow-bot')).toHaveCSS('fill','rgb(0, 170, 255)');
});


test('manual intake reference confirms and calls only guarded no-motion script',async({page})=>{
 await openCard(page);await page.locator('[data-device="fdm_360"]').click();
 await expect(page.locator('#reference-controls')).toBeVisible();
 await page.locator('#reference-opening').fill('50');await page.locator('#record-reference').click();
 await expect(page.locator('#confirm-note')).toContainText('without moving');
 await page.locator('#cancel-command').click();expect(await page.evaluate(()=>window.calls)).toEqual([]);
 await page.locator('#record-reference').click();await page.locator('#confirm-command').click();
 expect(await page.evaluate(()=>window.calls)).toEqual([['script','ventsys_record_intake_reference',{target:'fdm_360',opening:50,revision:0}]]);
});

test('manual reference rejects unavailable fans and active PWM',async({page})=>{
 await openCard(page);await page.locator('[data-device="sla_360"]').click();
 await page.evaluate(()=>{window.fixture.states['fan.inline_fan'].state='unavailable';window.card.hass={...window.fixture};});
 await expect(page.locator('#record-reference')).toBeDisabled();
 await page.evaluate(()=>{window.fixture.states['fan.inline_fan'].state='off';window.fixture.states['binary_sensor.garage_ventsys_fdm_360_intake_valve_pwm_commanded_active'].state='on';window.card.hass={...window.fixture};});
 await expect(page.locator('#record-reference')).toBeDisabled();expect(await page.evaluate(()=>window.calls)).toEqual([]);
});
