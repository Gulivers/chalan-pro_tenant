/**
 * Resolve safe vue-router locations from Assistant entity_link blocks.
 * Authority: route_key + entity_id only (canonical locations).
 * Never trust arbitrary path strings from the payload.
 */

const ALLOWED_ROUTE_KEYS = new Set(['transactions-form', 'builder-view']);

/**
 * @param {object} block
 * @returns {import('vue-router').RouteLocationRaw|null}
 */
export function resolveEntityLinkLocation(block) {
  if (!block || typeof block !== 'object') return null;

  const routeKey = block.route_key;
  const entityId = block.entity_id;

  if (!ALLOWED_ROUTE_KEYS.has(routeKey)) return null;
  if (!isPositiveInt(entityId)) return null;

  // Ignore block.path for navigation. Backend may send a canonical path for
  // display/debug; the client always builds the known route from id.
  if (routeKey === 'transactions-form') {
    // Level-1 Assistant is read-only: open documents in view mode (same as list "View").
    return {
      name: 'transactions-form',
      query: { id: String(entityId), mode: 'view' },
    };
  }

  if (routeKey === 'builder-view') {
    return { name: 'builder-view', params: { id: String(entityId) } };
  }

  return null;
}

function isPositiveInt(value) {
  return typeof value === 'number' && Number.isInteger(value) && value >= 1;
}
