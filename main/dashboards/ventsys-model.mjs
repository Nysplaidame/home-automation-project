import { MODE_EXPECTED, OPERATING_PLANS, TEST_TARGETS } from './ventsys-modes.mjs?v=20261104-4';

export const VERSION = '20261107-8';
export const BOARD_HEALTH = [
  { key: 'booth_airflow', label: 'Booth airflow', uptime: 'sensor.ventsys_fdm_airflow_sensor_uptime', zone: 'ambient' },
  { key: 'fdm_airflow', label: 'FDM airflow', uptime: 'sensor.ventsys_fdm_airflow_sensor_uptime_2', zone: 'fdm' },
  { key: 'sla_airflow', label: 'SLA airflow', uptime: 'sensor.ventsys_sla_airflow_sensor_uptime', zone: 'sla' },
  { key: 'sla_pipe_air', label: 'SLA pipe air', uptime: 'sensor.garage_ventsys_sla_pipe_air_sensor_uptime', zone: 'sla' },
  { key: 'main_duct_1', label: 'Main duct valve 1', uptime: 'sensor.ventsys_main_duct_valve_1_uptime', zone: null },
  { key: 'main_duct_2', label: 'Main duct valve 2', uptime: 'sensor.garage_ventsys_main_duct_valve_2_uptime', zone: null },
  { key: 'fdm_branch', label: 'FDM branch valve', uptime: 'sensor.ventsys_e1_branch_valve_uptime', zone: 'fdm' },
  { key: 'sla_branch', label: 'SLA branch valve', uptime: 'sensor.ventsys_e2_branch_valve_uptime', zone: 'sla' },
  { key: 'fdm_print', label: 'FDM print valve', uptime: 'sensor.ventsys_fdm_print_valve_uptime', zone: 'fdm' },
  { key: 'sla_print', label: 'SLA print valve', uptime: 'sensor.ventsys_sla_print_valve_uptime', zone: 'sla' },
  { key: 'fdm_intake', label: 'FDM 360° intake', uptime: 'sensor.ventsys_sla_360_intake_valve_uptime', zone: 'fdm' },
  { key: 'sla_intake', label: 'SLA 360° intake', uptime: 'sensor.ventsys_fdm_360_intake_valve_uptime', zone: 'sla' },
];
export function latchedAlarms(states, connected) {
  if (!connected) return [];
  return Object.entries(states).filter(([id, entity]) =>
    /^binary_sensor\.(?:garage_)?ventsys_[a-z0-9_]+_alarm_latched$/.test(id) && entity.state === 'on'
  ).map(([id, entity]) => {
    const prefix = id.slice('binary_sensor.'.length, -'_alarm_latched'.length);
    const buttonId = `button.${prefix}_acknowledge_alarms`;
    const active = ['co_detected', 'smoke_detected', 'high_temperature'].some(name => states[`binary_sensor.${prefix}_${name}`]?.state === 'on');
    const fault = ['sensor_fault', 'co_sensor_fault', 'bme680_fault'].some(name => states[`binary_sensor.${prefix}_${name}`]?.state === 'on');
    const button = states[buttonId];
    return { id, buttonId, label: entity.attributes?.friendly_name?.replace(/\s*alarm_latched$/i, '') || prefix.replaceAll('_', ' '),
      active, fault, canAcknowledge: Boolean(!active && !fault && button && button.state !== 'unavailable') };
  }).sort((a, b) => a.label.localeCompare(b.label));
}
export function activeIncidents(states, connected) {
  if (!connected) return [];
  const incidents = [];
  for (const board of BOARD_HEALTH) {
    const uptime = states[board.uptime];
    if (!uptime) continue;
    const maintenance = states[`input_boolean.ventsys_maintenance_${board.key}`]?.state === 'on';
    const offline = ['unavailable', 'unknown'].includes(uptime.state);
    if (offline || maintenance) incidents.push({
      id: board.uptime, severity: maintenance ? 'blue' : 'orange', zone: board.zone,
      source: board.label, label: maintenance ? `Maintenance active — ${offline ? 'board offline' : 'dropout alerts paused'}` : 'Board offline — expected online', fault: offline
    });
  }
  const slaOnline = !['unavailable', 'unknown'].includes(states['sensor.garage_ventsys_sla_pipe_air_sensor_uptime']?.state);
  if (slaOnline && ['unavailable', 'unknown'].includes(states['sensor.garage_ventsys_sla_pipe_air_sensor_co_voltage']?.state)) incidents.push({
    id: 'sensor.garage_ventsys_sla_pipe_air_sensor_co_voltage', severity: 'orange', zone: 'sla',
    source: 'VentSys SLA Pipe Air Sensor', label: 'CO voltage entity unavailable', fault: true
  });
  for (const [id, entity] of Object.entries(states)) {
    if (entity.state !== 'on') continue;
    const match = /^binary_sensor\.((?:garage_)?ventsys_[a-z0-9_]+)_(co_detected|smoke_detected|high_temperature|sensor_fault|co_sensor_fault|bme680_fault|temperature_rising_fast|alarm_latched)$/.exec(id);
    if (!match) continue;
    const [, prefix, kind] = match;
    if (kind === 'sensor_fault' && states[`binary_sensor.${prefix}_co_sensor_fault`]?.state === 'on') continue;
    const zone = prefix.includes('sla') ? 'sla' : prefix.includes('fdm') ? 'fdm' : 'ambient';
    const fault = states[`binary_sensor.${prefix}_sensor_fault`]?.state === 'on' || states[`binary_sensor.${prefix}_co_sensor_fault`]?.state === 'on';
    const severity = ['co_detected','smoke_detected','high_temperature'].includes(kind) ? 'red' : kind === 'alarm_latched' && !fault ? 'orange' : 'orange';
    const source = entity.attributes?.friendly_name?.replace(/\s+(co_detected|smoke_detected|high_temperature|sensor_fault|co_sensor_fault|bme680_fault|temperature_rising_fast|alarm_latched)$/i,'') || prefix.replaceAll('_',' ');
    const label = kind === 'co_detected' && fault ? 'CO detection reported with sensor fault — unverified signal' : kind.replaceAll('_',' ');
    incidents.push({id, severity, zone, source, label, fault, latched: kind === 'alarm_latched'});
  }
  if (states['input_boolean.ventsys_failsafe']?.state === 'on') incidents.push({id:'input_boolean.ventsys_failsafe',severity:'red',zone:null,source:'VentSys',label:'Failsafe active'});
  if (states['script.ventsys_mode_fire_safe']?.state === 'on') incidents.push({id:'script.ventsys_mode_fire_safe',severity:'red',zone:null,source:'VentSys',label:'Fire response running'});
  const rank = { red: 0, orange: 1, blue: 2 };
  return incidents.sort((a,b) => rank[a.severity] - rank[b.severity] || a.source.localeCompare(b.source));
}
// HA retained the old 360 entity IDs after the physical roles were swapped.
// Bind by MAC. Running firmware also retains the old opposite-role MQTT topics.
export const DEVICE_LIST = [
  { key: 'main1', name: 'Main duct 1', short: 'MAIN-1', zone: 'Main duct', entity: 'number.main_duct_valve_1', native: ['number.ventsys_main_duct_valve_1_valve_position'], topic: 'ventsys/main/valve1/control', svg: 'valve-main-1', text: 'valve-main-1-pos' },
  { key: 'main2', name: 'Main duct 2', short: 'MAIN-2', zone: 'Main duct', entity: 'number.main_duct_valve_2', native: ['number.garage_ventsys_main_duct_valve_2_valve_position'], topic: 'ventsys/main/valve2/control', svg: 'valve-main-2', text: 'valve-main-2-pos' },
  { key: 'fdm_branch', name: 'FDM branch', short: 'E1 BRANCH', zone: 'FDM enclosure', entity: 'number.fdm_branch_valve', native: ['number.ventsys_e1_branch_valve_valve_position'], topic: 'ventsys/fdm/branch/control', svg: 'valve-enc1-vert', text: 'valve-enc1-vert-pos' },
  { key: 'fdm_print', name: 'FDM print valve', short: 'E1 PRINT', zone: 'FDM enclosure', entity: 'number.fdm_valve', native: ['number.ventsys_fdm_print_valve_valve_position'], topic: 'ventsys/fdm/valve/control', svg: 'valve-enc1-print', text: 'enc1-print-pct' },
  { key: 'fdm_360', name: 'FDM 360° intake', short: 'E1 INTAKE', zone: 'FDM enclosure', entity: 'number.fdm_360_intake', native: ['number.ventsys_sla_360_intake_valve_valve_position'], boardMac: 'a0:85:e3:ae:5b:c8', expectedRange: { min: 30, max: 60 }, topic: 'ventsys/sla/360/control', svg: 'valve-360-enc1', text: 'enc1-360-pct' },
  { key: 'sla_branch', name: 'SLA branch', short: 'E2 BRANCH', zone: 'SLA enclosure', entity: 'number.sla_branch_valve', native: ['number.ventsys_e2_branch_valve_valve_position'], topic: 'ventsys/sla/branch/control', svg: 'valve-enc2-vert', text: 'valve-enc2-vert-pos' },
  { key: 'sla_print', name: 'SLA print valve', short: 'E2 PRINT', zone: 'SLA enclosure', entity: 'number.sla_valve', native: ['number.ventsys_sla_print_valve_valve_position'], topic: 'ventsys/sla/valve/control', svg: 'valve-enc2-print', text: 'enc2-print-pct' },
  { key: 'sla_360', name: 'SLA 360° intake', short: 'E2 INTAKE', zone: 'SLA enclosure', entity: 'number.sla_360_intake', native: ['number.ventsys_fdm_360_intake_valve_valve_position'], boardMac: 'cc:ba:97:f0:e3:ec', expectedRange: { min: 30, max: 60 }, topic: 'ventsys/fdm/360/control', svg: 'valve-360-enc2', text: 'enc2-360-pct' },
  { key: 'fan_main', name: 'Main extraction fan', short: 'MAIN FAN', zone: 'Main duct', entity: 'fan.inline_fan', native: [], topic: 'ventsys/fan/control', speedTopic: 'ventsys/fan/percent', svg: 'fan-blades', text: 'main-fan-pct', fan: true },
  { key: 'fan_booth', name: 'Spray booth fan', short: 'BOOTH FAN', zone: 'Spray booth', entity: 'fan.spray_booth_fan', native: [], topic: 'ventsys/spray-fan/control', speedTopic: 'ventsys/spray-fan/percent', svg: 'spray-booth-fan-blades', text: 'spray-fan-pct', fan: true },
];
export const DEVICES = Object.fromEntries(DEVICE_LIST.map(device => [device.key, Object.freeze(device)]));
export const MODE_LABELS = { sealed: 'Seal all', purge: 'Purge all', booth: 'Spray booth', booth_seal: 'Seal booth', fdm_print: 'FDM print', fdm_enclosure: 'FDM enclosure', fdm_purge: 'FDM purge', fdm_seal: 'Seal FDM', sla_print: 'SLA print', sla_enclosure: 'SLA enclosure', sla_purge: 'SLA purge', sla_seal: 'Seal SLA' };
export { MODE_EXPECTED };
export function setupTargets(zone, operation) {
  const key=zone+':'+operation;
  if(!Object.hasOwn(TEST_TARGETS,key)) throw new Error('Invalid valve setup test');
  return {...TEST_TARGETS[key]};
}
export function operatingState(states) {
  const entity = states['input_text.ventsys_operating_state'];
  if (!entity || entity.state === 'unavailable') return null;
  try {
    const state = ['', 'unknown'].includes(entity.state) ? {fdm:'off',sla:'off',booth:'off',revision:0} : JSON.parse(entity.state);
    const key = [state.fdm,state.sla,state.booth].join('|');
    for(const zone of ['fdm','sla']) {
      const level=state[zone] === 'purge' ? state[zone+'_strength'] ?? 6 : 0;
      if(!Number.isInteger(level) || ![0,2,4,6,8,10].includes(level) || state[zone] === 'purge' && level === 0) return null;
      state[zone+'_strength']=level;
    }
    return Object.hasOwn(OPERATING_PLANS,key) && Number.isInteger(state.revision) && state.revision >= 0 ? {...state,key} : null;
  } catch (_) { return null; }
}
export const PURGE_STRENGTHS = Object.freeze({2:'Low',4:'Moderate',6:'Medium',8:'High',10:'Max'});
export function operatingPlan(state, zone, operation, strength) {
  const request = zone + ':' + operation;
  if (!state || !Object.hasOwn(OPERATING_PLANS,state.key) || !Object.hasOwn(OPERATING_PLANS[state.key],request)) throw new Error('Operating mode state is unavailable or invalid');
  const plan=structuredClone(OPERATING_PLANS[state.key][request]);
  if(operation === 'purge' && strength === undefined) strength=state[zone+'_strength'] || 6;
  if(operation === 'purge' && (!Number.isInteger(strength) || !Object.hasOwn(PURGE_STRENGTHS,strength)) || operation !== 'purge' && strength !== undefined) throw new Error('Choose a valid purge strength');
  for(const item of ['fdm','sla']) plan.desired[item+'_strength']=plan.desired[item] === 'purge' ? [item,'both'].includes(zone) ? strength : state[item+'_strength'] || 6 : 0;
  const percent=Math.max(plan.desired.fdm_strength,plan.desired.sla_strength)*10;
  if(percent) {
    plan.targets.fan_main_speed=percent;
    plan.phases=plan.phases.map(phase=>phase.fan_main === 'on' ? {fan_main_speed:percent,...phase} : phase);
  }
  return plan;
}
export function operatingWarnings(state, snapshot) {
  if(!state) return [];
  const expected=operatingPlan(state,'fdm',state.fdm).targets, warnings=[];
  for(const [key,target] of Object.entries(expected)) {
    const speed=key.endsWith('_speed'), name=speed ? key.slice(0,-6) : key, device=DEVICES[name], report=snapshot[name];
    if(!report?.available) {warnings.push(`Requested mode: ${device.name} report unavailable.`);continue;}
    const actual=speed ? report.speed : report.value;
    if(actual === target) continue;
    if(!speed && !device.fan && target === (device.expectedRange?.min ?? 0)) warnings.push(`Unwanted open report: ${device.name} reports ${actual}%; requested closed (${target}%).`);
    else warnings.push(`Requested mode mismatch: ${device.name}${speed ? ' speed' : ''} reports ${actual}; requested ${target}.`);
  }
  return warnings;
}

// MAC CC:BA:97:F0:D0:C0 is physically FDM; HA may retain its legacy SLA IDs.
const FDM_LEGACY = 'garage_sla_enclosure_sensor_array_1_sla_enclosure_sensor_';
const FDM_INSTALLED = 'garage_fdm_enclosure_sensor_fdm_enclosure_sensor_';
export const SENSORS = {
  fdm: {
    label: 'FDM enclosure', temperature: ['sensor.'+FDM_INSTALLED+'temperature','sensor.'+FDM_LEGACY+'temperature','sensor.ventsys_fdm_pipe_air_temperature', 'sensor.fdm_temperature'],
    humidity: ['sensor.'+FDM_INSTALLED+'humidity','sensor.'+FDM_LEGACY+'humidity','sensor.ventsys_fdm_pipe_air_humidity'], baro: ['sensor.'+FDM_INSTALLED+'pressure','sensor.'+FDM_LEGACY+'pressure','sensor.ventsys_fdm_pipe_air_baro_pressure'],
    differential: ['sensor.fdm_pressure_differential'], gas: ['sensor.'+FDM_INSTALLED+'iaq_gas_resistance','sensor.'+FDM_LEGACY+'iaq_gas_resistance','sensor.ventsys_fdm_pipe_air_iaq_gas_resistance', 'sensor.fdm_iaq'],
    smoke: ['binary_sensor.garage_fdm_enclosure_sensor_co_detected', 'binary_sensor.'+FDM_INSTALLED+'co_detected', 'sensor.fdm_co'], alarmLabel: 'CO',
    wheel: ['sensor.ventsys_fdm_airflow_sensor_flow_meter_wheel_speed', 'sensor.fdm_airflow_wheel_speed'],
  },
  sla: {
    label: 'SLA enclosure', temperature: ['sensor.garage_ventsys_sla_pipe_air_sensor_temperature', 'sensor.ventsys_sla_pipe_air_temperature', 'sensor.sla_temperature'],
    humidity: ['sensor.garage_ventsys_sla_pipe_air_sensor_humidity', 'sensor.ventsys_sla_pipe_air_humidity'],
    baro: ['sensor.garage_ventsys_sla_pipe_air_sensor_baro_pressure', 'sensor.ventsys_sla_pipe_air_baro_pressure'],
    differential: ['sensor.sla_pressure_differential'],
    gas: ['sensor.garage_ventsys_sla_pipe_air_sensor_iaq_gas_resistance', 'sensor.ventsys_sla_pipe_air_iaq_gas_resistance', 'sensor.sla_iaq'],
    smoke: ['binary_sensor.garage_ventsys_sla_pipe_air_sensor_co_detected'], alarmLabel: 'CO',
    wheel: ['sensor.sla_airflow_wheel_speed'],
  },
  ambient: {
    label: 'Garage ambient', temperature: ['sensor.ventsys_garage_air_temperature'], humidity: ['sensor.ventsys_garage_air_humidity'],
    baro: ['sensor.ventsys_garage_air_baro_pressure'], gas: ['sensor.ventsys_garage_air_iaq_gas_resistance'],
    smoke: ['binary_sensor.ventsys_garage_air_smoke_detected'],
  },
};

export function known(state) { return state && !['', 'unknown', 'unavailable', 'none'].includes(String(state.state ?? '').toLowerCase()); }
export function numeric(state) { return known(state) && String(state.state).trim() !== '' && Number.isFinite(Number(state.state)) ? Number(state.state) : null; }
export function timestamp(state) { const value = Date.parse(state?.last_reported || state?.last_updated || ''); return Number.isFinite(value) ? value : null; }
export function freshnessTime(id, state, states) {
  // Binary sensors can remain unchanged for days while their ESPHome board is
  // online. A recent temperature report from the same exact sensor prefix is
  // a heartbeat; never borrow freshness from another device or MQTT alias.
  const sibling = id === 'binary_sensor.garage_fdm_enclosure_sensor_co_detected' ? 'sensor.' + FDM_INSTALLED + 'temperature' : String(id || '').replace(/^[^.]+\./, 'sensor.').replace(/_(co_detected|smoke_detected|humidity|baro_pressure|pressure|iaq_gas_resistance)$/, '_temperature');
  const own = timestamp(state), heartbeat = known(states[sibling]) ? timestamp(states[sibling]) : null;
  return Math.max(own ?? 0, heartbeat ?? 0) || null;
}
export function deviceState(device, states, connected) {
  // An adopted native entity becoming unavailable must never be masked by a retained MQTT number.
  const nativeId = device.native.find(id => Object.hasOwn(states, id));
  const entityId = nativeId || device.entity;
  const state = states[entityId];
  const value = device.fan ? (known(state) && ['on', 'off'].includes(state.state) ? state.state : null) : numeric(state);
  const available = Boolean(connected && value !== null && (device.fan || (value >= 0 && value <= 100)));
  return { entityId, state, available, value: available ? value : null, speed: available ? numeric({ state: state?.attributes?.percentage }) : null,
    min: Math.max(0, Number(state?.attributes?.min ?? device.expectedRange?.min ?? 0)), max: Math.min(100, Number(state?.attributes?.max ?? device.expectedRange?.max ?? 100)),
    timestamp: timestamp(state), native: Boolean(nativeId), physicalVerified: false };
}

// UI opening is normalized; controller reports/commands retain calibrated raw units.
export function openingPercent(device, value) {
  if (typeof value !== 'number' || !Number.isFinite(value)) return null;
  const range=device.expectedRange;
  return range ? Math.max(0,Math.min(100,(value-range.min)*100/(range.max-range.min))) : value;
}
export function servoPercent(device, opening) {
  const range=device.expectedRange;
  return range ? Math.round(range.min+opening*(range.max-range.min)/100) : opening;
}

export function sensorValue(ids, states, connected, now = Date.now(), maxAge = 300000) {
  if (!connected) return { value: null, reason: 'Offline' };
  // Pick the first registered source. Missing sources permit fallback; unavailable
  // adopted sources stay visibly unavailable rather than silently using retained data.
  const id = ids?.find(id => Object.hasOwn(states, id));
  const state = states[id]; const value = numeric(state); const updated = freshnessTime(id, state, states);
  if (value === null) return { value: null, id, reason: 'Unavailable' };
  if (updated === null || now - updated > maxAge || updated > now + 30000) return { value: null, id, reason: 'Stale', timestamp: updated };
  return { value, id, unit: state.attributes?.unit_of_measurement || '', timestamp: updated };
}

export function measurement(kind, sensor) {
  if (sensor.value === null) return sensor;
  let { value, unit } = sensor;
  const bad = () => ({ ...sensor, value: null, reason: 'Unit mismatch' });
  if (kind === 'baro') {
    if (unit === 'Pa') value /= 100;
    else if (unit === 'kPa') value *= 10;
    else if (!['hPa', 'mbar'].includes(unit)) return bad();
    unit = 'hPa';
  } else if (kind === 'differential') { if (unit !== 'Pa') return bad(); }
  else if (kind === 'gas') {
    if (['Ω', 'ohm', 'ohms'].includes(unit)) value /= 1000;
    else if (!['kΩ', 'kOhm', 'kOhms', 'kOhm/s'].includes(unit)) return bad();
    unit = 'kΩ'; // Raw resistance is not a certified air-quality index.
  } else if (kind === 'wheel') {
    if (['rounds/s', 'rps', 'rev/s'].includes(unit)) value *= 60;
    else if (!['rpm', 'RPM'].includes(unit)) return bad();
    unit = 'RPM';
  } else if (kind === 'temperature') { if (!['°C', 'C'].includes(unit)) return bad(); unit = '°C'; }
  else if (kind === 'humidity') { if (unit !== '%') return bad(); }
  return { ...sensor, value, unit };
}

export function smokeState(ids, states, connected, previousAlarm = false, now = Date.now()) {
  const registered = ids.filter(id => Object.hasOwn(states, id));
  const active = state => known(state) && ['on', 'detected', 'smoke', 'true', '1'].includes(String(state.state).toLowerCase());
  const clear = state => known(state) && ['off', 'clear', 'normal', 'false', '0'].includes(String(state.state).toLowerCase());
  const fresh = state => { const id = registered.find(id => states[id] === state); const time = freshnessTime(id, state, states); return time !== null && now - time <= 300000 && time <= now + 30000; };
  const anyAlarm = registered.some(id => active(states[id]));
  const primary = states[registered[0]];
  const currentAlarm = connected && anyAlarm;
  const canClear = connected && !anyAlarm && clear(primary) && fresh(primary);
  const alarm = currentAlarm || (previousAlarm && !canClear);
  return { alarm, unknown: !connected || !primary || !fresh(primary) || (!active(primary) && !clear(primary)),
    label: alarm ? (currentAlarm && fresh(primary) ? 'SMOKE DETECTED' : 'ALARM · last known') : canClear ? 'Clear' : 'Unavailable' };
}

export function commandRequest(kind, target, value) {
  if (kind === 'mode') {
    if (!Object.hasOwn(MODE_EXPECTED, target) || value !== undefined) throw new Error('Invalid mode');
    return { kind, target };
  }
  const device = Object.hasOwn(DEVICES, target) ? DEVICES[target] : null;
  if (!device || !['position', 'fan', 'speed'].includes(kind)) throw new Error('Invalid control');
  if (kind === 'fan') {
    if (!device.fan || !['on', 'off'].includes(value)) throw new Error('Invalid fan command');
  } else if (!Number.isInteger(value) || value < 0 || value > 100 || (kind === 'position' && device.fan) || (kind === 'speed' && !device.fan)) throw new Error('Invalid percentage');
  return { kind, target, value };
}

export function commandExpected(request, snapshot) {
  const expected = request.kind === 'mode' ? MODE_EXPECTED[request.target] : { [request.kind === 'speed' ? request.target + '_speed' : request.target]: request.value };
  if (request.kind !== 'mode' || request.scope !== 'available') return expected;
  if (Array.isArray(request.included)) return Object.fromEntries(Object.entries(expected).filter(([key])=>request.included.includes(key)));
  return Object.fromEntries(Object.entries(expected).filter(([key]) => {
    const speed = key.endsWith('_speed'), name = speed ? key.slice(0,-6) : key, state = snapshot?.[name];
    return state?.available && (DEVICES[name].fan || state.native) && (!speed || Number.isFinite(state.speed));
  }));
}
export function matchesExpected(expected, snapshot) {
  return Object.entries(expected).every(([key, value]) => {
    const speed = key.endsWith('_speed'); const device = snapshot[speed ? key.slice(0, -6) : key];
    return device?.available && (speed ? device.speed : device.value) === value;
  });
}
export function commandBlock(request, snapshot, connected, failsafe) {
  if (!connected) return 'Home Assistant is offline';
  if (failsafe !== 'off') return failsafe === 'on' ? 'Failsafe is active; manual controls are locked' : 'Failsafe status is unavailable';
  const expected = commandExpected(request, snapshot);
  if (!Object.keys(expected).length) return 'No available controllers for this mode';
  for (const [key, target] of Object.entries(expected)) {
    const speed = key.endsWith('_speed'); const device = snapshot[speed ? key.slice(0, -6) : key];
    if (!device?.available) return `${DEVICES[speed ? key.slice(0, -6) : key]?.name || key} is unavailable`;
    if (speed && (device.speed === null || !Number.isFinite(device.speed))) return 'Fan speed report is unavailable';
    const definition = DEVICES[speed ? key.slice(0, -6) : key];
    if (!definition.fan && !device.native) return `${definition.name} has no adopted native controller report`;
    if (typeof target === 'number' && !speed && (target < device.min || target > device.max)) return `${definition.name} accepts controller targets ${device.min}–${device.max}%`;
  }
  return '';
}

export function deriveMode(snapshot, connected) {
  if (!connected) return 'Offline';
  if (matchesExpected(MODE_EXPECTED.sealed, snapshot)) return 'Sealed · reported';
  if (matchesExpected(MODE_EXPECTED.purge, snapshot)) return 'Purge all · reported';
  const partial = ['fdm_print', 'fdm_enclosure', 'fdm_purge', 'sla_print', 'sla_enclosure', 'sla_purge', 'booth'].filter(key => matchesExpected(MODE_EXPECTED[key], snapshot));
  return partial.length ? partial.map(key => MODE_LABELS[key]).join(' + ') : DEVICE_LIST.some(d => !snapshot[d.key]?.available) ? 'Incomplete state' : 'Manual';
}

export function airflowWarnings(snapshot) {
  const v = key => {
    const state = snapshot[key]; if (!state?.available) return null;
    return DEVICES[key]?.expectedRange ? Math.max(0, Math.min(100, (state.value - state.min) / Math.max(1, state.max - state.min) * 100)) : state.value;
  };
  const needed = ['main1', 'main2', 'fdm_branch', 'fdm_print', 'fdm_360', 'sla_branch', 'sla_print', 'sla_360'];
  const out = [];
  if (v('fan_main') === 'on') {
    const openPath=(v('fdm_branch') > 0 && (v('fdm_print') > 0 || v('fdm_360') > 0)) || (v('main1') > 0 && v('sla_branch') > 0 && (v('sla_print') > 0 || v('sla_360') > 0)) || (v('main1') > 0 && v('main2') > 0);
    if (!openPath && needed.some(key => v(key) === null)) out.push('Main fan is on; an open exhaust path cannot be verified because valve state is missing.');
    else if (!openPath) out.push('Main fan is on with no reported enclosure or booth path. Check branch and intake positions.');
  }
  if (v('fan_booth') === 'on' && !(v('main1') > 0 && v('main2') > 0)) out.push('Booth fan is on; both main duct valves must report an open path.');
  return out;
}
