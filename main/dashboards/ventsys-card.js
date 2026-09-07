class VentSysDashboardCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._entityIds = [];
    this._lastSnapshot = "";
    this._onMessage = this._onMessage.bind(this);
  }

  setConfig(config) {
    const dashboardUrl = new URL(
      config.dashboard_url || "/local/ventsys-dashboard.html",
      window.location.href,
    );
    if (dashboardUrl.origin !== window.location.origin) {
      throw new Error("VentSys dashboard_url must use the Home Assistant origin");
    }
    dashboardUrl.searchParams.set("ha_bridge", "1");
    this._config = { ...config, dashboard_url: dashboardUrl.toString() };
    this._render();
  }

  set hass(value) {
    this._hass = value;
    this._sendSnapshot();
  }

  connectedCallback() {
    window.addEventListener("message", this._onMessage);
    if (!this.shadowRoot.firstChild) this._render();
  }

  disconnectedCallback() {
    window.removeEventListener("message", this._onMessage);
  }

  getCardSize() {
    return 10;
  }

  _render() {
    const src = this._config.dashboard_url || "/local/ventsys-dashboard.html?ha_bridge=1";
    this.shadowRoot.innerHTML = `
      <style>
        :host { display: block; }
        ha-card { overflow: hidden; background: #000; }
        iframe {
          display: block;
          width: 100%;
          aspect-ratio: 1024 / 600;
          border: 0;
          background: #000;
        }
      </style>
      <ha-card>
        <iframe title="VentSys dashboard" src="${this._escapeAttribute(src)}"></iframe>
      </ha-card>
    `;
    this._lastSnapshot = "";
  }

  _onMessage(event) {
    const frame = this.shadowRoot.querySelector("iframe");
    if (
      event.origin !== window.location.origin ||
      !frame ||
      event.source !== frame.contentWindow ||
      event.data?.channel !== "ventsys-ha-bridge"
    ) {
      return;
    }

    if (event.data.type === "ready") {
      this._entityIds = Array.from(new Set(event.data.entity_ids || []))
        .filter((entityId) => /^[a-z_]+\.[a-z0-9_]+$/.test(String(entityId)))
        .slice(0, 100);
      this._lastSnapshot = "";
      this._sendSnapshot();
      return;
    }

    if (event.data.type === "service-call") {
      this._handleServiceCall(event.data);
    }
  }

  _sendSnapshot() {
    const frame = this.shadowRoot.querySelector("iframe");
    if (!frame?.contentWindow || !this._hass || this._entityIds.length === 0) return;
    const states = this._entityIds
      .map((entityId) => this._hass.states?.[entityId])
      .filter(Boolean);
    const signature = JSON.stringify(states.map((state) => [
      state.entity_id,
      state.state,
      state.last_updated,
      state.attributes,
    ]));
    if (signature === this._lastSnapshot) return;
    this._lastSnapshot = signature;
    frame.contentWindow.postMessage(
      {
        channel: "ventsys-ha-bridge",
        type: "state-snapshot",
        connected: true,
        states,
      },
      window.location.origin,
    );
  }

  async _handleServiceCall(message) {
    const requestId = Number(message.request_id);
    try {
      if (!this._hass || !Number.isSafeInteger(requestId)) {
        throw new Error("Home Assistant context is unavailable");
      }
      if (message.kind === "mqtt-publish") {
        const topic = String(message.topic || "");
        const payload = String(message.payload ?? "");
        if (!/^ventsys\/[a-z0-9/_-]+$/.test(topic) || payload.length > 256) {
          throw new Error("MQTT request is outside the VentSys allowlist");
        }
        await this._hass.callService("mqtt", "publish", {
          topic,
          payload,
          retain: message.retain === true,
        });
      } else if (message.kind === "script-turn-on") {
        const entityId = String(message.entity_id || "");
        if (!/^script\.ventsys_[a-z0-9_]+$/.test(entityId)) {
          throw new Error("Script request is outside the VentSys allowlist");
        }
        await this._hass.callService("script", "turn_on", { entity_id: entityId });
      } else {
        throw new Error("Unsupported VentSys service request");
      }
      this._reply(requestId, true);
    } catch (error) {
      this._reply(requestId, false, error instanceof Error ? error.message : "Service call failed");
    }
  }

  _reply(requestId, success, error = null) {
    const frame = this.shadowRoot.querySelector("iframe");
    frame?.contentWindow?.postMessage(
      {
        channel: "ventsys-ha-bridge",
        type: "service-result",
        request_id: requestId,
        success,
        error,
      },
      window.location.origin,
    );
  }

  _escapeAttribute(value) {
    return String(value)
      .replaceAll("&", "&amp;")
      .replaceAll('"', "&quot;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;");
  }
}

if (!customElements.get("ventsys-dashboard-card")) {
  customElements.define("ventsys-dashboard-card", VentSysDashboardCard);
}

window.customCards = window.customCards || [];
window.customCards.push({
  type: "ventsys-dashboard-card",
  name: "VentSys Dashboard",
  description: "Authenticated VentSys control and monitoring dashboard",
  preview: false,
});
