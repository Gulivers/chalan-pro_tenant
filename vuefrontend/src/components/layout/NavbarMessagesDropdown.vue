<template>
  <li v-if="shouldShow" class="nav-item mx-1">
    <router-link to="/chat-general" class="nav-link p-0">
      <button type="button" class="btn btn-sm btn-primary position-relative">
        <img :src="envelopeIcon" alt="Messages" width="24" height="24" />
        <span
          v-if="chatStore.unreadTotal > 0"
          class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-warning">
          {{ chatStore.unreadTotal }}
          <span class="visually-hidden">unread messages</span>
        </span>
      </button>
    </router-link>
  </li>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useChatStore } from '@/stores/chatStore'
import envelopeIcon from '@/assets/img/envelope-arrow-up.svg'
import axios from 'axios'
import messageSound from '@/assets/sounds/mixkit-sci-fi-confirmation-914.wav'

const ensureTrailingSlash = (url = '') => (url.endsWith('/') ? url : `${url}/`); // Añade slash final.
const stripTrailingSlash = (url = '') => url.replace(/\/+$/, ''); // Quita slashes extra.
const stripLeadingSlash = (path = '') => path.replace(/^\/+/, ''); // Quita slashes al inicio.

const getWsBaseUrl = () => {
  const explicit = window.__WS_BASE_URL || '';
  if (explicit) return ensureTrailingSlash(explicit);
  const api = window.__API_BASE_URL || '';
  if (api.startsWith('https://')) return ensureTrailingSlash(`wss://${api.slice(8)}`);
  if (api.startsWith('http://')) return ensureTrailingSlash(`ws://${api.slice(7)}`);
  return ensureTrailingSlash(api);
};

const buildWsUrl = (path = '') => {
  const base = stripTrailingSlash(getWsBaseUrl());
  const cleanPath = stripLeadingSlash(path);
  return `${base}/${cleanPath}`;
};

export default {
  setup() {
    const route = useRoute()
    const chatStore = useChatStore()
    const ws = ref(null)
    const userId = ref(null)
    const lastUnreadTotal = ref(0)
    const audio = new Audio(messageSound)
    
    // Verificar reactivamente si debemos mostrar el componente
    const shouldShow = computed(() => {
      // Si la ruta tiene hideNavbar, no mostrar
      if (route.meta.hideNavbar) {
        return false
      }
      
      const token = localStorage.getItem('authToken')
      if (!token) {
        return false
      }
      
      // Verificar también por pathname como fallback
      const currentPath = window.location.pathname || route.path || ''
      const publicPaths = ['/onboarding', '/login', '/reset_password', '/reset-password-confirm']
      const isPublicRoute = publicPaths.some(path => currentPath.startsWith(path))
      
      return !isPublicRoute
    })

    const connectWebSocket = async () => {
      // Verificar PRIMERO si el componente debería mostrarse
      if (!shouldShow.value) {
        console.log('[NavbarMessagesDropdown] connectWebSocket: Component should not show, skipping.')
        return
      }
      
      // Verificar que hay un token antes de intentar conectar
      const token = localStorage.getItem('authToken')
      if (!token) {
        console.log('[NavbarMessagesDropdown] No token, skipping WebSocket connection')
        return
      }
      
      // Verificar si estamos en una ruta pública
      const currentPath = window.location.pathname || route.path || ''
      const publicPaths = ['/onboarding', '/login', '/reset_password', '/reset-password-confirm', '/about']
      const isPublicRoute = publicPaths.some(path => currentPath.startsWith(path))
      
      if (isPublicRoute) {
        console.log('[NavbarMessagesDropdown] connectWebSocket: Public route, skipping.')
        return
      }
      
      try {
        const res = await axios.get('/api/user_detail/')
        userId.value = res.data.id

        if (!userId.value) throw new Error('User ID not found.')

        ws.value = new WebSocket(buildWsUrl(`ws/schedule/unread/user/${userId.value}/`))

        ws.value.onopen = () => console.log('[WS] Connected to unread chat count.')

        ws.value.onmessage = async (event) => {
          const data = JSON.parse(event.data)

          if (data.type === 'unread.updated') {
            const { event_id, count, user_id: sender } = data

            if (sender !== userId.value) {
              await chatStore.fetchUnreadEvents()
              if (chatStore.unreadTotal > lastUnreadTotal.value) {
                audio.play().catch(err => console.warn('Audio playback failed:', err))
              }
              lastUnreadTotal.value = chatStore.unreadTotal
            }
          }
        }

        ws.value.onclose = () => console.warn('[WS] Chat unread WebSocket closed.')
        ws.value.onerror = (err) => console.error('[WS] Error:', err)
      } catch (err) {
        // Silenciar errores 401 ya que son esperados cuando no hay autenticación
        if (err.response?.status !== 401) {
          console.error('Failed to connect WebSocket:', err)
        }
      }
    }

    onMounted(async () => {
      // Verificar PRIMERO si el componente debería mostrarse
      // Si no debería mostrarse, no hacer NINGUNA llamada
      if (!shouldShow.value) {
        console.log('[NavbarMessagesDropdown] Component should not show, skipping ALL operations', {
          hideNavbar: route.meta.hideNavbar,
          path: route.path,
          currentPath: window.location.pathname,
          hasToken: !!localStorage.getItem('authToken')
        })
        return
      }
      
      // Verificar si estamos en una ruta pública ANTES de cualquier otra cosa
      const currentPath = window.location.pathname || route.path || ''
      const publicPaths = ['/onboarding', '/login', '/reset_password', '/reset-password-confirm', '/about']
      const isPublicRoute = publicPaths.some(path => currentPath.startsWith(path))
      
      if (isPublicRoute) {
        console.log('[NavbarMessagesDropdown] Public route detected, skipping ALL API calls', { currentPath })
        return
      }
      
      // Solo hacer llamadas a la API si el usuario está autenticado
      const token = localStorage.getItem('authToken')
      if (!token) {
        console.log('[NavbarMessagesDropdown] No token, skipping API calls')
        return
      }
      
      // Si llegamos aquí, el usuario está autenticado y no es una ruta pública
      try {
        await chatStore.fetchUnreadEvents()
        lastUnreadTotal.value = chatStore.unreadTotal
        connectWebSocket()
      } catch (err) {
        // Silenciar errores 401 ya que son esperados cuando no hay autenticación
        if (err.response?.status !== 401) {
          console.warn('[NavbarMessagesDropdown] Error fetching unread events:', err)
        }
      }
    })

    onBeforeUnmount(() => {
      if (ws.value) ws.value.close()
    })

    return {
      chatStore,
      envelopeIcon,
      shouldShow,
    }
  }
}
</script>

<style scoped>
.badge {
  font-size: 0.75rem;
  padding: 0.35em 0.6em;
}
</style>
