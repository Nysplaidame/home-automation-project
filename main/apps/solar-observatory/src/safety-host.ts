import type { DisplayMessage, DisplayState } from "./safety.ts";

export const DISPLAY_ENTITIES = Object.freeze({ failsafe: "input_boolean.ventsys_failsafe", fan: "fan.inline_fan" });
export interface HaDisplayContext {
  connection?: {
    connected: boolean;
    addEventListener?: (type: "disconnected" | "ready", callback: () => void) => void;
    removeEventListener?: (type: "disconnected" | "ready", callback: () => void) => void;
  };
  states?: Record<string, { state?: unknown } | undefined>;
}

function switchState(value: unknown): "on" | "off" | "unknown" {
  return value === "on" || value === "off" ? value : "unknown";
}

export function mapDisplayState(context: HaDisplayContext): DisplayState {
  return {
    failsafe: switchState(context.states?.[DISPLAY_ENTITIES.failsafe]?.state),
    fan: switchState(context.states?.[DISPLAY_ENTITIES.fan]?.state),
    // Transport connectivity is not proof that physical monitoring is commissioned.
    monitoring: "unverified",
  };
}

export class SnapshotPublisher {
  private sequence = 0;
  readonly sessionId: string;

  constructor(sessionId = crypto.randomUUID()) {
    if (!/^[a-zA-Z0-9-]{16,128}$/.test(sessionId)) throw new Error("Invalid session");
    this.sessionId = sessionId;
  }

  next(context: HaDisplayContext | null, issuedAtMs = Date.now()): DisplayMessage {
    if (!Number.isSafeInteger(issuedAtMs)) throw new Error("Invalid host clock");
    const connected = context?.connection?.connected === true;
    const envelope = {
      version: 1 as const, sessionId: this.sessionId, sequence: this.sequence++,
      issuedAtMs, expiresAtMs: issuedAtMs + 15000,
    };
    return connected ? { ...envelope, type: "state_snapshot", state: mapDisplayState(context!) } : { ...envelope, type: "offline" };
  }
}
