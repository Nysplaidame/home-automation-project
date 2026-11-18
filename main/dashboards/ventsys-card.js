import {activity} from './ventsys-history.mjs?v=20261117-7';
import { SENSOR_DEVICES, CONTROL_MAINTENANCE, detailEntities, ENVIRONMENT_SOURCES, pressureRelation, VERSION, DEVICE_LIST, DEVICES, MODE_LABELS, SENSORS, BOARD_HEALTH, deviceState, sensorValue, measurement, smokeState, commandRequest, commandExpected, commandBlock, matchesExpected, deriveMode, airflowWarnings, operatingState, operatingPlan, PURGE_STRENGTHS, operatingWarnings, setupTargets, openingPercent, servoPercent, latchedAlarms, activeIncidents } from './ventsys-model.mjs?v=20261117-7';

const asset = name => new URL(name + '?v=' + VERSION, import.meta.url).href;
const lockKey = Symbol.for('ventsys.pending-command');
const sensorDisplay = (kind,value) => ['gas','wheel'].includes(kind) ? String(Math.round(value)) : display(value);
const display = value => typeof value === 'number' ? value.toFixed(1).replace(/\.0$/, '') : String(value);

export class VentSysDashboardCard extends HTMLElement {
  constructor() {
    super(); this.attachShadow({ mode: 'open' });
    this._selected = 'main1'; this._alarms = {}; this._events = []; this._faultSince = new Map(); this._started = Date.now();
    this._status = 'Ready · no commands sent'; this._pending = null; this._draft = null;
    this._renderShell();
  }
  setConfig(config) {
    if (config.dashboard_url || config.token || config.entities || config.topics) throw new Error('VentSys uses the fixed authenticated card contract; credentials and command overrides are unsupported.');
    if (config.layout && !['standard', 'touch'].includes(config.layout)) throw new Error('Layout must be standard or touch');
    this._config = { type: config.type, layout: config.layout || 'standard' };
    if (config.layout === 'touch') this._enableTouch();
  }
  getCardSize() { return 12; }
  getGridOptions() { return { columns: 'full', rows: 'auto', min_columns: 6 }; }
  set hass(value) { this._hass = value; this._scheduleRender(); }
  connectedCallback() {
    clearInterval(this._timer); this._timer = setInterval(() => this._update(), 1000);
    this._loadSchematic(); this._scheduleRender();
  }
  disconnectedCallback() {
    clearInterval(this._timer); cancelAnimationFrame(this._frame); this._frame = null;
    this._finish('Dashboard closed; command confirmation interrupted');
    this._draft = null; for (const dialog of this.shadowRoot.querySelectorAll('dialog')) dialog.close(); this._hass = null;
  }
  $(selector) { return this.shadowRoot.querySelector(selector); }
  _connected() { return this.isConnected && this._hass?.connection?.connected === true; }
  _scheduleRender() {
    if (this._frame) return;
    this._frame = requestAnimationFrame(() => { this._frame = null; this._update(); });
  }
  _text(selector, text) { const node = this.$(selector); if (node && node.textContent !== String(text)) node.textContent = text; }
  _event(message, severity = '') {
    this._events.unshift({ time: Date.now(), message, severity }); this._events.length = Math.min(this._events.length, 200);
    this._renderActivity();
  }
  _activityEntries(){return [...(this._historyEvents || []),...this._events].sort((a,b)=>b.time-a.time);}
  _renderActivity(){const list=this.$('#events');if(!list)return;list.replaceChildren();for(const entry of this._activityEntries().slice(0,100)){const li=document.createElement('li'),time=document.createElement('time');time.textContent=new Date(entry.time).toLocaleString();li.append(time,document.createTextNode(entry.message));if(entry.severity)li.dataset.severity=entry.severity;list.append(li);}}
  async _loadActivity(force=false){if(!this._connected() || !this._hass?.callWS || this._historyLoading || (!force && Date.now()-(this._historyLoaded || 0)<60000))return;this._historyLoading=true;this._historyLoaded=Date.now();try{const rows=await activity(this._hass);if(!this.isConnected)return;this._historyEvents=rows;this._renderActivity();this._scheduleRender();}catch(_){this._historyError=true;}finally{this._historyLoading=false;}}
  _openActivity(){const card=this.$('ventsys-activity-card');card.sessionEvents=this._events;card.hass=this._hass;this.$('#activity-dialog').showModal();card.load(true);}
  _observeChanges(){const states=this._hass?.states || {};if(!this._connected()){this._previousStates=null;return;}const selected=Object.entries(states).filter(([id])=>/^(binary_sensor|sensor|button)\.(garage_)?(ventsys_|sla_enclosure|fdm_enclosure)/.test(id));const previous=this._previousStates;this._previousStates=Object.fromEntries(selected.map(([id,s])=>[id,s.state]));if(!previous)return;for(const [id,state] of selected){if(previous[id]===undefined || previous[id]===state.state)continue;const unavailable=v=>['unknown','unavailable',''].includes(v);const label=state.attributes?.friendly_name || id;if(!unavailable(previous[id]) && unavailable(state.state))this._event(label+': unavailable','orange');else if(unavailable(previous[id]) && !unavailable(state.state))this._event(label+': available');else if(/alarm_latched$/.test(id))this._event(label+(state.state==='off'?': latch cleared':': alarm latched'),state.state==='on'?'orange':'');}}

  _renderShell() {
    // Static markup only; HA strings always enter through textContent.
    this.shadowRoot.innerHTML = `
      <link rel="stylesheet" href="${asset('ventsys-dashboard.css')}">
      <ha-card><main>
        <header><div><p class="eyebrow">GARAGE / VENTILATION</p><h1>Vent<span>Sys</span></h1></div><div class="connection"><span id="connection" role="status">Offline</span><span class="testing">Under testing</span></div></header>
        <section class="summary" aria-label="System summary"><div><span class="label">Reported configuration</span><strong id="mode">Offline</strong></div><div><span class="label">Controller reports</span><strong id="coverage">0 / 10 available</strong></div></section>
        <div class="alarm-actions"><span id="incident-symbol" role="status" aria-live="polite">● No active incidents</span><button type="button" id="open-alarm-menu">Clear alarms <span id="latched-count"></span></button></div>
        <section id="incident-panel" aria-label="Current VentSys incidents" hidden><h2>Current incidents</h2><ul id="incident-list"></ul></section>
        <details id="faults"><summary id="fault-title">Checking state</summary><ul id="fault-list"></ul></details>
        <section class="mode-controls" aria-label="Operating modes"><label class="setup-toggle"><input type="checkbox" id="setup-mode"> Setup/test — available valves only</label><p id="setup-note" hidden>Valve tests only. Fans are not commanded. Stop powered fans before testing. This does not establish ventilation.</p><div id="mode-groups"></div><p id="operating-intents"></p><p id="operating-result"></p><span id="mode-help">Checking operating controls.</span></section>
        <section class="workspace" aria-label="Ventilation schematic and controls">
          <div class="schematic-panel"><div class="section-head"><h2>Duct schematic</h2><button id="open-safety-menu" type="button">Safety</button></div><div id="schematic" aria-label="Ventilation duct schematic"><p>Loading schematic…</p></div><p class="caption">Positions show controller reports. Duct lines show routes, not measured airflow.</p></div>
          <section class="device-panel" aria-labelledby="device-name"><p class="eyebrow" id="device-zone">MAIN DUCT</p><h2 id="device-name">Main duct 1</h2><div class="reported"><span id="device-value">—</span><span id="device-unit">%</span></div><p id="device-source">Controller unavailable</p>
            <dl><div><dt>State updated</dt><dd id="device-age">Unavailable</dd></div><div><dt>Controller range</dt><dd id="device-range">0–100%</dd></div></dl>
            <div id="position-controls"><label for="position-slider">Requested position <output id="requested">0%</output></label><input id="position-slider" type="range" min="0" max="100" step="1" value="0"><div class="number-row"><label for="position-number">Percent</label><input id="position-number" type="number" min="0" max="100" step="1" value="0"></div><div id="reference-controls" hidden><label for="reference-opening">Observed opening (%)</label><input id="reference-opening" type="number" min="0" max="100" step="1"><button type="button" id="record-reference">Record without moving</button><p class="help">Records your observation as the controller reference; physical position is not measured.</p></div></div>
            <div id="fan-controls" hidden><div class="fan-actions"><button id="fan-on">Turn on</button><button id="fan-off">Turn off</button></div><label for="speed-slider">Requested speed <output id="speed-requested">0%</output></label><input id="speed-slider" type="range" min="0" max="100" step="1" value="0"></div><p id="device-help" class="help"></p>
            <section id="board-detail"><p id="maintenance-status"></p><button id="start-board-maintenance">Maintenance / take offline</button><button id="end-board-maintenance">Reactivate after reconnect</button><p id="board-action-status" role="status"></p><p id="sensor-alarm-status" role="status"></p><button id="sensor-ack" hidden>Acknowledge / clear stored latch</button><dl id="sensor-values"></dl><div id="detail-graphs"></div></section>
          </section>
        </section>
        <nav class="device-list" aria-label="Select controller"></nav><p id="command-status" role="status" aria-live="polite">Ready · no commands sent</p>
        <section class="pressure-panel"><h2>Enclosure pressure</h2><p>Inside minus outside. H port inside, L port outside.</p><label>Roughly equal tolerance ± <input id="pressure-tolerance" type="number" min="0" max="20" step="0.1" value="0.5"> Pa</label><p class="help">Provisional display tolerance; verify zero and tubing. Does not change alarm thresholds.</p><div class="pressure-readings"><section><h3>FDM array 1</h3><strong id="pressure-fdm" role="status">Unavailable</strong></section><section><h3>SLA array 1</h3><strong id="pressure-sla" role="status">Unavailable</strong></section></div></section><section class="sensors" aria-label="Environmental sensors"></section>
        <details class="events"><summary>System log details</summary><p class="help">Latest recorded HA activity and this dashboard session.</p><button id="full-activity">Open full activity history</button><ul id="events"><li>No commands sent this session.</li></ul></details>
        <footer>Authenticated through Home Assistant <span>VentSys ${VERSION}</span></footer>
      </main></ha-card>
      <dialog aria-labelledby="confirm-title"><form method="dialog"><p class="eyebrow">CONFIRM CHANGE</p><h2 id="confirm-title">Confirm change</h2><p id="confirm-description"></p><p class="help" id="confirm-note">The dashboard waits for controller reports after sending.</p><div id="purge-strength-options" hidden></div><div class="dialog-actions"><button value="cancel" id="cancel-command">Cancel</button><button type="button" id="confirm-command">Send command</button></div></form></dialog>
      <dialog id="safety-menu" aria-label="VentSys safety"><h2>Safety · under testing</h2><p id="safety-state"></p><p id="safety-automation-state"></p><p>Failsafe locks manual controls. Activation runs fire-safe ventilation only when the fire-safe sync automation is enabled. Deactivation does not clear board alarms or restore prior valve positions.</p><button id="safety-activate">Activate failsafe</button><button id="safety-deactivate">Deactivate failsafe</button><p id="safety-confirm-text"></p><button id="safety-confirm" hidden>Confirm change</button><p id="safety-result" role="status"></p><button id="safety-close">Close</button></dialog><dialog id="maintenance-dialog"><h2 id="maintenance-title">Board maintenance</h2><p id="maintenance-description"></p><button id="maintenance-cancel">Cancel</button><button id="maintenance-confirm">Confirm maintenance</button></dialog>
      <dialog id="activity-dialog" aria-label="Full activity history"><button id="close-activity">Close history</button><ventsys-activity-card></ventsys-activity-card></dialog>
      <dialog id="alarm-menu" aria-labelledby="alarm-menu-title"><h2 id="alarm-menu-title">Latched alarms</h2><p class="help">Acknowledging clears a stored alarm only when its board reports no active alarm. It does not calibrate a sensor.</p><ul id="latched-alarm-list"></ul><p id="alarm-menu-status" role="status" aria-live="polite"></p><div class="dialog-actions"><button type="button" id="close-alarm-menu">Close</button></div></dialog>`;
    for (const device of DEVICE_LIST) {
      const button = document.createElement('button'); button.dataset.device = device.key;
      const name = document.createElement('span'); name.textContent = device.short;
      const value = document.createElement('strong'); value.dataset.deviceValue = device.key; value.textContent = '—';
      button.append(name, value); button.addEventListener('click', () => this._select(device.key)); this.$('.device-list').append(button);
    }
    for (const [label, choices] of [
      ['Enclosure', [['booth','enclosure','Booth'],['fdm','enclosure','FDM'],['sla','enclosure','SLA']]],
      ['Print', [['fdm','print','FDM'],['sla','print','SLA'],['both','print','Both']]],
      ['Purge', [['fdm','purge','FDM'],['sla','purge','SLA'],['both','purge','Both']]],
      ['Close', [['fdm','off','FDM'],['sla','off','SLA'],['booth','off','Booth'],['all','off','All']]],
    ]) {
      const group=document.createElement('fieldset'), legend=document.createElement('legend');legend.textContent=label;group.append(legend);
      for (const [zone,operation,name] of choices) {
        const button=document.createElement('button');button.type='button';button.dataset.modeZone=zone;button.dataset.operation=operation;button.textContent=name;
        button.addEventListener('click',()=>this._operate(zone,operation));group.append(button);
      }
      this.$('#mode-groups').append(group);
    }
    for(const [level,label] of Object.entries(PURGE_STRENGTHS)) {
      const button=document.createElement('button');button.type='button';button.dataset.purgeStrength=level;button.textContent=`${label} · ${level} (${Number(level)*10}%)`;
      button.addEventListener('click',()=>{
        const choice=this._purgeChoice;if(!choice) return;
        this.$('dialog').close();this._draft={kind:'operation',target:choice.zone,value:'purge',revision:choice.revision,strength:Number(level)};this._submit();
      });this.$('#purge-strength-options').append(button);
    }
    for(const [key,config] of Object.entries(SENSOR_DEVICES)){const button=document.createElement('button');button.dataset.sensorDevice=key;button.textContent=config.name;button.addEventListener('click',()=>this._select(key));this.$('.device-list').append(button);}
    for (const [zone, config] of Object.entries(SENSORS)) {
      const section = document.createElement('section'); section.className = 'sensor-zone'; section.dataset.zone = zone;
      const title = document.createElement('h2'); title.textContent = config.label; section.append(title);
      const smoke = document.createElement('p'); smoke.dataset.smoke = zone; smoke.className = 'smoke'; smoke.textContent = (config.alarmLabel || 'Smoke') + ' · unavailable'; section.append(smoke);
      const dl = document.createElement('dl');
      for (const [kind, label] of [['temperature', 'Temperature'], ['humidity', 'Humidity'], ['baro', 'Barometric'], ['differential', 'Differential'], ['gas', 'Gas resistance'], ['wheel', 'Flow wheel']]) {
        if (!config[kind]) continue;
        const row = document.createElement('div'), dt = document.createElement('dt'), dd = document.createElement('dd'); dt.textContent = label; dd.dataset.sensor = zone + '-' + kind; dd.textContent = 'Unavailable'; row.append(dt, dd); dl.append(row);
      }
      section.append(dl); this.$('.sensors').append(section);
    }
    this.$('#open-safety-menu').addEventListener('click',()=>{this._safetyChoice=null;this.$('#safety-confirm').hidden=true;this._text('#safety-confirm-text','');this.$('#safety-menu').showModal();this._updateSafety();});
    this.$('#safety-close').addEventListener('click',()=>this.$('#safety-menu').close());
    for(const [id,value] of [['safety-activate','on'],['safety-deactivate','off']]) this.$('#'+id).addEventListener('click',()=>{this._safetyChoice=value;this._text('#safety-confirm-text',value==='on'?'Confirm activation: locks controls; may move valves and operate fans if fire-safe sync is enabled.':'Confirm deactivation: releases the manual-control lock. Board alarms remain.');this.$('#safety-confirm').hidden=false;});
    this.$('#safety-confirm').addEventListener('click',()=>this._setSafety());
    this.$('#pressure-tolerance').addEventListener('input', () => this._update());
    this.$('#start-board-maintenance').addEventListener('click',()=>this._reviewMaintenance());
    this.$('#end-board-maintenance').addEventListener('click',()=>this._reactivate());
    this.$('#sensor-ack').addEventListener('click',()=>this._sensorAck());
    this.$('#maintenance-cancel').addEventListener('click',()=>this.$('#maintenance-dialog').close());
    this.$('#maintenance-confirm').addEventListener('click',()=>this._applyMaintenance());
    this.$('#position-slider').addEventListener('input', e => { this._editing = true; this.$('#position-number').value = e.target.value; this._text('#requested', e.target.value + '%'); });
    this.$('#position-number').addEventListener('input', e => { this._editing = true; this.$('#position-slider').value = e.target.value; this._text('#requested', e.target.value + '%'); });
    this.$('#record-reference').addEventListener('click', () => this._reviewReference());
    this.$('#speed-slider').addEventListener('input', e => { this._editing = true; this._text('#speed-requested', e.target.value + '%'); });
    this.$('#position-slider').addEventListener('change', () => this._review('position', this._selected, Number(this.$('#position-number').value)));
    this.$('#position-number').addEventListener('keydown', event => { if(event.key === 'Enter') event.target.blur(); });
    this.$('#position-number').addEventListener('change', () => this._review('position', this._selected, Number(this.$('#position-number').value)));
    this.$('#speed-slider').addEventListener('change', () => this._review('speed', this._selected, Number(this.$('#speed-slider').value)));
    this.$('#fan-on').addEventListener('click', () => this._review('fan', this._selected, 'on'));
    this.$('#fan-off').addEventListener('click', () => this._review('fan', this._selected, 'off'));
    this.$('#setup-mode').addEventListener('change',()=>this._update());
    this.$('#open-alarm-menu').addEventListener('click', () => { this.$('#alarm-menu').showModal(); this._updateAlarms(); this.$('#close-alarm-menu').focus(); });
    this.$('#full-activity').addEventListener('click',()=>this._openActivity());
    this.$('#close-activity').addEventListener('click',()=>this.$('#activity-dialog').close());
    this.$('#close-alarm-menu').addEventListener('click', () => this.$('#alarm-menu').close());
    this.$('#confirm-command').addEventListener('click', () => this._submit());
    this.$('dialog').addEventListener('close', () => { this._draft = null; this._purgeChoice=null; });
    this._select(this._selected);
  }
  async _loadSchematic() {
    if (this._svgLoading || this.$('#diagram')) return;
    this._svgLoading = true;
    try {
      const response = await fetch(asset('ventsys-schematic.svg'), { credentials: 'same-origin' });
      if (!response.ok) throw new Error('Schematic asset unavailable');
      const parsed = new DOMParser().parseFromString(await response.text(), 'image/svg+xml'), svg = parsed.documentElement;
      if (svg.localName !== 'svg' || parsed.querySelector('parsererror')) throw new Error('Invalid schematic');
      if (svg.querySelector('script,foreignObject,image,a,use')) throw new Error('Unsupported schematic content');
      for (const node of [svg, ...svg.querySelectorAll('*')]) for (const attr of [...node.attributes]) if (/^on/i.test(attr.name) || /href/i.test(attr.name) || /url\((?!#)/i.test(attr.value)) throw new Error('Unsafe schematic attribute');
      this.$('#schematic').replaceChildren(document.importNode(svg, true));
      for (const device of DEVICE_LIST) {
        const node = this.$('#' + device.svg) || this.$('.' + device.svg); if (!node) continue;
        node.setAttribute('role', 'button'); node.setAttribute('tabindex', '0'); node.dataset.select = device.key;
        if (this._touch) {
          const bounds = node.getBBox(), hit = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
          const width = Math.max(108, bounds.width), height = Math.max(108, bounds.height);
          for (const [key, value] of Object.entries({x:bounds.x+(bounds.width-width)/2,y:bounds.y+(bounds.height-height)/2,width,height,fill:'transparent'})) hit.setAttribute(key, value);
          hit.classList.add('touch-hit'); node.prepend(hit);
        }
        node.addEventListener('click', () => this._select(device.key));
        node.addEventListener('keydown', e => { if (['Enter', ' '].includes(e.key)) { e.preventDefault(); this._select(device.key); } });
      }
      for(const [key,config] of Object.entries(SENSOR_DEVICES))for(const id of config.svg){const node=this.$('#'+id);if(!node)continue;node.dataset.sensorSelect=key;node.setAttribute('role','button');node.setAttribute('tabindex','0');node.style.cursor='pointer';node.addEventListener('click',()=>this._select(key));node.addEventListener('keydown',e=>{if(['Enter',' '].includes(e.key)){e.preventDefault();this._select(key);}});}
      for(const node of this.shadowRoot.querySelectorAll('[id^="env-"]')){const zone=node.id.slice(4).replace(/-(temperature|humidity|baro|gas|smoke)$/,'');const key={ambient:'ambient',fdm:'fdm_array',fdm_pipe:'fdm_pipe',sla:'sla_array',sla_pipe:'sla_pipe'}[zone];if(key){node.style.cursor='pointer';node.addEventListener('click',e=>{e.stopPropagation();this._select(key);});}}
      this._touchPanel('#environment-box'); this._touchPanel('#svg-log-box');
      this._update();
    } catch (error) { this._text('#schematic', 'Schematic unavailable. Use the labelled controller buttons below.'); this._event(error.message); }
    finally { this._svgLoading = false; }
  }
  _enableTouch() {
    if (this._touch) return;
    this._touch = true; this.setAttribute('layout', 'touch');
    const title = document.createElement('div'); title.className = 'touch-titlebar';
    title.innerHTML = '<strong class="touch-logo">PRINT<span>AIR</span>PIPE</strong><span id="touch-connection">Offline</span><span id="touch-reports">0 / 10 reports</span><time id="touch-clock"></time>';
    const toolbar = document.createElement('nav'); toolbar.className = 'touch-toolbar'; toolbar.setAttribute('aria-label', 'Touch screen menus');
    const dialog = document.createElement('dialog'); dialog.id = 'touch-menu'; dialog.setAttribute('aria-labelledby', 'touch-menu-title');
    dialog.innerHTML = '<div class="touch-dialog-head"><h2 id="touch-menu-title">Controllers</h2><button type="button" id="touch-close">Close</button></div>';
    this.shadowRoot.append(dialog);
    const groups = { controls: ['.device-panel', '.device-list'], modes: ['.mode-controls'], sensors: ['.pressure-panel', '.sensors'], status: ['.summary', '.alarm-actions', '#incident-panel', '#faults'], log: ['.events'] };
    this._touchPages = {};
    for (const [key, selectors] of Object.entries(groups)) {
      const section = document.createElement('section'); section.dataset.touchPage = key; section.hidden = true;
      for (const selector of selectors) section.append(this.$(selector));
      dialog.append(section); this._touchPages[key] = section;
      const button = document.createElement('button'); button.type = 'button'; button.dataset.touchMenu = key;
      button.textContent = {controls:'Controllers',modes:'Modes',sensors:'Sensors',status:'Status',log:'System log'}[key];
      button.addEventListener('click', () => this._openTouch(key)); toolbar.append(button);
    }
    dialog.append(this.$('#command-status'));
    this.$('#touch-close').addEventListener('click', () => dialog.close());
    const fullscreen = document.createElement('button'); fullscreen.type = 'button'; fullscreen.textContent = 'Full screen';
    fullscreen.addEventListener('click', async () => { try { if (document.fullscreenElement === this) await document.exitFullscreen(); else await this.requestFullscreen(); } catch (_) { this._event('Full screen unavailable in this browser'); } }); toolbar.append(fullscreen);
    const status = document.createElement('div'); status.className = 'touch-statusbar'; status.setAttribute('role', 'status');
    status.innerHTML = '<span>FLOW: <b>Unmeasured</b></span><span>MODE: <b id="touch-mode">Offline</b></span><span id="touch-outcome">Controller reports</span>';
    const main = this.$('main'); main.prepend(title, toolbar); main.append(status);
    for (const key of ['#environment-box', '#svg-log-box']) this._touchPanel(key);
  }
  _openTouch(key) {
    if (!this._touch) return;
    for (const [name, section] of Object.entries(this._touchPages)) section.hidden = name !== key;
    this._text('#touch-menu-title', {controls:'Controllers',modes:'Operating modes',sensors:'Environmental sensors',status:'System status',log:'System log · this session'}[key]);
    if (key === 'log') {this.$('.events').open = true;this._loadActivity(true);}
    if (key === 'status') this.$('#faults').open = true;
    const dialog = this.$('#touch-menu'); if (!dialog.open) dialog.showModal(); this.$('#touch-close').focus();
  }
  _touchPanel(selector) {
    const node = this.$(selector); if ((!this._touch && selector !== '#svg-log-box') || !node || node.dataset.touchPanel) return;
    node.dataset.touchPanel = 'true'; node.setAttribute('role', 'button'); node.setAttribute('tabindex', '0');
    const open = () => selector === '#svg-log-box' ? this._openActivity() : this._openTouch('sensors');
    node.addEventListener('click', open); node.addEventListener('keydown', event => { if (['Enter', ' '].includes(event.key)) { event.preventDefault(); open(); } });
  }
  _select(key) { if (!DEVICES[key] && !SENSOR_DEVICES[key]) return; this._selected = key; this._text('#board-action-status',''); this._editing = false; this._update(); if (this._touch) this._openTouch('controls'); }
  _snapshot() { const states = this._hass?.states || {}; return Object.fromEntries(DEVICE_LIST.map(d => [d.key, deviceState(d, states, this._connected())])); }
  _failsafe() { return this._hass?.states?.['input_boolean.ventsys_failsafe']?.state; }
  _environmentCell(zone, kind, text, description, alarm = false) {
    const node = this.$(`#env-${zone}-${kind}`); if (!node) return;
    node.textContent = text; node.setAttribute('aria-label', `${(ENVIRONMENT_SOURCES[zone] || SENSORS[zone]).label} ${kind}: ${description}`);
    node.style.fill = alarm ? '#ff826a' : text === '—' ? '#91a2b8' : '';
  }
  _updateSafety(){const states=this._hass?.states || {};this._text('#safety-state','Failsafe: '+this._failsafe());this._text('#safety-automation-state','Automatic cutoff: '+(states['automation.ventsys_fire_risk_cutoff']?.state || 'unavailable')+' · Fire-safe sync: '+(states['automation.ventsys_fail_safe_sync_to_topics']?.state || 'unavailable'));const valid=this._connected() && ['on','off'].includes(this._failsafe());this.$('#safety-activate').disabled=!valid || this._failsafe()==='on';this.$('#safety-deactivate').disabled=!valid || this._failsafe()==='off';}
  async _setSafety(){const value=this._safetyChoice;if(!this._connected() || !['on','off'].includes(value) || this._safetySending)return;this._safetySending=true;this.$('#safety-confirm').disabled=true;try{await this._hass.callService('input_boolean',value==='on'?'turn_on':'turn_off',{entity_id:'input_boolean.ventsys_failsafe'});this._event('Failsafe '+(value==='on'?'activation':'deactivation')+' requested');this._text('#safety-result','Request sent; current state is shown above.');this.$('#safety-confirm').hidden=true;this._safetyChoice=null;}catch(_){this._text('#safety-result','Failsafe request failed.');}finally{this._safetySending=false;this.$('#safety-confirm').disabled=false;this._updateSafety();}}
  _backendBlock(includeBusy = true) {
    this._updateSafety();
    const states = this._hass?.states || {};
    if (!this._connected()) return 'Home Assistant is offline';
    if (this._failsafe() !== 'off') return this._failsafe() === 'on' ? 'Failsafe is active; manual controls are locked' : 'Failsafe status is unavailable';
    const fire = states['script.ventsys_mode_fire_safe']?.state;
    if (fire !== 'off') return fire === 'on' ? 'Fire response is running; manual controls are locked' : 'Fire response status is unavailable';
    const dispatcher = states['script.ventsys_normal_command']?.state;
    if (!['on', 'off'].includes(dispatcher)) return 'Command dispatcher is unavailable';
    return includeBusy && (dispatcher === 'on' || states['script.ventsys_set_operating_mode']?.state === 'on' || states['script.ventsys_test_valves']?.state === 'on') ? 'Another VentSys command is running; wait before changing controls.' : '';
  }
  _operatingSummary(snapshot,connected) {
    if(!connected) return 'Offline';
    const saved=operatingState(this._hass?.states || {});
    if(!saved) return deriveMode(snapshot,connected);
    const labels=['fdm','sla'].filter(z=>saved[z] !== 'off').map(z=>z.toUpperCase()+' '+saved[z]);
    if(saved.booth !== 'off') labels.push('Booth');
    if(!labels.length) return 'No requested modes';
    const expected=operatingPlan(saved,'fdm',saved.fdm).targets;
    const busy=this._hass.states['script.ventsys_set_operating_mode']?.state === 'on';
    return labels.join(' + ') + (busy ? ' · applying' : matchesExpected(expected,snapshot) ? ' · reported' : ' · reports differ');
  }
  _expected(request) {
    if(request.kind === 'setup') return Object.fromEntries(Object.entries(setupTargets(request.target,request.value)).filter(([key])=>request.included.includes(key)));
    return request.kind === 'operation' ? operatingPlan(operatingState(this._hass?.states || {}),request.target,request.value,request.strength).targets : commandExpected(request,this._snapshot());
  }
  _blocked(request) {
    const maintenanceKey=CONTROL_MAINTENANCE[request.target];if(maintenanceKey && this._hass?.states?.['input_boolean.ventsys_maintenance_'+maintenanceKey]?.state==='on')return 'Board is in maintenance; reconnect power and reactivate first.';
    const backend=this._backendBlock(); if(backend) return backend;
    if(request.kind === 'reference') {
      const states=this._hass?.states || {}, saved=operatingState(states), device=DEVICES[request.target], report=this._snapshot()[request.target];
      const pwm=request.target === 'fdm_360' ? 'binary_sensor.garage_ventsys_sla_360_intake_valve_pwm_commanded_active' : 'binary_sensor.garage_ventsys_fdm_360_intake_valve_pwm_commanded_active';
      if(!device?.expectedRange || !Number.isInteger(request.opening) || request.opening < 0 || request.opening > 100) return 'Enter an opening from 0 to 100%';
      if(!saved || saved.revision !== request.revision || ['fdm','sla','booth'].some(z=>saved[z] !== 'off')) return 'Stop all operating modes first';
      if(!['fan.inline_fan','fan.spray_booth_fan'].every(id=>states[id]?.state === 'off')) return 'Both fan reports must be available and off';
      if(states['script.ventsys_record_intake_reference']?.state !== 'off') return 'Reference service unavailable or busy';
      if(states[pwm]?.state !== 'off' || !report?.available || !report.native) return 'Controller and inactive PWM reports are required';
      return '';
    }
    if(request.kind === 'setup') {
      const states=this._hass?.states || {}, saved=operatingState(states);
      if(states['script.ventsys_test_valves']?.state !== 'off') return 'Setup test service unavailable or busy';
      if(!saved || saved.revision !== request.revision) return 'Operating intents changed; choose the test again';
      if(['fdm','sla','booth'].some(z=>saved[z] !== 'off')) return 'Stop operating modes before valve setup testing';
      if(['fan_main','fan_booth'].some(key=>this._snapshot()[key].value === 'on')) return 'Stop running fans before valve setup testing';
      if(!request.included.length) return 'No available valves for this test';
      for(const [key,value] of Object.entries(this._expected(request))) {
        const reason=commandBlock(commandRequest('position',key,value),this._snapshot(),this._connected(),this._failsafe());if(reason) return reason;
      }
      return '';
    }
    if(request.kind === 'operation') {
      if(this._hass?.states?.['script.ventsys_set_operating_mode']?.state !== 'off') return 'Operating mode service is unavailable or busy';
      const saved=operatingState(this._hass.states);
      if(!saved || saved.revision !== request.revision) return 'Operating intents changed; refresh and try again';
      for(const [key,value] of Object.entries(this._expected(request))) {
        const speed=key.endsWith('_speed'), name=speed ? key.slice(0,-6) : key, device=DEVICES[name];
        const reason=commandBlock(commandRequest(speed ? 'speed' : device.fan ? 'fan' : 'position',name,value),this._snapshot(),this._connected(),this._failsafe());
        if(reason) return reason;
        if(!speed && device.fan && value === 'on' && !(name+'_speed' in this._expected(request)) && !(this._snapshot()[name].speed > 0)) return 'Set a nonzero speed for ' + device.name;
      }
      return '';
    }
    const state=operatingState(this._hass?.states || {});
    if(state) {
      const active=operatingPlan(state,'fdm',state.fdm).targets;
      // targets also include current active shared paths. Filter release actions
      // by using an unchanged single-enclosure transition.
      if(request.kind === 'speed' && (active[request.target] === 'on' && request.value === 0 || active[request.target+'_speed'] !== undefined && active[request.target+'_speed'] !== request.value) || request.kind !== 'speed' && request.target in active && active[request.target] !== request.value) return 'This controller is required by an active mode; stop that mode first';
    }
    return commandBlock(request,this._snapshot(),this._connected(),this._failsafe());
  }
  _setupRequest(zone,operation) {
    const saved=operatingState(this._hass?.states || {}), snapshot=this._snapshot();
    return {kind:'setup',target:zone,value:operation,revision:saved?.revision,included:Object.keys(setupTargets(zone,operation)).filter(key=>snapshot[key]?.available && snapshot[key].native)};
  }
  _reviewSetup(zone,operation) {
    const request=this._setupRequest(zone,operation), reason=this._blocked(request);
    if(this._pending || window[lockKey] || reason) {this._status=reason || 'Another command is pending';this._update();return;}
    const all=setupTargets(zone,operation), expected=this._expected(request);
    this._draft=request;this.$('#purge-strength-options').hidden=true;this.$('#confirm-command').hidden=false;
    this._text('#confirm-title',`Setup/test: ${zone.toUpperCase()} ${operation}`);
    this._text('#confirm-description','Valve targets: '+Object.entries(expected).map(([key,value])=>DEVICES[key].name+' '+display(openingPercent(DEVICES[key],value))+'%').join(', ')+'. Skipped: '+Object.keys(all).filter(key=>!request.included.includes(key)).map(key=>DEVICES[key].name).join(', ')+'.');
    this._text('#confirm-note','Fans are not commanded. Stop any powered fans before testing. This is not an operating mode and does not establish ventilation.');
    this.$('dialog').showModal();this.$('#cancel-command').focus();
  }
  _operate(zone,operation) {
    if(this.$('#setup-mode').checked) {this._reviewSetup(zone,operation);return;}
    const saved=operatingState(this._hass?.states || {});
    if(!saved) {this._status='Operating state unavailable';this._update();return;}
    if(operation === 'purge') {
      if(this._pending || window[lockKey]) return;
      this._purgeChoice={zone,revision:saved.revision};this.$('#purge-strength-options').hidden=false;this.$('#confirm-command').hidden=true;
      this._text('#confirm-title',zone.toUpperCase()+' purge strength');this._text('#confirm-description','Choose the requested main fan level. The higher active purge request wins.');
      this._text('#confirm-note','Levels 2/4/6/8/10 request 20/40/60/80/100%. Physical mapping awaits calibration.');this.$('dialog').showModal();this.$('#cancel-command').focus();this._update();return;
    }
    const request={kind:'operation',target:zone,value:operation,revision:saved.revision};
    const reason=this._blocked(request);if(reason){this._status=reason;this._update();return;}
    this._draft=request;this._submit();
  }
  _reviewReference() {
    const opening=Number(this.$('#reference-opening').value), saved=operatingState(this._hass?.states || {});
    const request={kind:'reference',target:this._selected,opening,value:servoPercent(DEVICES[this._selected],opening),revision:saved?.revision};
    const reason=this.$('#reference-opening').value.trim() === '' ? 'Enter an observed opening' : this._blocked(request);
    if(reason || this._pending || window[lockKey]) {this._status=reason || 'Another command is pending';this._update();return;}
    this._draft=request;this.$('#purge-strength-options').hidden=true;this.$('#confirm-command').hidden=false;
    this._text('#confirm-title','Record observed opening');
    this._text('#confirm-description',`${DEVICES[request.target].name}: record ${display(openingPercent(DEVICES[request.target],request.value))}%?`);
    this._text('#confirm-note','This changes the saved controller reference without moving the valve. It is your observation, not a measured position.');
    this.$('dialog').showModal();this.$('#cancel-command').focus();
  }
  _review(kind, target, value) {
    try {
      if(kind === 'position' && (!Number.isInteger(value) || value < 0 || value > 100)) throw new Error('Invalid percentage');
      const request = commandRequest(kind, target, kind === 'position' ? servoPercent(DEVICES[target],value) : value);
      if (this._pending || window[lockKey]) throw new Error('Another dashboard command is awaiting confirmation');
      const blocked = this._blocked(request); if (blocked) throw new Error(blocked);
      const snapshot = this._snapshot(), expected = this._expected(request);
      if (request.scope === 'available') request.included = Object.keys(expected);
      this.$('#purge-strength-options').hidden=true;this.$('#confirm-command').hidden=false;this._text('#confirm-note','The dashboard waits for controller reports after sending.');
      this._draft = request;
      const label = kind === 'mode' ? MODE_LABELS[target] : DEVICES[target].name;
      this._text('#confirm-title', label); this._text('#confirm-description', kind === 'mode' ? 'Apply ' + label + '?' : `${label}: ${kind === 'speed' ? 'speed ' : ''}${kind === 'position' ? display(openingPercent(DEVICES[target],request.value)) : value}${typeof value === 'number' ? '%' : ''}?`);
      this.$('dialog').showModal(); this.$('#cancel-command').focus();
    } catch (error) { this._status = error.message; this._update(); }
  }
  async _submit() {
    const request = this._draft; if (!request || this._pending || window[lockKey]) return;
    const blocked = this._blocked(request); this.$('dialog').close();
    if (blocked) { this._status = blocked; this._update(); return; }
    const snapshot = this._snapshot(), expected = this._expected(request);
    const pending = { request, expected, serviceDone: false, baseline: {}, unchanged: {} };
    for (const [key, value] of Object.entries(expected)) {
      const state = snapshot[key.endsWith('_speed') ? key.slice(0, -6) : key];
      pending.baseline[key] = state?.timestamp; pending.unchanged[key] = (key.endsWith('_speed') ? state.speed : state.value) === value;
    }
    this._pending = pending; window[lockKey] = this;
    this._status = 'Pending · submitting request'; this._event('Requested ' + (['operation','setup'].includes(request.kind) ? (request.kind === 'setup' ? 'Valve setup test ' : '')+request.target.toUpperCase() + ' ' + request.value : DEVICES[request.target].name)); this._update();
    pending.timer = setTimeout(() => { if (this._pending === pending) { this._finish('Timed out · controller confirmation not received'); this._update(); } }, request.kind === 'operation' ? 45000 : 12000);
    try {
      await this._hass.callService('script', request.kind === 'reference' ? 'ventsys_record_intake_reference' : request.kind === 'setup' ? 'ventsys_test_valves' : request.kind === 'operation' ? 'ventsys_set_operating_mode' : 'ventsys_dashboard_command', request.kind === 'reference' ? {target:request.target,opening:request.opening,revision:request.revision} : request.kind === 'setup' ? {zone:request.target,operation:request.value,revision:request.revision,included:request.included} : request.kind === 'operation' ? {zone:request.target,operation:request.value,revision:request.revision,...(request.strength === undefined ? {} : {strength:request.strength})} : request);
      if (this._pending !== pending) return;
      if (Object.values(pending.unchanged).every(Boolean)) {
        this._finish(request.kind === 'reference' ? 'Reference request sent · storage and physical position unverified' : request.kind === 'setup' ? 'Valve test sent · target already reported; ventilation not established' : 'Command sent · target already reported'); this._update(); return;
      }
      pending.serviceDone = true; this._status = 'Pending · waiting for a newer controller report'; this._update();
    } catch (_) { if (this._pending === pending) { this._finish('Failed · HA rejected or could not complete the command'); this._update(); } }
  }
  _finish(message) {
    if (!this._pending) return;
    clearTimeout(this._pending.timer); this._pending = null;
    if (window[lockKey] === this) delete window[lockKey];
    this._status = message; this._event(message);
  }
  _updateAlarms() {
    const connected = this._connected(), alarms = latchedAlarms(this._hass?.states || {}, connected);
    this._text('#latched-count', alarms.length ? `(${alarms.length})` : '');
    this.$('#open-alarm-menu').classList.toggle('alarm', alarms.length > 0);
    if (!this.$('#alarm-menu').open) { this._alarmListSignature = null; return; }
    const signature = JSON.stringify([connected, alarms.map(({id, label, active, fault, canAcknowledge}) => [id, label, active, fault, Boolean(canAcknowledge)]), Boolean(this._acknowledging)]);
    if (signature === this._alarmListSignature) return;
    this._alarmListSignature = signature;
    const list = this.$('#latched-alarm-list'); list.replaceChildren();
    if (!connected || !alarms.length) {
      const item = document.createElement('li'); item.textContent = connected ? 'No latched VentSys alarms.' : 'Home Assistant is offline; alarm state unavailable.'; list.append(item); return;
    }
    for (const alarm of alarms) {
      const item = document.createElement('li'), label = document.createElement('span'), button = document.createElement('button');
      label.textContent = alarm.label + (alarm.active ? ' · alarm still active' : alarm.fault ? ' · sensor fault; inspect first' : ' · stored alarm');
      button.type = 'button'; button.textContent = 'Acknowledge'; button.disabled = !alarm.canAcknowledge || Boolean(this._acknowledging);
      button.title = alarm.active ? 'Current alarm is active' : alarm.fault ? 'Sensor fault is active' : !alarm.canAcknowledge ? 'Acknowledge control unavailable' : '';
      button.addEventListener('click', () => this._acknowledgeAlarm(alarm)); item.append(label, button); list.append(item);
    }
  }
  _updateIncidents() {
    const incidents = activeIncidents(this._hass?.states || {}, this._connected());
    const signature = JSON.stringify(incidents.map(({id,severity,label}) => [id,severity,label]));
    const highest = incidents.some(item => item.severity === 'red') ? 'red' : incidents.some(item => item.severity === 'orange') ? 'orange' : incidents.length ? 'blue' : 'clear';
    const symbol = this.$('#incident-symbol'); symbol.dataset.severity = highest;
    symbol.textContent = incidents.length ? `${highest === 'red' ? '⚠' : '◆'} ${incidents.length} active incident${incidents.length === 1 ? '' : 's'}` : '● No active incidents';
    this.$('#incident-panel').hidden = !incidents.length;
    for (const zone of ['fdm','sla','ambient']) {
      const panel = this.$(`.sensor-zone[data-zone="${zone}"]`);
      panel.dataset.severity = incidents.some(item => item.zone === zone && item.severity === 'red') ? 'red' : incidents.some(item => item.zone === zone && item.severity === 'orange') ? 'orange' : incidents.some(item => item.zone === zone) ? 'blue' : '';
    }
    if (signature === this._incidentSignature) return;
    const prior = this._incidentIds || new Set(), current = new Set(incidents.map(item => item.id));
    for (const item of incidents) if (this._incidentIds && !prior.has(item.id)) this._event(`${item.source}: ${item.label}`, item.severity);
    this._incidentIds = current; this._incidentSignature = signature;
    const list = this.$('#incident-list'); list.replaceChildren();
    for (const item of incidents) {
      const li = document.createElement('li'); li.dataset.severity = item.severity;
      const mark = document.createElement('strong'); mark.textContent = item.severity === 'red' ? '⚠ Alarm' : item.severity === 'orange' ? '◆ Warning' : '● Info';
      const content = document.createElement('span'); content.textContent = `${item.source}: ${item.label}`;
      li.append(mark, content); list.append(li);
    }
  }
  async _acknowledgeAlarm(alarm) {
    const current = latchedAlarms(this._hass?.states || {}, this._connected()).find(entry => entry.id === alarm.id);
    if (!current?.canAcknowledge || this._acknowledging) return;
    this._acknowledging = true; this._text('#alarm-menu-status', `Acknowledging ${current.label}…`); this._updateAlarms();
    try {
      await this._hass.callService('button', 'press', { entity_id: current.buttonId });
      this._event('Acknowledge requested: '+current.label);
      this._text('#alarm-menu-status', `Acknowledge sent to ${current.label}; waiting for the board to report clear.`);
    } catch (_) { this._text('#alarm-menu-status', `Could not acknowledge ${current.label}. Check the device in Home Assistant.`); }
    finally { this._acknowledging = false; this._updateAlarms(); }
  }
  _update() {
    if (!this.$('#mode')) return;
    const connected = this._connected(), states = this._hass?.states || {}, snapshot = this._snapshot(), now = Date.now();
    if (!connected && this._pending) this._finish('Disconnected · command outcome unknown');
    this._updateAlarms();
    this._loadActivity();
    this._observeChanges();
    this._updateIncidents();
    const interruption = this._backendBlock(false);
    if (connected && interruption && this._pending) this._finish('Interrupted · ' + interruption + '. Command outcome unverified.');
    if (!connected && this._draft) this.$('dialog').close();
    const pending = this._pending;
    if (pending?.serviceDone && matchesExpected(pending.expected, snapshot) && Object.keys(pending.expected).every(key => {
      const state = snapshot[key.endsWith('_speed') ? key.slice(0, -6) : key];
      return pending.unchanged[key] || (state.timestamp !== null && state.timestamp > (pending.baseline[key] ?? 0));
    })) { this._finish(pending.request.kind === 'setup' ? 'Valve test controller reports confirmed · ventilation not established' : pending.request.scope === 'available' ? 'Available controller targets reported' : 'Confirmed by controller report'); this._editing = false; }
    this._text('#connection', connected ? 'HA connected' : 'Offline'); this.$('#connection').className = connected ? 'live' : 'offline';
    if (this._touch) {
      this._text('#touch-connection', connected ? 'HA connected' : 'Offline');
      this._text('#touch-reports', `${DEVICE_LIST.filter(d => snapshot[d.key].available && (d.fan || snapshot[d.key].native)).length} / 10 reports`);
      this._text('#touch-clock', new Date(now).toLocaleTimeString([], {hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false}));
      this._text('#touch-mode', this._operatingSummary(snapshot, connected));
      this._text('#touch-outcome', this._pending ? 'Command pending' : /Interrupted|Failed|Timed out|Disconnected/.test(this._status) ? 'Command outcome unverified' : 'Controller reports');
    }
    this._text('#mode', this._operatingSummary(snapshot, connected)); this._text('#coverage', `${DEVICE_LIST.filter(d => snapshot[d.key].available && (d.fan || snapshot[d.key].native)).length} / 10 available`); this._text('#command-status', this._status);
    this.$('#command-status').classList.toggle('failed', /Failed|Timed out|Disconnected|Interrupted/.test(this._status));
    const faults = [], failsafe = this._failsafe();
    if (!connected) faults.push('Home Assistant connection unavailable. All controls are disabled.');
    if (failsafe !== 'off') faults.push(failsafe === 'on' ? 'FAILSAFE ACTIVE. Manual controls are locked.' : 'Failsafe state is unavailable. Manual controls are locked.');
    else if (connected && this._backendBlock(false)) faults.push(this._backendBlock(false));
    for (const device of DEVICE_LIST) {
      const state = snapshot[device.key], text = state.available ? display(device.fan ? state.value : openingPercent(device,state.value)) + (device.fan ? '' : '%') : 'Unavailable';
      this._text(`[data-device-value="${device.key}"]`, text);
      const button = this.$(`[data-device="${device.key}"]`); button.setAttribute('aria-pressed', String(device.key === this._selected)); button.classList.toggle('unavailable', !state.available);
      if (!state.available && connected) faults.push(device.name + ': not yet set up or currently unavailable.');
      else if (!device.fan && !state.native && connected) faults.push(device.name + ': only retained MQTT state is available; native controller is not adopted.');
      if (state.available && !device.fan && (state.min !== (device.expectedRange?.min ?? 0) || state.max !== (device.expectedRange?.max ?? 100))) faults.push(`${device.name}: reported range ${state.min}–${state.max}% differs from its configured range.`);
      this._text('#' + device.text, state.available ? (device.fan ? (state.speed === null ? '—' : display(state.speed) + '%') : display(device.fan ? state.value : openingPercent(device,state.value)) + '%') : '—');
      const node = this.$(`[data-select="${device.key}"]`);
      if (node) { node.classList.toggle('selected', device.key === this._selected); node.classList.toggle('unknown', !state.available); node.setAttribute('aria-label', `Select ${device.name}, ${text}`); }
    }
    for (const [zone, config] of Object.entries(SENSORS)) {
      // Device availability is independent of one reading or a stale sample.
      if (zone !== 'ambient') {
        const online=connected && ['temperature','humidity','baro','gas','smoke'].some(kind => (config[kind] || []).some(id => { const entity=states[id]; return entity && !['','unknown','unavailable','none'].includes(String(entity.state ?? '').toLowerCase()); }));
        const n=zone === 'fdm' ? 1 : 2;
        for (const id of ['circle','label','iaq']) { const node=this.$(`#bme${n}-${id}`); if(node) node.style.opacity=online ? '1' : '.35'; }
      }
      const smoke = smokeState(config.smoke, states, connected, this._alarms[zone], now); this._alarms[zone] = smoke.alarm;
      const alarmLabel = config.alarmLabel || 'Smoke', stateLabel = smoke.label.replace('SMOKE', alarmLabel.toUpperCase());
      this._text(`[data-smoke="${zone}"]`, alarmLabel + ' · ' + stateLabel); this.$(`[data-smoke="${zone}"]`).className = 'smoke ' + (smoke.alarm ? 'alarm' : smoke.unknown ? 'unknown' : 'clear');
      this.$(`[data-smoke="${zone}"]`).setAttribute('role', smoke.alarm ? 'alert' : 'status');
      this._environmentCell(zone, 'smoke', smoke.alarm ? 'ALARM' : smoke.unknown ? '—' : 'Clear', stateLabel, smoke.alarm);
      if (smoke.alarm) faults.unshift(config.label + ': ' + stateLabel + '.'); else if (smoke.unknown && connected) faults.push(config.label + `: ${alarmLabel} reading unavailable or stale.`);
      for (const kind of ['temperature', 'humidity', 'baro', 'differential', 'gas', 'wheel']) {
        if (!config[kind]) continue;
        const reading = measurement(kind, sensorValue(config[kind], states, connected, now), states);
        if (kind === 'differential') {
          const input = this.$('#pressure-tolerance');
          const tolerance = input.value.trim() !== '' && input.validity.valid ? Number(input.value) : null;
          this._text('#pressure-' + zone, reading.value === null ? reading.reason : tolerance === null ? 'Enter tolerance 0–20 Pa' : `${pressureRelation(reading.value, tolerance)} · ${reading.value.toFixed(2)} Pa`);
          const relation=reading.value === null || tolerance === null ? 'Unavailable' : pressureRelation(reading.value,tolerance);
          this._text('#pressure-'+zone+'-icon',relation === 'Unavailable' ? '?' : relation === 'Roughly equal' ? '=' : relation === 'Negative pressure' ? '↓ −' : '↑ +');
          this._text('#pressure-'+zone+'-value',reading.value === null ? '' : reading.value.toFixed(2)+' Pa');
          const icon=this.$('#pressure-'+zone+'-icon');if(icon){icon.setAttribute('aria-label',relation);icon.setAttribute('fill',relation==='Unavailable'?'#91a2b8':relation==='Positive pressure'?'#ffb000':relation==='Negative pressure'?'#70c8ff':'#00ff88');}

        }
        if (kind === 'wheel' && zone !== 'ambient') this._flowAnimation(zone === 'fdm' ? 1 : 2,reading);

        if (connected && reading.value === null) faults.push(`${config.label}: ${kind === 'gas' ? 'gas resistance' : kind} ${reading.reason === 'Unavailable' ? 'not yet set up or currently unavailable' : reading.reason.toLowerCase()}.`);
        this._text(`[data-sensor="${zone}-${kind}"]`, reading.value === null ? reading.reason : sensorDisplay(kind,reading.value) + ' ' + reading.unit);
        this.$(`[data-sensor="${zone}-${kind}"]`).title = reading.id ? reading.id + (reading.timestamp ? ' · state updated ' + new Date(reading.timestamp).toLocaleString() : '') : 'No adopted sensor';
        if (zone !== 'ambient') { const n = zone === 'fdm' ? 1 : 2; if (kind === 'gas') this._text('#bme' + n + '-iaq', reading.value === null ? '—' : sensorDisplay(kind,reading.value)); if (kind === 'wheel') this._text('#flow' + n + '-rate', reading.value === null ? reading.reason : sensorDisplay(kind,reading.value)); }
        this._environmentCell(zone, kind, reading.value === null ? '—' : sensorDisplay(kind,reading.value), reading.value === null ? reading.reason : sensorDisplay(kind,reading.value) + ' ' + reading.unit);
      }
    }
    for(const [zone,config] of Object.entries(ENVIRONMENT_SOURCES)) {
      for(const kind of ['temperature','humidity','baro','gas']) {
        const reading=measurement(kind,sensorValue(config[kind],states,connected,now));
        this._environmentCell(zone,kind,reading.value === null ? '—' : sensorDisplay(kind,reading.value),reading.value === null ? reading.reason : reading.value+' '+reading.unit);
      }
      if(zone==='fdm_pipe' || zone==='sla_pipe'){const n=zone==='fdm_pipe'?1:2;const online=connected && ['temperature','humidity','baro','gas','smoke'].some(kind=>(config[kind] || []).some(id=>states[id] && !['unknown','unavailable',''].includes(states[id].state)));for(const part of ['circle','label','iaq']){const node=this.$('#bme'+n+'-'+part);if(node)node.style.opacity=online?'1':'.35';}const gas=measurement('gas',sensorValue(config.gas,states,connected,now));this._text('#bme'+n+'-iaq',gas.value===null?'—':sensorDisplay('gas',gas.value));}
      this._environmentAlarms ||= {};const status=smokeState(config.smoke || [],states,connected,this._environmentAlarms[zone],now);this._environmentAlarms[zone]=status.alarm;
      this._environmentCell(zone,'smoke',status.alarm ? 'ALARM' : status.unknown ? '—' : 'Clear',status.label,status.alarm);
    }
    if(connected) faults.push(...operatingWarnings(operatingState(states),snapshot));
    faults.push(...airflowWarnings(snapshot)); this.$('#fault-list').replaceChildren();
    const current = new Set(faults); for (const key of this._faultSince.keys()) if (!current.has(key)) this._faultSince.delete(key);
    for (const fault of faults) { if (!this._faultSince.has(fault)) this._faultSince.set(fault, now); const li = document.createElement('li'); li.textContent = fault + ' Since ' + new Date(this._faultSince.get(fault)).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }); this.$('#fault-list').append(li); }
    const smokeAlarm = Object.values(this._alarms).some(Boolean), fireRunning = states['script.ventsys_mode_fire_safe']?.state === 'on';
    this._text('#fault-title', smokeAlarm ? 'Smoke alarm reported · expand for details' : failsafe === 'on' ? 'Failsafe active · manual controls locked' : fireRunning ? 'Fire response running · manual controls locked' : faults.length ? `${faults.length} setup and status notes` : 'No dashboard faults detected');
    this.$('#faults').classList.toggle('alarm', smokeAlarm || failsafe === 'on' || fireRunning);
    if (this._touch) { const statusButton = this.$('[data-touch-menu="status"]'); statusButton.classList.toggle('alarm', smokeAlarm || failsafe === 'on' || fireRunning); statusButton.textContent = smokeAlarm ? 'Status · Alarm' : failsafe === 'on' || fireRunning ? 'Status · Locked' : connected ? 'Status' : 'Status · Offline'; }
    this._updateDevice(snapshot, connected);
    const saved=operatingState(states), busy=Boolean(this._pending || window[lockKey]);
    this._text('#operating-intents',saved ? `Requested: FDM ${saved.fdm}${saved.fdm === 'purge' ? ' '+PURGE_STRENGTHS[saved.fdm_strength] : ''} · SLA ${saved.sla}${saved.sla === 'purge' ? ' '+PURGE_STRENGTHS[saved.sla_strength] : ''} · Booth ${saved.booth === 'enclosure' ? 'on' : 'off'}` : 'Operating intents unavailable');
    const result=states['input_text.ventsys_operating_result']?.state;
    this._text('#operating-result',!result || ['unknown','unavailable'].includes(result) ? 'No operating result recorded' : result.startsWith('Applying') && states['script.ventsys_set_operating_mode']?.state === 'off' ? 'Previous transition interrupted; inspect controller reports and verify released paths. Retrying may not close them.' : 'Last result: '+result.replace('retry to reconcile','inspect controller reports and verify released paths; retry may not close them'));
    this._text('#mode-help','Modes combine across enclosures. Changing a mode replaces only the selected enclosure. Fan speeds are retained.');
    const setup=this.$('#setup-mode').checked;this.$('#setup-note').hidden=!setup;
    const modeReasons=new Set();
    for(const button of this.shadowRoot.querySelectorAll('[data-mode-zone]')) {
      const zone=button.dataset.modeZone, operation=button.dataset.operation;
      const request=setup ? this._setupRequest(zone,operation) : {kind:'operation',target:zone,value:operation,revision:saved?.revision,...(operation === 'purge' ? {strength:6} : {})};
      const reason=saved ? this._blocked(request) : 'Operating mode service unavailable';
      button.disabled=busy || Boolean(reason) && (setup || operation !== 'purge');button.title=reason || '';if(reason) modeReasons.add(reason);
      button.setAttribute('aria-pressed',String(!setup && saved && (zone === 'both' ? saved.fdm === operation && saved.sla === operation : zone === 'all' ? Object.values({fdm:saved.fdm,sla:saved.sla,booth:saved.booth}).every(x=>x==='off') : saved[zone] === operation)));
    }
    if(this._purgeChoice) {
      const choice=this._purgeChoice, reasons=new Set();
      for(const button of this.shadowRoot.querySelectorAll('[data-purge-strength]')) {
        const reason=this._blocked({kind:'operation',target:choice.zone,value:'purge',revision:choice.revision,strength:Number(button.dataset.purgeStrength)});
        button.disabled=busy || Boolean(reason);button.title=reason || '';if(reason) reasons.add(reason);
      }
      this._text('#confirm-description',reasons.size ? 'Cannot start purge: '+[...reasons].join(' · ') : 'Choose the requested main fan level. The higher active purge request wins.');
    }
    if(modeReasons.size) this._text('#mode-help','Unavailable actions: '+[...modeReasons].join(' · '));
    const boothWheel=measurement('wheel',sensorValue(['sensor.ventsys_booth_airflow_sensor_flow_meter_wheel_speed'],states,connected,now));
    this._flowAnimation(3,boothWheel);
    this._text('#flow3-rate',boothWheel.value === null ? boothWheel.reason : sensorDisplay('wheel',boothWheel.value));
    this._updateSchematic(snapshot);
  }
  _flowAnimation(index,reading) {
    const moving=reading.value !== null && reading.value > 0;
    const entity=reading.id && this._hass?.states?.[reading.id];
    const offline=!this._hass?.connection?.connected || !entity || ['unavailable','unknown',''].includes(String(entity.state).toLowerCase());
    const circle=this.$(`#flow${index}-circle`); if(circle) circle.style.opacity=offline ? '.35' : '1';
    for(const part of ['bot','ctr','top']) {
      const arrow=this.$(`#flow${index}-arrow-${part}`);
      if(arrow) {arrow.classList.toggle('flow-moving',moving);arrow.style.opacity=''; arrow.style.fill=moving ? '#00aaff' : '#ff2200'; arrow.style.filter=moving ? 'drop-shadow(0 0 4px #00aaff)' : 'drop-shadow(0 0 4px #ff2200)';}
    }
  }
  _boardConfig(){const sensor=SENSOR_DEVICES[this._selected];if(sensor)return sensor;const d=DEVICES[this._selected];const prefixes=d?.native.map(id=>id.split('.')[1].replace(/_(valve_position|fan)$/,'')) || [];const states=this._hass?.states || {};const power=Object.keys(states).find(id=>id.startsWith('button.') && prefixes.some(p=>id.startsWith('button.'+p+'_')) && id.endsWith('_power_off_board'));return {name:d?.name,maintenance:CONTROL_MAINTENANCE[this._selected],power,prefixes};}
  _updateBoardDetail(){const c=this._boardConfig(),states=this._hass?.states || {},helper='input_boolean.ventsys_maintenance_'+c.maintenance;this._text('#maintenance-status',states[helper]?.state==='on'?'Maintenance: expected offline. Reconnect power before reactivation.':'Active roster: board expected online.');this.$('#start-board-maintenance').disabled=!this._connected() || !['on','off'].includes(states[helper]?.state) || states[helper]?.state==='on';this.$('#end-board-maintenance').disabled=!this._connected() || states[helper]?.state!=='on';
    const d=DEVICES[this._selected];const ids=SENSOR_DEVICES[this._selected]?detailEntities(c,states):[...new Set([...(d?.native || []),d?.entity,...Object.keys(states).filter(id=>c.prefixes.some(p=>id.startsWith('sensor.'+p+'_') || id.startsWith('binary_sensor.'+p+'_')))].filter(id=>id && Object.hasOwn(states,id)))];
    const signature=JSON.stringify([this._selected,ids.map(id=>[id,states[id].state])]);if(signature!==this._detailSignature){this._detailSignature=signature;const list=this.$('#sensor-values');list.replaceChildren();for(const id of ids){const row=document.createElement('div'),dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=states[id].attributes?.friendly_name || id;dd.textContent=states[id].state+' '+(states[id].attributes?.unit_of_measurement || '');row.append(dt,dd);list.append(row);}}
    const alarmIds=ids.filter(id=>id.startsWith('binary_sensor.') && /_(co_detected|smoke_detected|high_temperature|sensor_fault)$/.test(id));const latched=ids.some(id=>/alarm_latched$/.test(id) && states[id].state==='on');this._text('#sensor-alarm-status',!c.ack?'':alarmIds.some(id=>states[id].state==='on')?'Active alarm or sensor fault':alarmIds.some(id=>!['on','off'].includes(states[id].state))?'Alarm state unavailable':latched?'Stored alarm latched; active conditions clear':'Alarm clear');
    const ack=this.$('#sensor-ack');ack.hidden=!c.ack;ack.disabled=!this._canSensorAck(c);for(const card of this._detailCards || [])card.hass=this._hass;const graphKey=this._selected+':'+ids.join(',');if(this._graphSelection!==graphKey){this._graphSelection=graphKey;this._buildDetailGraphs(ids);}}
  _canSensorAck(c){const states=this._hass?.states || {},button=states[c.ack];const ids=detailEntities(c,states);const safety=ids.filter(id=>id.startsWith('binary_sensor.') && /_(co_detected|smoke_detected|high_temperature|sensor_fault|co_sensor_fault|bme680_fault)$/.test(id));return this._connected() && button && button.state!=='unavailable' && safety.length>0 && safety.every(id=>states[id].state==='off');}
  async _sensorAck(){const c=this._boardConfig();if(!this._canSensorAck(c))return;try{await this._hass.callService('button','press',{entity_id:c.ack});this._event(c.name+': latch acknowledgment requested');this._text('#board-action-status','Acknowledgment sent; watch the latch report.');}catch(_){this._text('#board-action-status','Acknowledgment failed.');}}
  async _buildDetailGraphs(ids){const selection=this._selected;const box=this.$('#detail-graphs');box.replaceChildren();this._detailCards=[];if(!window.loadCardHelpers)return;try{const helpers=await window.loadCardHelpers();if(selection!==this._selected || !this.isConnected)return;const states=this._hass.states,groups=new Map();for(const id of ids){if(!/^(sensor|number|fan)\./.test(id) || /uptime|wifi|heap|loop/.test(id))continue;const unit=states[id].attributes?.unit_of_measurement || (id.startsWith('fan.')?'Fan state':id.startsWith('number.')?'Controller report':/rs_r0_ratio$/.test(id)?'Ratio':null);if(!unit)continue;if(!groups.has(unit))groups.set(unit,[]);groups.get(unit).push(id);}for(const [unit,entities] of groups){const card=helpers.createCardElement({type:'history-graph',title:'Recent history · '+unit,entities,hours_to_show:2,refresh_interval:60});card.hass=this._hass;box.append(card);this._detailCards.push(card);}}catch(_){box.textContent='Open Sensor trends for history.';}}
  _reviewMaintenance(){const c=this._boardConfig(),states=this._hass?.states || {};this._maintenanceDraft={selection:this._selected,...c};const available=c.power && states[c.power] && states[c.power].state!=='unavailable';this._text('#maintenance-title','Take '+c.name+' out of service');this._text('#maintenance-description',available?'Marks the board in maintenance, then sends its shutdown command. Sensing/control will stop. Reconnect power to bring it back; reactivation cannot wake it remotely.':'Marks this board in maintenance. No reachable firmware shutdown control exists; unplug it manually. Reconnect power before reactivation.');this.$('#maintenance-dialog').showModal();}
  async _applyMaintenance(){const c=this._maintenanceDraft;if(this._maintenancePending || !c || c.selection!==this._selected || !this._connected())return;this._maintenancePending=true;this.$('#maintenance-dialog').close();try{await this._hass.callService('input_boolean','turn_on',{entity_id:'input_boolean.ventsys_maintenance_'+c.maintenance});this._event(c.name+': maintenance started');const state=c.power && this._hass.states[c.power];if(state && state.state!=='unavailable'){await this._hass.callService('button','press',{entity_id:c.power});this._event(c.name+': shutdown requested');this._text('#board-action-status','Shutdown requested. Reconnect power before reactivation.');}else this._text('#board-action-status','Maintenance started. Unplug the board manually.');}catch(_){this._text('#board-action-status','Maintenance/shutdown failed or incomplete; inspect board and maintenance state.');}finally{this._maintenanceDraft=null;this._maintenancePending=false;}}
  async _reactivate(){const c=this._boardConfig();if(!this._connected())return;try{await this._hass.callService('input_boolean','turn_off',{entity_id:'input_boolean.ventsys_maintenance_'+c.maintenance});this._event(c.name+': active monitoring requested');this._text('#board-action-status','Expected online again. This does not restore power; confirm fresh readings.');}catch(_){this._text('#board-action-status','Reactivation failed.');}}
  _updateDevice(snapshot, connected) {
    this._updateBoardDetail();
    if(SENSOR_DEVICES[this._selected]){const config=SENSOR_DEVICES[this._selected];this._text('#device-name',config.name);this._text('#device-zone','SENSOR BOARD');this._text('#device-value','');this._text('#device-unit','');this._text('#device-source','Live measurements and recorded history');this._text('#device-range','Not an actuator');this._text('#device-age','See individual reports');this.$('#position-controls').hidden=true;this.$('#fan-controls').hidden=true;this._text('#device-help','Alarms are cleared only when the underlying condition is clear.');return;}
    const device = DEVICES[this._selected], state = snapshot[this._selected];
    this._text('#device-name', device.name); this._text('#device-zone', device.zone); this._text('#device-value', state.value === null ? '—' : display(device.fan ? state.value : openingPercent(device,state.value))); this._text('#device-unit', device.fan ? '' : '%');
    this._text('#device-source', !state.available ? 'Controller report unavailable' : state.native ? 'Native controller report' : 'MQTT report');
    this._text('#device-range', `${state.min}–${state.max}%`); this._text('#device-age', connected && state.timestamp ? new Date(state.timestamp).toLocaleTimeString() : 'Unavailable');
    this.$('#reference-controls').hidden = !device.expectedRange;
    this.$('#record-reference').disabled = Boolean(!device.expectedRange || this._blocked({kind:'reference',target:this._selected,opening:0,value:device.expectedRange?.min,revision:operatingState(this._hass?.states || {})?.revision}));
    this.$('#position-controls').hidden = Boolean(device.fan); this.$('#fan-controls').hidden = !device.fan;
    const maintained=this._hass?.states?.['input_boolean.ventsys_maintenance_'+CONTROL_MAINTENANCE[this._selected]]?.state==='on';const reason = this._backendBlock() || (maintained?'Board in maintenance; controls are disabled.':!state.available ? 'Controller unavailable; controls are disabled.' : !device.fan && !state.native ? 'Native controller not adopted; retained MQTT state cannot verify availability.' : this._pending || window[lockKey] ? 'A command is awaiting confirmation.' : '');
    for (const selector of ['#position-slider', '#position-number', '#fan-on', '#fan-off', '#speed-slider']) this.$(selector).disabled = Boolean(reason);
    this._text('#device-help', reason || ((!device.fan && (state.min > 0 || state.max < 100)) ? `Opening 0–100% maps to servo ${device.expectedRange?.min ?? state.min}–${device.expectedRange?.max ?? state.max}%. Targets are rounded to controller steps.` : 'Change a target to open its confirmation popup.'));
    for (const selector of ['#position-slider', '#position-number']) { this.$(selector).min = String(device.expectedRange ? 0 : state.min); this.$(selector).max = String(device.expectedRange ? 100 : state.max); }
    if (!this._editing) { const value = typeof state.value === 'number' ? openingPercent(device,state.value) : (device.expectedRange ? 0 : state.min); for (const selector of ['#position-slider', '#position-number']) this.$(selector).value = String(value); this._text('#requested', display(value) + '%'); this.$('#speed-slider').value = String(state.speed ?? 0); this._text('#speed-requested', (state.speed ?? 0) + '%'); }
  }
  _updateSchematic(snapshot) {
    const recorded=this._activityEntries(); const entries = recorded.length ? recorded : [{ time: this._started, message: 'Ready · no commands sent' }];
    for (let index = 0; index < 6; index++) {
      const entry = entries[index], node = this.$('#log-msg-' + (index + 1));
      this._text('#log-ts-' + (index + 1), entry ? new Date(entry.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }) : '');
      if (node) { node.textContent = entry?.message || ''; node.removeAttribute('textLength'); if(node.getComputedTextLength && node.getComputedTextLength()>510){node.setAttribute('textLength','510');node.setAttribute('lengthAdjust','spacingAndGlyphs');} node.setAttribute('aria-label', entry?.message || ''); }
    }
    for (const [key, textId, bladeId] of [['fan_main', 'fan-status-sub', 'fan-blades'], ['fan_booth', 'spray-fan-status-sub', 'spray-booth-fan-blades']]) {
      const state = snapshot[key]; const rpmLabel=this.$(key==='fan_main'?'#main-fan-rpm':'#booth-fan-rpm');if(rpmLabel)rpmLabel.setAttribute('fill',state.available?'#00ff88':'#91a2b8'); this._text(key==='fan_main'?'#main-fan-rpm':'#booth-fan-rpm',''); this._text('#'+DEVICES[key].text, !state.available || state.value==='off' ? '0' : '—'); const label=this.$('#'+textId); if(label){label.setAttribute('fill', state.available ? '#00ff88' : '#91a2b8');label.style.textShadow='none';} this._text('#' + textId, !state.available ? 'UNAVAILABLE' : state.value === 'on' ? 'ON · REPORTED' : 'OFF · REPORTED'); const blades = this.$('#' + bladeId); if (blades) blades.classList.toggle('running', state.value === 'on');
    }
    for (const device of DEVICE_LIST.filter(d => !d.fan)) {
      const state = snapshot[device.key], node = this.$(`[data-select="${device.key}"]`); if (!node) continue;
      const fraction = state.value === null ? .5 : device.expectedRange ? Math.max(0, Math.min(1, (state.value - state.min) / Math.max(1, state.max - state.min))) : state.value / 100;
      const color = !state.available ? '#91a2b8' : fraction <= 0 ? '#e00000' : fraction >= 1 ? '#00ff00' : '#ffb000'; node.style.color = color;
      const positionLabel = this.$('#' + device.text); if (positionLabel) positionLabel.setAttribute('fill', color);
      const suffix = device.svg.replace('valve-', ''), ellipse = this.$('#ellipse-' + suffix), circle = this.$('#circle-' + suffix);
      if (ellipse) { ellipse.setAttribute('fill', color); ellipse.setAttribute('opacity', '.9'); ellipse.style.filter = 'none'; ellipse.setAttribute('transform', `rotate(${state.value === null ? 45 : 90 - state.value * .9} ${ellipse.getAttribute('cx')} ${ellipse.getAttribute('cy')})`); }
      if (circle) { circle.setAttribute('stroke', color); circle.style.filter = 'none'; }
      if (device.key.endsWith('_360')) {
        const number = device.key.startsWith('fdm') ? 1 : 2, line = this.$('#intake' + number + '-line'), dot = this.$('#intake' + number + '-circle'), ring = this.$('#circle-360-enc' + number);
        const angle = (fraction * 90 - 90) * Math.PI / 180, x = Math.cos(angle) * 25, y = Math.sin(angle) * 25;
        if (line) { line.setAttribute('x2', x); line.setAttribute('y2', y); line.setAttribute('stroke', color); }
        if (dot) { dot.setAttribute('cx', x); dot.setAttribute('cy', y); dot.setAttribute('fill', color); }
        if (ring) { ring.setAttribute('stroke', color); ring.style.filter = 'none'; }
      }
    }
  }
}
if (!customElements.get('ventsys-dashboard-card')) customElements.define('ventsys-dashboard-card', VentSysDashboardCard);
window.customCards = window.customCards || [];
if (!window.customCards.some(card => card.type === 'ventsys-dashboard-card')) window.customCards.push({ type: 'ventsys-dashboard-card', name: 'VentSys Dashboard', description: 'Authenticated VentSys monitoring and reviewed controls', preview: false });

class VentSysDiagnosticsCard extends HTMLElement {
  setConfig(config) { this._config = config; }
  getCardSize() { return 8; }
  set hass(hass) { this._hass = hass; this.render(); }
  connectedCallback() { this.render(); }
  render() {
    if (!this._hass || !this.isConnected) return;
    if (!this.shadowRoot) {
      this.attachShadow({ mode: 'open' });
      this.shadowRoot.innerHTML = `<style>
        :host{display:block;color:#e5eef7;font:14px/1.4 system-ui,sans-serif;background:#091722;padding:20px;min-height:80vh}
        h1{font-size:26px;margin:0 0 4px}p{color:#a9bac9;margin:0 0 16px}
        input{box-sizing:border-box;width:100%;max-width:460px;padding:10px 12px;margin:0 0 18px;background:#132838;border:1px solid #527088;border-radius:8px;color:inherit;font:inherit}
        .summary{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 18px}.summary span{background:#173043;border-radius:8px;padding:7px 11px}
        .maintenance{margin:0 0 18px;padding:14px}.maintenance h2{margin:-14px -14px 10px}.maintenance p{margin:0 0 12px}
        .maintenance-list{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:8px}
        .maintenance-item{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:8px;border:1px solid #365268;border-radius:8px}
        .maintenance-item button{background:#254559;border:1px solid #64849a;border-radius:6px;color:#e5eef7;padding:6px 9px;cursor:pointer}
        .maintenance-item button[aria-pressed=true]{background:#25486d;border-color:#76c7ff;color:#aee0ff}
        .maintenance-item button:disabled{opacity:.5;cursor:not-allowed}
        .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,430px),1fr));gap:14px}
        section{background:#102535;border:1px solid #365268;border-radius:12px;overflow:hidden}h2{font-size:17px;margin:0;padding:12px 15px;background:#173245}
        table{border-collapse:collapse;width:100%;table-layout:fixed}td{border-top:1px solid #294152;padding:7px 10px;overflow-wrap:anywhere;vertical-align:top}td:first-child{width:52%;color:#b8cad7}td:last-child{text-align:right;font-variant-numeric:tabular-nums}
        small{display:block;color:#93a8b8}.bad{color:#ff977c}.warn{color:#ffc36d}.ok{color:#8be0c3}
      </style><h1>VentSys live diagnostics</h1><p>Home Assistant entity reports · telemetry is read only · values may be stale or unavailable</p><section class="maintenance"><h2>Expected online and maintenance</h2><p>Adopted boards are expected online by default. Maintenance pauses dropout push alerts for that board; offline state remains visible.</p><div class="maintenance-list"></div></section><input id="filter" type="search" aria-label="Filter VentSys entities" placeholder="Filter board, entity or reading"><div class="summary"></div><div class="grid"></div>`;
      this.shadowRoot.querySelector('#filter').addEventListener('input', () => this.render());
    }
    const query = this.shadowRoot.querySelector('#filter').value.trim().toLowerCase();
    const maintenanceList = this.shadowRoot.querySelector('.maintenance-list'); maintenanceList.replaceChildren();
    for (const board of BOARD_HEALTH) {
      const helperId = `input_boolean.ventsys_maintenance_${board.key}`, helper = this._hass.states[helperId];
      const item = document.createElement('div'), name = document.createElement('span'), button = document.createElement('button');
      const boardState = this._hass.states[board.uptime]?.state;
      const paused = helper?.state === 'on'; button.type = 'button'; button.textContent = paused ? 'End maintenance' : 'Start maintenance';
      item.className = 'maintenance-item'; name.textContent = `${board.label} · ${!boardState ? 'Unknown' : ['unavailable','unknown'].includes(boardState) ? 'Offline' : 'Online'}${paused ? ' · Maintenance' : ''}`;
      button.setAttribute('aria-label', `${board.label}: ${paused ? 'end maintenance' : 'start maintenance and pause dropout alerts'}`);
      button.setAttribute('aria-pressed', String(paused)); button.disabled = !helper || !['on','off'].includes(helper.state);
      button.addEventListener('click', () => this._hass.callService('input_boolean', paused ? 'turn_off' : 'turn_on', { entity_id: helperId }));
      item.append(name, button); maintenanceList.append(item);
    }
    const aliases = new Set(DEVICE_LIST.map(device => device.entity));
    const entities = Object.values(this._hass.states).filter(e => /(?:\.|_)ventsys_/.test(e.entity_id) || aliases.has(e.entity_id));
    const visible = entities.filter(e => !query || `${e.entity_id} ${e.attributes.friendly_name || ''} ${e.state}`.toLowerCase().includes(query));
    const groups = new Map();
    const boards = ['sla_pipe_air_sensor','fdm_airflow_sensor','booth_airflow_sensor','sla_airflow_sensor','main_duct_valve_1','main_duct_valve_2','e1_branch_valve','e2_branch_valve','fdm_print_valve','sla_print_valve','fdm_360_intake_valve','sla_360_intake_valve'];
    for (const entity of visible) {
      const raw = entity.entity_id.split('.')[1].replace(/^garage_/, '');
      const board = boards.find(name => raw.startsWith(`ventsys_${name}_`));
      const group = board ? board.replaceAll('_', ' ') : 'System and legacy entities';
      if (!groups.has(group)) groups.set(group, []);
      groups.get(group).push(entity);
    }
    const summary = this.shadowRoot.querySelector('.summary'); summary.replaceChildren();
    for (const value of [`${entities.length} entities`, `${visible.length} shown`, `${entities.filter(e => e.state==='unavailable' || e.state==='unknown' && !['button','script'].includes(e.entity_id.split('.')[0])).length} unavailable/unknown`]) { const chip=document.createElement('span'); chip.textContent=value; summary.append(chip); }
    const grid = this.shadowRoot.querySelector('.grid'); grid.replaceChildren();
    for (const [name, items] of [...groups].sort(([a],[b]) => a.localeCompare(b))) {
      const section=document.createElement('section'), heading=document.createElement('h2'), table=document.createElement('table');
      heading.textContent=name.replace(/\b\w/g,c=>c.toUpperCase()); section.append(heading,table);
      for (const entity of items.sort((a,b) => a.entity_id.localeCompare(b.entity_id))) {
        const row=document.createElement('tr'), label=document.createElement('td'), value=document.createElement('td'), id=document.createElement('small');
        label.textContent=entity.attributes.friendly_name || entity.entity_id; id.textContent=entity.entity_id; label.append(id);
        const unit=entity.attributes.unit_of_measurement || '';
        const numeric=Number(entity.state), reading=entity.state!=='' && Number.isFinite(numeric) ? String(Math.round(numeric*1000)/1000) : entity.state;
        value.textContent=`${reading}${unit ? ' '+unit : ''}`;
        const age=Math.max(0,Math.round((Date.now()-Date.parse(entity.last_updated))/1000));
        const stamp=document.createElement('small'); stamp.textContent=Number.isFinite(age) ? `updated ${age<60 ? age+'s' : Math.round(age/60)+'m'} ago` : 'update time unknown'; value.append(stamp);
        value.className=entity.state==='unavailable' || entity.state==='unknown' && !['button','script'].includes(entity.entity_id.split('.')[0])?'bad':entity.state==='on' && /fault|alarm|failsafe|detected/.test(entity.entity_id)?'warn':'';
        row.append(label,value); table.append(row);
      }
      grid.append(section);
    }
  }
}
if (!customElements.get('ventsys-diagnostics-card')) customElements.define('ventsys-diagnostics-card', VentSysDiagnosticsCard);
if (!window.customCards.some(card => card.type === 'ventsys-diagnostics-card')) window.customCards.push({ type: 'ventsys-diagnostics-card', name: 'VentSys Diagnostics', description: 'Read-only live VentSys entity inventory', preview: false });
