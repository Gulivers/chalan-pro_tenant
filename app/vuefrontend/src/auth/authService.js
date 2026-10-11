import axios from 'axios'
import router from '../router'
import { useAuthStore } from '../stores/auth'

let renewTimer = null
const RENEW_LEAD_MS = 2 * 60 * 1000

function clearRenewTimer() {
  if (renewTimer) {
    clearTimeout(renewTimer)
    renewTimer = null
  }
}

function readAccessExpiryMs(token) {
  try {
    const part = String(token || '').split('.')[1]
    if (!part) return null
    const json = atob(part.replace(/-/g, '+').replace(/_/g, '/'))
    const exp = JSON.parse(json).exp
    return typeof exp === 'number' ? exp * 1000 : null
  } catch {
    return null
  }
}

function scheduleRenew(token) {
  clearRenewTimer()
  const expMs = readAccessExpiryMs(token)
  if (!expMs) return
  const delay = expMs - Date.now() - RENEW_LEAD_MS
  if (delay <= 0) return
  renewTimer = setTimeout(() => {
    renewTimer = null
    authService.refreshAccess().catch(() => {})
  }, delay)
}

const authService = {
  async login(username, password) {
    const response = await axios.post('/api/auth/login/', { username, password })
    const authStore = useAuthStore()
    authStore.applyLoginResponse(response.data)
    scheduleRenew(response.data.access)
    return response.data
  },

  async refreshAccess() {
    const authStore = useAuthStore()
    const body = {}
    const refresh = authStore.getRefreshToken()
    if (refresh) {
      body.refresh = refresh
    }
    const response = await axios.post('/api/auth/refresh/', body, {
      // Cookie mode sends jr_refresh automatically when same-origin
      withCredentials: true,
    })
    authStore.setAccessToken(response.data.access)
    if (response.data.refresh) {
      authStore.setRefreshToken(response.data.refresh)
    }
    scheduleRenew(response.data.access)
    return response.data.access
  },

  async handleLogout() {
    const authStore = useAuthStore()
    const refresh = authStore.getRefreshToken()
    try {
      await axios.post(
        '/api/auth/logout/',
        refresh ? { refresh } : {},
        { withCredentials: true }
      )
    } catch (_) {
      // Client cleanup proceeds even if server session already gone
    }
    clearRenewTimer()
    authStore.clearSession()
    router.push('/login')
  },

  async ensureAccess() {
    const authStore = useAuthStore()
    if (authStore.accessToken.value) {
      return authStore.accessToken.value
    }
    try {
      return await this.refreshAccess()
    } catch (_) {
      clearRenewTimer()
      authStore.clearSession()
      return null
    }
  },
}

export default authService
