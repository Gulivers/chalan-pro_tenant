/**
 * Pick the operational work order from a list.
 * Prefer explicit deep-link id, then In Progress, then Scheduled/Pending (recent),
 * then any non-terminal non-absence, else the newest by date.
 *
 * @param {Array<object>} events
 * @param {number|string|null} preferredId
 * @returns {object|null}
 */
export function pickPreferredWorkOrder(events, preferredId = null) {
  if (!Array.isArray(events) || !events.length) return null;

  if (preferredId != null && preferredId !== "") {
    const want = Number(preferredId);
    if (Number.isFinite(want)) {
      const match = events.find((event) => Number(event.id) === want);
      if (match) return match;
    }
  }

  const scored = events.map((event) => {
    const code = String(event?.work_order_status_code || "").toLowerCase();
    const terminal = !!event?.work_order_status_is_terminal;
    const absence = !!event?.is_absence;
    const dateMs = event?.date ? new Date(event.date).getTime() : 0;

    let score = 0;
    if (!absence && !terminal && code === "in_progress") {
      score = 400;
    } else if (
      !absence &&
      !terminal &&
      (code.includes("schedul") || code.includes("pending"))
    ) {
      score = 300;
    } else if (!absence && !terminal) {
      score = 200;
    } else if (!absence) {
      score = 100;
    } else {
      score = 10;
    }

    return { event, score, dateMs };
  });

  scored.sort((a, b) => b.score - a.score || b.dateMs - a.dateMs);
  return scored[0]?.event ?? null;
}

/**
 * Resolve deep-link order id from route query (`order` preferred, `event` legacy).
 */
export function resolveOrderQueryId(query = {}) {
  const raw = query?.order ?? query?.event;
  const parsed = Number(raw);
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null;
}
