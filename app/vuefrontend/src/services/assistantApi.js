import axios from 'axios';

const QUERY_URL = '/api/assistant/query/';

/**
 * POST a natural-language query to JobRhythm Assistant.
 * @param {string} message
 * @param {{ view?: string|null, route_name?: string|null, entity_type?: string|null, entity_id?: number|null }} context
 * @returns {Promise<object>} structured assistant response
 */
export async function postQuery(message, context = {}) {
  const payload = {
    schema_version: '1',
    message: String(message || '').trim(),
    context: {
      view: context.view ?? null,
      route_name: context.route_name ?? null,
      entity_type: context.entity_type ?? null,
      entity_id: context.entity_id ?? null,
    },
  };
  const response = await axios.post(QUERY_URL, payload);
  return response.data;
}

/**
 * Map axios/network errors to a user-facing English message.
 * @param {unknown} error
 * @returns {{ status: number|null, code: string|null, message: string }}
 */
export function getAssistantErrorInfo(error) {
  if (!error || !error.response) {
    return {
      status: null,
      code: 'network_error',
      message: 'Unable to reach JobRhythm Assistant. Check your connection and try again.',
    };
  }

  const status = error.response.status;
  const data = error.response.data || {};
  const code = data.code || null;
  const detail = typeof data.detail === 'string' ? data.detail : null;

  if (status === 401) {
    return {
      status,
      code: code || 'unauthorized',
      message: detail || 'Your session expired. Please sign in again.',
    };
  }
  if (status === 403) {
    return {
      status,
      code: code || 'permission_denied',
      message:
        detail ||
        'You do not have permission to use JobRhythm Assistant for documents.',
    };
  }
  if (status === 503) {
    return {
      status,
      code: code || 'assistant_disabled',
      message: detail || 'JobRhythm Assistant is temporarily unavailable.',
    };
  }
  if (status === 400) {
    return {
      status,
      code: code || 'validation_error',
      message: detail || 'The request could not be processed. Please rephrase and try again.',
    };
  }
  if (status >= 500) {
    return {
      status,
      code: code || 'server_error',
      message: detail || 'Something went wrong on the server. Please try again.',
    };
  }

  return {
    status,
    code,
    message: detail || 'Unable to complete the request. Please try again.',
  };
}
