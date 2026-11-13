export interface DisplayState {
  failsafe: "on" | "off" | "unknown";
  fan: "on" | "off" | "unknown";
  monitoring: "available" | "unavailable" | "unverified";
}
export interface DisplayMessage {
  version: 1;
  type: "state_snapshot" | "offline";
  sessionId: string;
  sequence: number;
  issuedAtMs: number;
  expiresAtMs: number;
  state?: DisplayState;
}
export interface SafetyView {
  connected: boolean;
  critical: boolean;
  label: string;
  state: DisplayState | null;
}
const MAX_LIFETIME_MS = 15000;
const keysAre = (value: Record<string, unknown>, keys: string[]) =>
  Object.keys(value).length === keys.length && keys.every(key => Object.hasOwn(value, key));
const record = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

function validMessage(value: unknown, sessionId: string, wallMs: number): value is DisplayMessage {
  if (!record(value)) return false;
  const keys = ["version", "type", "sessionId", "sequence", "issuedAtMs", "expiresAtMs"];
  if (value.type === "state_snapshot") keys.push("state");
  if (!keysAre(value, keys) || value.version !== 1 ||
      !["state_snapshot", "offline"].includes(String(value.type)) || value.sessionId !== sessionId ||
      !Number.isSafeInteger(value.sequence) || Number(value.sequence) < 0 ||
      !Number.isSafeInteger(value.issuedAtMs) || !Number.isSafeInteger(value.expiresAtMs)) return false;
  const issued = Number(value.issuedAtMs);
  const expires = Number(value.expiresAtMs);
  if (issued > wallMs || expires <= wallMs || expires <= issued || expires - issued > MAX_LIFETIME_MS) return false;
  if (value.type === "offline") return true;
  const state = value.state;
  return record(state) && keysAre(state, ["failsafe", "fan", "monitoring"]) &&
    typeof state.failsafe === "string" && ["on", "off", "unknown"].includes(state.failsafe) &&
    typeof state.fan === "string" && ["on", "off", "unknown"].includes(state.fan) &&
    typeof state.monitoring === "string" && ["available", "unavailable", "unverified"].includes(state.monitoring);
}

// Protocol validation, not an isolation boundary against malicious same-origin scripts.
export class SafetyReceiver {
  private state: DisplayState | null = null;
  private sequence = -1;
  private expiresWall = 0;
  private expiresMono = 0;
  private origin: string;
  private source: object;
  private sessionId: string;

  constructor(origin: string, source: object, sessionId: string) {
    if (new URL(origin).origin !== origin || !/^[a-zA-Z0-9-]{16,128}$/.test(sessionId)) {
      throw new Error("Explicit origin and unpredictable per-load session required");
    }
    this.origin = origin;
    this.source = source;
    this.sessionId = sessionId;
  }

  disconnect(): void {
    this.state = null;
    this.expiresWall = 0;
    this.expiresMono = 0;
  }

  receive(event: { origin: string; source: object | null; data: unknown }, wallMs: number, monoMs: number): boolean {
    if (event.origin !== this.origin || event.source !== this.source) return false;
    if (!Number.isFinite(wallMs) || !Number.isFinite(monoMs) ||
        !validMessage(event.data, this.sessionId, wallMs) || event.data.sequence <= this.sequence) {
      this.disconnect();
      return false;
    }
    const message = event.data;
    this.sequence = message.sequence;
    this.expiresWall = message.expiresAtMs;
    this.expiresMono = monoMs + message.expiresAtMs - wallMs;
    this.state = message.type === "state_snapshot" ? { ...message.state! } : null;
    return true;
  }

  view(wallMs: number, monoMs: number): SafetyView {
    if (!Number.isFinite(wallMs) || !Number.isFinite(monoMs) || wallMs >= this.expiresWall || monoMs >= this.expiresMono) {
      this.disconnect();
    }
    if (!this.state) return { connected: false, critical: false, label: "Live status unavailable", state: null };
    const state = { ...this.state };
    const critical = state.failsafe === "on";
    const label = critical ? "Failsafe active" : state.failsafe === "unknown" || state.monitoring !== "available" ?
      "Monitoring incomplete" : "HA connected - safety not certified";
    return { connected: true, critical, label, state };
  }
}
