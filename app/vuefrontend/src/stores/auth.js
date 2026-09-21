/**
 * JobRhythm auth session (Stage B JWT).
 * - access: in-memory only
 * - refresh: HttpOnly cookie (default, shared across tabs) OR body+sessionStorage
 *   when AUTH_USE_REFRESH_COOKIE=False
 * - jr_session: non-secret localStorage flag so new tabs know to call /refresh/
 * - userPermissions: localStorage (UX only; backend remains authority)
 */
import { ref, computed } from 'vue'
import axios from 'axios'

const ACCESS_KEY = 'jr_access' // legacy clear only
const REFRESH_SESSION_KEY = 'jr_refresh'
const SESSION_FLAG_KEY = 'jr_session'
const PERMS_KEY = 'userPermissions'
const LEGACY_TOKEN_KEY = 'authToken'

const accessToken = ref(null)
const user = ref(null)

function clearLegacyStorage() {
  try {
    localStorage.removeItem(LEGACY_TOKEN_KEY)
    localStorage.removeItem(ACCESS_KEY)
  } catch (_) {
    /* ignore */
  }
}

function setSessionFlag(on) {
  try {
    if (on) {
      localStorage.setItem(SESSION_FLAG_KEY, '1')
    } else {
      localStorage.removeItem(SESSION_FLAG_KEY)
    }
  } catch (_) {
    /* ignore */
  }
}

function hasSessionFlag() {
  try {
    return localStorage.getItem(SESSION_FLAG_KEY) === '1'
  } catch (_) {
    return false
  }
}

export function useAuthStore() {
  const isAuthenticated = computed(() => !!accessToken.value)

  function setAccessToken(token) {
    accessToken.value = token || null
    if (token) {
      axios.defaults.headers.common.Authorization = `Bearer ${token}`
    } else {
      delete axios.defaults.headers.common.Authorization
    }
  }

  function setRefreshToken(token) {
    // Body mode only (when server returns refresh in JSON). Never localStorage.
    if (token) {
      sessionStorage.setItem(REFRESH_SESSION_KEY, token)
    } else {
      sessionStorage.removeItem(REFRESH_SESSION_KEY)
    }
  }

  function getRefreshToken() {
    return sessionStorage.getItem(REFRESH_SESSION_KEY)
  }

  function setPermissions(permissions) {
    const list = Array.isArray(permissions) ? permissions : []
    localStorage.setItem(PERMS_KEY, JSON.stringify({ permissions: list }))
  }

  function setUser(newUser) {
    user.value = newUser
  }

  function applyLoginResponse(data) {
    clearLegacyStorage()
    setAccessToken(data.access)
    // Cookie mode: refresh is null in body; browser stores HttpOnly jr_refresh.
    // Body mode: refresh string → sessionStorage (single-tab only).
    if (data.refresh) {
      setRefreshToken(data.refresh)
    } else {
      setRefreshToken(null)
    }
    setSessionFlag(true)
    if (Array.isArray(data.permissions)) {
      setPermissions(data.permissions)
    }
    if (data.user) {
      setUser(data.user)
    }
  }

  function clearSession() {
    setAccessToken(null)
    setRefreshToken(null)
    setUser(null)
    setSessionFlag(false)
    clearLegacyStorage()
    try {
      localStorage.removeItem(PERMS_KEY)
    } catch (_) {
      /* ignore */
    }
  }

  function logout() {
    clearSession()
  }

  return {
    token: accessToken,
    accessToken,
    user,
    isAuthenticated,
    setToken: setAccessToken,
    setAccessToken,
    setRefreshToken,
    getRefreshToken,
    setPermissions,
    setUser,
    applyLoginResponse,
    clearSession,
    logout,
    hasSessionFlag,
  }
}

export { REFRESH_SESSION_KEY, PERMS_KEY, SESSION_FLAG_KEY }
