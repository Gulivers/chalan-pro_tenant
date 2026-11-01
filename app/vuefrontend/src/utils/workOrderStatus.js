/**
 * Helpers for Work Order (Event) status & progress.
 * Work Orders use flexible transitions between active statuses — unlike
 * Document Status, there is no next/previous (sequence ±1) rule here.
 */
import { readApiError } from './documentStatus';

export { formatStatusWhen, readApiError } from './documentStatus';

/**
 * Light-badge severity for a Work Order status. Keyed mainly by the
 * operational flags so tenant-renamed statuses still read sensibly;
 * a couple of well-known codes refine the tone.
 */
export function workOrderStatusSeverity(status) {
  if (!status) return 'secondary';
  const code =
    typeof status === 'string'
      ? status.toLowerCase()
      : String(status.status_code || status.code || '').toLowerCase();
  const isTerminal =
    typeof status === 'object' && Boolean(status.is_terminal);
  if (isTerminal || code === 'passed_closed') return 'success';
  if (code === 'corrections_required') return 'warning';
  if (code === 'pending_inspection') return 'info';
  if (code === 'in_progress') return 'info';
  if (code === 'pending_prereqs') return 'warning';
  return 'secondary';
}

export function workAccountStateLabel(state) {
  const key = String(state || '').toLowerCase();
  if (key === 'completed') return 'Completed';
  if (key === 'in_progress') return 'In progress';
  return 'Not started';
}

export function workAccountStateSeverity(state) {
  const key = String(state || '').toLowerCase();
  if (key === 'completed') return 'success';
  if (key === 'in_progress') return 'info';
  return 'secondary';
}

/** Progress requirements the API reported as blocking a transition. */
export function missingRequirementsFromError(err) {
  const data = err?.response?.data;
  const list = data?.missing_requirements;
  if (!Array.isArray(list)) return [];
  return list
    .map((item) =>
      typeof item === 'string'
        ? { code: item, name: item }
        : { id: item?.id ?? null, code: item?.code || '', name: item?.name || item?.code || '' },
    )
    .filter((item) => item.name);
}

export function readWorkOrderError(err, fallback = 'Something went wrong.') {
  return readApiError(err, fallback);
}
