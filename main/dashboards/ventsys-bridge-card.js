// Local read-only candidate. The direct VentSys dashboard remains the control UI.
export class VentSysBridgeCard extends HTMLElement {
  constructor() { super(); this.attachShadow({mode:'open'}); this.sequence = 0; }
  setConfig(config) { if (Object.keys(config).some(k => k !== 'type')) throw new Error('No bridge configuration overrides'); }
  connectedCallback() {
    this.shadowRoot.innerHTML = '<iframe title="VentSys read-only status"></iframe>';
    this.frame = this.shadowRoot.querySelector('iframe');
    this.frame.addEventListener('load', () => this.startSession());
    this.frame.src = new URL('./ventsys-bridge-page.html', import.meta.url).href;
    this.timer = setInterval(() => this.send(), 5000);
  }
  disconnectedCallback() { this.sendOffline(); clearInterval(this.timer); this.session = null; this._hass = null; }
  set hass(value) { this._hass = value; this.send(); }
  startSession() {
    this.session = null; this.sequence = 0;
    try {
      const bytes = crypto.getRandomValues(new Uint8Array(16));
      this.session = Array.from(bytes, b => b.toString(16).padStart(2, '0')).join('');
      this.frame.contentDocument.documentElement.dataset.ventsysSession = this.session;
      this.send();
    } catch { this.session = null; }
  }
  envelope(type, payload) {
    const issuedAtMs = Date.now();
    return {version:1, type, sessionId:this.session, sequence:++this.sequence, issuedAtMs, expiresAtMs:issuedAtMs + 15000, ...(payload ? {payload} : {})};
  }
  sendOffline() { if (this.session && this.frame?.contentWindow) this.frame.contentWindow.postMessage(this.envelope('offline'), location.origin); }
  send() {
    if (!this.session || !this.isConnected) return;
    if (this._hass?.connection?.connected !== true) { this.sendOffline(); return; }
    const state = this._hass.states?.['input_boolean.ventsys_failsafe']?.state;
    const failsafe = state === 'on' ? 'on' : state === 'off' ? 'off' : 'unknown';
    this.frame.contentWindow.postMessage(this.envelope('state_snapshot', {failsafe}), location.origin);
  }
}
customElements.define('ventsys-bridge-card', VentSysBridgeCard);
