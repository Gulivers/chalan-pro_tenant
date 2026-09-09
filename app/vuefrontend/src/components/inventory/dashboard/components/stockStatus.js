/**
 * Client-side stock status for dashboard triage.
 * Uses existing list fields only (current_stock / total_stock / reorder_level).
 */

export function getStockQty(product) {
  const n = Number(product?.current_stock ?? product?.total_stock ?? 0);
  return Number.isFinite(n) ? n : 0;
}

export function getReorderLevel(product) {
  const n = Number(product?.reorder_level ?? 0);
  return Number.isFinite(n) ? n : 0;
}

/** @returns {'critical'|'out'|'low'|'healthy'} */
export function getStockStatus(product) {
  const stock = getStockQty(product);
  const reorder = getReorderLevel(product);
  if (stock < 0) return 'critical';
  if (stock === 0) return 'out';
  if (stock < reorder) return 'low';
  return 'healthy';
}

export function stockStatusLabel(status) {
  switch (status) {
    case 'critical':
      return 'Critical';
    case 'out':
      return 'Out of Stock';
    case 'low':
      return 'Low Stock';
    default:
      return 'Healthy';
  }
}

/** JRBadge severity */
export function stockStatusSeverity(status) {
  switch (status) {
    case 'critical':
    case 'out':
      return 'danger';
    case 'low':
      return 'warn';
    default:
      return 'success';
  }
}

export function summarizeStockAttention(products) {
  const list = Array.isArray(products) ? products : [];
  const counts = { critical: 0, out: 0, low: 0, healthy: 0 };
  for (const product of list) {
    counts[getStockStatus(product)] += 1;
  }
  return counts;
}
