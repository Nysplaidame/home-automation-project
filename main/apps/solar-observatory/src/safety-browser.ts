import { SafetyReceiver, type SafetyView } from "./safety.ts";

const offline = (): SafetyView => ({ connected: false, critical: false, label: "Live status unavailable", state: null });

export function connectSafetyDisplay(update: (view: SafetyView) => void): () => void {
  const enabled = window.parent !== window && new URLSearchParams(location.search).get("bridge") === "read-only-v1";
  let receiver: SafetyReceiver | null = null;
  const publish = () => update(receiver?.view(Date.now(), performance.now()) ?? offline());
  publish();
  if (!enabled) return () => {};

  const receive = (event: MessageEvent<unknown>) => {
    if (event.origin !== location.origin || event.source !== window.parent) return;
    if (!receiver) {
      // Bind once against the per-document UUID installed by the exact parent
      // on load. Old queued messages cannot bootstrap a reloaded document.
      if (!event.data || typeof event.data !== "object" || !("sessionId" in event.data) || typeof event.data.sessionId !== "string") return;
      if (event.data.sessionId !== document.documentElement.dataset.observatorySession) return;
      try {
        const candidate = new SafetyReceiver(location.origin, window.parent, event.data.sessionId);
        if (candidate.receive({ origin: event.origin, source: event.source, data: event.data }, Date.now(), performance.now())) receiver = candidate;
      } catch { /* Remain offline until a valid bootstrap arrives. */ }
    } else {
      receiver.receive({ origin: event.origin, source: event.source, data: event.data }, Date.now(), performance.now());
    }
    publish();
  };
  window.addEventListener("message", receive);
  document.addEventListener("visibilitychange", publish);
  const timer = window.setInterval(publish, 250);
  return () => {
    window.clearInterval(timer);
    window.removeEventListener("message", receive);
    document.removeEventListener("visibilitychange", publish);
    receiver?.disconnect();
    update(offline());
  };
}
