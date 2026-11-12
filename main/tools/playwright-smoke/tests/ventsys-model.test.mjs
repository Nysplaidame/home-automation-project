import { test } from 'node:test';
import assert from 'node:assert/strict';
import { DEVICE_LIST, DEVICES, deviceState, numeric, sensorValue, measurement, smokeState, commandRequest, commandBlock, matchesExpected, deriveMode, airflowWarnings, MODE_EXPECTED } from '../../../dashboards/ventsys-model.mjs';
const now = Date.now();
const state = (value, unit = '', age = 0, attrs = {}) => ({ state: String(value), last_updated: new Date(now - age).toISOString(), attributes: { unit_of_measurement: unit, ...attrs } });
function snapshot(value = 0) { return Object.fromEntries(DEVICE_LIST.map(d => [d.key, { available: true, native: true, value: d.fan ? 'off' : d.expectedRange && value === 0 ? 30 : d.expectedRange && value === 100 ? 60 : value, speed: 50, min: d.expectedRange?.min ?? 0, max: d.expectedRange?.max ?? 100, timestamp: now }])); }
test('native unavailability overrides retained MQTT', () => {
  const d = DEVICES.main1, states = { [d.entity]: state(100), [d.native[0]]: state('unavailable') };
  assert.equal(deviceState(d, states, true).available, false);
});
test('full-range values remain 0–100 without normalization', () => { for (const value of [0,25,50,75,100]) assert.equal(deviceState(DEVICES.main1, { [DEVICES.main1.native[0]]: state(value) }, true).value, value); });
test('offline state cannot claim a position', () => assert.equal(deviceState(DEVICES.main1, { [DEVICES.main1.native[0]]: state(100) }, false).value, null));
test('numeric parser rejects partial numeric strings and null', () => { for (const value of ['12oops', '', null, 'NaN', 'unknown']) assert.equal(numeric({ state: value }), null); });
test('unavailable and stale sensors do not preserve previous values', () => {
  for (const s of [state('unavailable'), state(42,'%',300001)]) assert.equal(sensorValue(['sensor.a'], { 'sensor.a': s }, true, now).value, null);
});
test('registered unavailable primary is not masked by fallback', () => assert.equal(sensorValue(['sensor.a','sensor.b'], { 'sensor.a': state('unavailable'), 'sensor.b': state(42) }, true, now).value, null));
test('missing primary permits explicit fallback', () => assert.equal(sensorValue(['sensor.a','sensor.b'], { 'sensor.b': state(42) }, true, now).value, 42));
test('pressure quantities and units remain separate', () => {
  assert.equal(measurement('baro', { value: 101300, unit: 'Pa' }).value, 1013);
  assert.equal(measurement('differential', { value: 1013, unit: 'hPa' }).value, null);
  assert.equal(measurement('differential', { value: -8, unit: 'Pa' }).value, -8);
});
test('gas resistance uses units instead of magnitude heuristics', () => { assert.equal(measurement('gas',{ value: 1500, unit: 'Ω' }).value, 1.5); assert.equal(measurement('gas',{ value: 1500, unit: 'kΩ' }).value, 1500); });
test('wheel readings convert actual rps to per-wheel RPM', () => assert.equal(measurement('wheel',{ value: 2, unit: 'rounds/s' }).value, 120));
test('360 roles follow registry MACs and corrected MQTT roles, not legacy HA prefixes', () => {
  assert.equal(DEVICES.fdm_360.native[0], 'number.ventsys_sla_360_intake_valve_valve_position');
  assert.equal(DEVICES.fdm_360.boardMac, 'a0:85:e3:ae:5b:c8');
  assert.equal(DEVICES.fdm_360.topic, 'ventsys/sla/360/control');
  assert.equal(DEVICES.sla_360.native[0], 'number.ventsys_fdm_360_intake_valve_valve_position');
  assert.equal(DEVICES.sla_360.boardMac, 'cc:ba:97:f0:e3:ec');
  assert.equal(DEVICES.sla_360.topic, 'ventsys/fdm/360/control');
  const states = { [DEVICES.fdm_360.native[0]]: state(41), [DEVICES.sla_360.native[0]]: state(57) };
  assert.equal(deviceState(DEVICES.fdm_360, states, true).value, 41);
  assert.equal(deviceState(DEVICES.sla_360, states, true).value, 57);
});
test('fallback clear never overwrites active smoke', () => assert.equal(smokeState(['a','b'], { a: state('on'), b: state('clear') }, true, false, now).alarm, true));
test('smoke alarm survives unavailable primary or disconnect', () => {
  assert.equal(smokeState(['a','b'], { a: state('unavailable'), b: state('clear') }, true, true, now).alarm, true);
  assert.equal(smokeState(['a'], { a: state('off') }, false, true, now).alarm, true);
});
test('fresh explicit primary clear can clear previous alarm', () => assert.equal(smokeState(['a','b'], { a: state('off'), b: state('clear') }, true, true, now).alarm, false));
test('unchanged native binary sensor uses only its own board heartbeat', () => {
  const id='binary_sensor.board_smoke_detected';
  assert.equal(smokeState([id], { [id]: state('off','',900000), 'sensor.board_temperature': state(20,'°C') }, true, false, now).label, 'Clear');
  assert.equal(smokeState([id], { [id]: state('off','',900000), 'sensor.other_temperature': state(20,'°C') }, true, false, now).label, 'Unavailable');
});
test('command schema rejects arbitrary targets, scripts, percentages and retain-like payloads', () => {
  for (const args of [['mode','fire_safe'], ['position','__proto__',0], ['position','main1',NaN], ['position','main1','100'], ['position','main1',101], ['position','main1',-1], ['position','main1',0.5], ['fan','main1','on'], ['speed','main1',50], ['position','fan_main',50], ['mode','sealed','on']]) assert.throws(() => commandRequest(...args));
});
test('all eight valve commands accept 100; fan commands are explicit', () => {
  for (const d of DEVICE_LIST.filter(d=>!d.fan)) assert.equal(commandRequest('position',d.key,100).value,100);
  assert.deepEqual(commandRequest('fan','fan_main','off'),{kind:'fan',target:'fan_main',value:'off'});
});
test('failsafe unknown, offline, unavailable and firmware ranges block commands', () => {
  const request=commandRequest('position','main1',100), s=snapshot();
  assert.match(commandBlock(request,s,false,'off'), /offline/);
  assert.match(commandBlock(request,s,true,undefined), /unavailable/);
  assert.match(commandBlock(request,s,true,'on'), /Failsafe/);
  s.main1.max=60;assert.match(commandBlock(request,s,true,'off'), /accepts controller targets/);
  s.main1.available=false;assert.match(commandBlock(request,s,true,'off'), /unavailable/);
});
test('mode status requires complete relevant reports', () => {
  const s=snapshot();assert.equal(deriveMode(s,true),'Sealed · reported');s.main1.available=false;assert.equal(deriveMode(s,true),'Incomplete state');assert.equal(deriveMode(s,false),'Offline');
});
test('purge requires full standard travel and accepted 360 open endpoints', () => { const s=snapshot(50);s.fan_main.value=s.fan_booth.value='on';assert.equal(matchesExpected(MODE_EXPECTED.purge,s),false);for(const d of DEVICE_LIST.filter(d=>!d.fan))s[d.key].value=d.expectedRange?.max ?? 100;assert.equal(matchesExpected(MODE_EXPECTED.purge,s),true); });
test('360 closed target 30 is treated as closed when checking exhaust paths', () => { const s=snapshot();s.fan_main.value='on';s.fdm_branch.value=100;assert.match(airflowWarnings(s)[0],/no reported/);s.fdm_360.value=60;assert.deepEqual(airflowWarnings(s),[]); });
test('blocked-path warning and unknown path remain actionable', () => { const s=snapshot();s.fan_main.value='on';assert.match(airflowWarnings(s)[0],/no reported/);s.main1.available=false;assert.match(airflowWarnings(s)[0],/cannot be verified/); });

test('both unwanted opening and required opening failures are explicit report mismatches',async()=>{
 const {operatingState,operatingWarnings}=await import('../../../dashboards/ventsys-model.mjs');
 const current=operatingState({'input_text.ventsys_operating_state':state(JSON.stringify({fdm:'print',sla:'off',booth:'off',revision:1}))});
 const s=snapshot();s.fdm_360.value=60;s.fdm_branch.value=0;
 const warnings=operatingWarnings(current,s);
 assert(warnings.some(x=>x.includes('Unwanted open report: FDM 360')));
 assert(warnings.some(x=>x.includes('FDM branch')&&x.includes('mismatch')));
 assert(!warnings.some(x=>x.includes('jam confirmed')));
});
test('booth-only route is a reported open path even when unused enclosure reports are missing',()=>{
 const s=snapshot();s.fan_main.value='on';s.main1.value=s.main2.value=100;s.fdm_branch.available=false;
 assert.deepEqual(airflowWarnings(s),[]);
});


test('intake UI opening maps endpoints and midpoint without changing controller state', async () => {
  const {openingPercent,servoPercent}=await import('../../../dashboards/ventsys-model.mjs');
  for(const key of ['fdm_360','sla_360']) {
    const device=DEVICES[key];
    assert.equal(openingPercent(device,30),0);assert.equal(openingPercent(device,45),50);assert.equal(openingPercent(device,60),100);
    assert.equal(servoPercent(device,0),30);assert.equal(servoPercent(device,50),45);assert.equal(servoPercent(device,100),60);
    assert.equal(openingPercent(device,null),null);
  }
});

test('CO fault is an orange incident and simultaneous detection is unverified', async () => {
  const { activeIncidents } = await import('../../../dashboards/ventsys-model.mjs');
  const prefix = 'garage_ventsys_sla_pipe_air_sensor';
  const states = { [`binary_sensor.${prefix}_co_sensor_fault`]: state('on'), [`binary_sensor.${prefix}_sensor_fault`]: state('on'), [`binary_sensor.${prefix}_co_detected`]: state('off') };
  const incidents = activeIncidents(states, true);
  assert.equal(incidents.length, 1);
  assert.equal(incidents[0].severity, 'orange');
  assert.equal(incidents[0].label, 'co sensor fault');
  assert.equal(incidents[0].fault, true);
  states[`binary_sensor.${prefix}_co_detected`] = state('on');
  assert.match(activeIncidents(states, true).find(i => i.severity === 'red').label, /unverified signal/);
});
