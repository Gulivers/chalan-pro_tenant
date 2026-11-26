/**
 * Lightweight Work Order Viewer telemetry (Oleada 4).
 * Emits to window.dataLayer when present; no-ops otherwise.
 *
 * @param {string} action
 * @param {Record<string, unknown>} [payload]
 */
export function trackWov(action, payload = {}) {
  if (typeof window === "undefined") return;
  const event = {
    event: "wov",
    wov_action: action,
    ...payload,
    ts: Date.now(),
  };
  try {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(event);
  } catch {
    /* ignore */
  }
  if (import.meta.env?.DEV) {
    // eslint-disable-next-line no-console
    console.debug("[wov]", action, payload);
  }
}
