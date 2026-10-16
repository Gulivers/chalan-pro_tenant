/**
 * Shared helpers for DocumentType status tracking (not Material Request).
 */

export function documentStatusSeverity(code, { isTerminal = false } = {}) {
  const key = String(code || '').toLowerCase();
  if (isTerminal || key === 'closed') return 'secondary';
  if (
    key === 'approved' ||
    key === 'ordered' ||
    key === 'delivered' ||
    key === 'picked' ||
    key === 'submitted'
  ) {
    return 'success';
  }
  if (key === 'preparing' || key === 'draft') return 'warning';
  return 'info';
}

export function formatStatusWhen(value) {
  if (!value) return '';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return date.toLocaleString();
}

export function readApiError(err, fallback = 'Something went wrong.') {
  const data = err?.response?.data;
  if (!data) return fallback;
  if (typeof data === 'string') return data;
  const detail =
    data.status ||
    data.detail ||
    data.non_field_errors ||
    data.error;
  if (Array.isArray(detail)) return detail.join(' ');
  if (typeof detail === 'string') return detail;
  if (detail && typeof detail === 'object') {
    return Object.values(detail).flat().join(' ') || fallback;
  }
  const fieldMsgs = Object.entries(data)
    .filter(([key]) => !['status', 'detail', 'non_field_errors', 'error'].includes(key))
    .map(([key, msgs]) => {
      const text = Array.isArray(msgs) ? msgs.join(' ') : String(msgs);
      return `${key}: ${text}`;
    })
    .filter(Boolean);
  if (fieldMsgs.length) return fieldMsgs.join(' ');
  return fallback;
}
