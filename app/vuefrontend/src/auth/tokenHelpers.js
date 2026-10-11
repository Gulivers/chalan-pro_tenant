import { useAuthStore } from '@/stores/auth'
import { SESSION_FLAG_KEY, REFRESH_SESSION_KEY } from '@/stores/auth'

/** Current JWT access token (memory). */
export function getAccessToken() {
  try {
    return useAuthStore().accessToken?.value || null
  } catch (_) {
    return null
  }
}

/**
 * True if we can attempt to restore a session in this tab:
 * - access already in memory, or
 * - body-mode refresh in sessionStorage, or
 * - cookie-mode session flag in localStorage (HttpOnly cookie is invisible to JS)
 */
export function hasAuthSession() {
  if (getAccessToken()) return true
  try {
    if (sessionStorage.getItem(REFRESH_SESSION_KEY)) return true
  } catch (_) {
    /* ignore */
  }
  try {
    return localStorage.getItem(SESSION_FLAG_KEY) === '1'
  } catch (_) {
    return false
  }
}

export function bearerAuthHeader() {
  const token = getAccessToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}
