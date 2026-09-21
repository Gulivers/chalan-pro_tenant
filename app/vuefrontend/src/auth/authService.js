import axios from 'axios'
import router from '../router'
import { useAuthStore } from '../stores/auth'

const authService = {
  async login(username, password) {
    const response = await axios.post('/api/auth/login/', { username, password })
    const authStore = useAuthStore()
    authStore.applyLoginResponse(response.data)
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
      authStore.clearSession()
      return null
    }
  },
}

export default authService
