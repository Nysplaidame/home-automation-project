import "./observatory-card.ts";
import type { ObservatoryReadonlyCard } from "./observatory-card.ts";
import type { HaDisplayContext } from "./safety-host.ts";

const card = document.getElementById("card") as ObservatoryReadonlyCard;
const status = document.getElementById("mock-status")!;
const listeners = new Map<string, Set<() => void>>();
let failsafe = "off";
let blocked = false;
let commandCalls = 0;
const connection = {
  connected: false,
  addEventListener: (name: string, callback: () => void) => {
    if (!listeners.has(name)) listeners.set(name, new Set());
    listeners.get(name)!.add(callback);
  },
  removeEventListener: (name: string, callback: () => void) => { listeners.get(name)?.delete(callback); },
};
const context = (): HaDisplayContext => ({
  connection,
  states: {
    "input_boolean.ventsys_failsafe": { state: failsafe },
    "fan.inline_fan": { state: "on" },
    "sensor.unrelated": { state: "private-test-value" },
  },
});
function supply(): void {
  // The extra spy exists only in this mock host to prove the card never invokes it.
  card.hass = { ...context(), callService: () => { commandCalls++; } } as HaDisplayContext;
}
card.setConfig({ observatory_url: new URL("./index.html?reference=1&simulation=1", location.href).href });
supply();
const frame = () => card.shadowRoot!.querySelector("iframe")!;
let restoreDelivery: (() => void) | null = null;
document.getElementById("connect")!.addEventListener("click", () => {
  connection.connected = true;
  listeners.get("ready")?.forEach(listener => listener());
  supply();
  status.textContent = "Mock connected; physical monitoring remains unverified.";
});
document.getElementById("alert")!.addEventListener("click", () => { failsafe = "on"; supply(); status.textContent = "Simulated failsafe is ON."; });
document.getElementById("clear")!.addEventListener("click", () => { failsafe = "off"; supply(); status.textContent = "Simulated failsafe is OFF; acknowledge in the display."; });
document.getElementById("disconnect")!.addEventListener("click", () => {
  connection.connected = false;
  listeners.get("disconnected")?.forEach(listener => listener());
  supply();
  status.textContent = "Mock disconnected; display must clear trusted state.";
});
document.getElementById("silence")!.addEventListener("click", event => {
  blocked = !blocked;
  if (blocked) {
    // Drop messages before dispatch. A listener added after the receiver is not
    // a reliable way to simulate transport loss for Window message events.
    const destination = frame().contentWindow!;
    const original = destination.postMessage;
    destination.postMessage = () => {};
    restoreDelivery = () => { destination.postMessage = original; };
  } else { restoreDelivery?.(); restoreDelivery = null; supply(); }
  (event.target as HTMLButtonElement).textContent = blocked ? "Resume delivery" : "Pause delivery";
  status.textContent = blocked ? "Messages suppressed in the simulation. Trusted state must expire within 15 seconds." : "Message delivery restored.";
});
document.getElementById("reload")!.addEventListener("click", () => {
  restoreDelivery?.();
  restoreDelivery = null;
  blocked = false;
  document.getElementById("silence")!.textContent = "Pause delivery";
  frame().contentWindow!.location.reload();
});
Object.assign(window, { mockHostDiagnostics: () => ({ commandCalls, connected: connection.connected, failsafe, blocked }) });
