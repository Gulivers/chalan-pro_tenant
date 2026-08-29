/**
 * Format Assistant block values for display.
 * Backend already sends decimal strings; currency uses en-US / USD by default.
 */
export function formatAssistantValue(value, format = 'text', currency = 'USD') {
  if (value == null || value === '') return '—';

  if (format === 'currency') {
    const num = Number(value);
    if (Number.isFinite(num)) {
      try {
        return num.toLocaleString('en-US', {
          style: 'currency',
          currency: currency || 'USD',
        });
      } catch {
        return num.toLocaleString('en-US', {
          style: 'currency',
          currency: 'USD',
        });
      }
    }
    return String(value);
  }

  if (format === 'number') {
    const num = Number(value);
    if (Number.isFinite(num)) {
      return num.toLocaleString('en-US');
    }
  }

  return String(value);
}

/** Parse chart decimal strings safely for Chart.js. */
export function parseChartNumber(value) {
  const num = Number(value);
  return Number.isFinite(num) ? num : 0;
}
