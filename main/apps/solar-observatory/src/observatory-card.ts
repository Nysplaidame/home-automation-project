import { SnapshotPublisher, type HaDisplayContext } from "./safety-host.ts";

interface CardConfig { observatory_url?: string }

// Candidate HA custom card: no child-message listener and no service-call capability.
export class ObservatoryReadonlyCard extends HTMLElement {
  private context: HaDisplayContext | null = null;
  private frame: HTMLIFrameElement | null = null;
  private publisher: SnapshotPublisher | null = null;
  private timer: number | undefined;
  private url: URL | null = null;
  private receivedAfterDisconnect = false;
  private onDisconnected = () => {
    this.receivedAfterDisconnect = false;
    this.send(true);
  };
  private onReady = () => {
    // Wait for HA to provide state again; don't re-certify cached data on socket open.
    this.receivedAfterDisconnect = false;
    this.send(true);
  };

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  setConfig(config: CardConfig): void {
    const url = new URL(config.observatory_url || "/local/solar-observatory/index.html", location.href);
    if (url.origin !== location.origin || url.username || url.password || !["http:", "https:"].includes(url.protocol)) {
      throw new Error("Observatory URL must use the exact HA origin and contain no credentials");
    }
    // Only our index document can be embedded. Custom paths still require deployment review.
    if (!url.pathname.endsWith("/index.html") && url.pathname !== "/") throw new Error("Expected observatory index document");
    if ([...url.searchParams].some(([key, value]) => !["reference", "simulation"].includes(key) || value !== "1") || url.hash) {
      throw new Error("Only reference/simulation flags are permitted in the frame URL");
    }
    url.searchParams.set("bridge", "read-only-v1");
    this.url = url;
    if (this.isConnected) this.render();
  }

  set hass(context: HaDisplayContext) {
    const previous = this.context?.connection;
    if (previous !== context.connection) {
      this.detachConnection();
      context.connection?.addEventListener?.("disconnected", this.onDisconnected);
      context.connection?.addEventListener?.("ready", this.onReady);
    }
    this.context = context;
    this.receivedAfterDisconnect = context.connection?.connected === true;
    this.send();
  }

  connectedCallback(): void {
    if (this.url) this.render();
  }

  disconnectedCallback(): void {
    this.send(true);
    if (this.timer !== undefined) window.clearInterval(this.timer);
    this.timer = undefined;
    this.detachConnection();
    this.publisher = null;
    this.receivedAfterDisconnect = false;
    this.context = null;
  }

  private detachConnection(): void {
    this.context?.connection?.removeEventListener?.("disconnected", this.onDisconnected);
    this.context?.connection?.removeEventListener?.("ready", this.onReady);
  }

  private render(): void {
    if (!this.url) return;
    this.send(true);
    if (this.timer !== undefined) window.clearInterval(this.timer);
    this.publisher = null;
    const style = document.createElement("style");
    style.textContent = ":host{display:block;height:100%;min-height:480px}iframe{display:block;width:100%;height:100%;min-height:480px;border:0;background:#080e15}";
    const frame = document.createElement("iframe");
    frame.title = "Read-only VentSys observatory";
    frame.referrerPolicy = "same-origin";
    frame.addEventListener("load", () => {
      if (this.frame !== frame || !this.isConnected || frame.contentWindow?.location.href !== this.url?.href) return;
      this.publisher = new SnapshotPublisher();
      // Per-document bootstrap, outside the two-message wire protocol. A queued
      // envelope from the previous document cannot select the new session.
      frame.contentDocument!.documentElement.dataset.observatorySession = this.publisher.sessionId;
      this.send();
    });
    frame.src = this.url.href;
    this.frame = frame;
    this.shadowRoot!.replaceChildren(style, frame);
    this.timer = window.setInterval(() => this.send(), 5000);
  }

  private send(forceOffline = false): void {
    if (!this.publisher || !this.frame?.contentWindow || !this.url) return;
    const context = !forceOffline && this.receivedAfterDisconnect ? this.context : null;
    this.frame.contentWindow.postMessage(this.publisher.next(context), this.url.origin);
  }

  getCardSize(): number { return 10; }
}

if (!customElements.get("observatory-readonly-card")) customElements.define("observatory-readonly-card", ObservatoryReadonlyCard);
