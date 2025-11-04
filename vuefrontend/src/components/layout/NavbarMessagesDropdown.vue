<template>
  <li class="nav-item mx-1">
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
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useChatStore } from '@/stores/chatStore'
import envelopeIcon from '@/assets/img/envelope-arrow-up.svg'
import axios from 'axios'
import messageSound from '@/assets/sounds/mixkit-sci-fi-confirmation-914.wav'

export default {
  setup() {
    const chatStore = useChatStore()
    const ws = ref(null)
    const userId = ref(null)
    const lastUnreadTotal = ref(0)
    const audio = new Audio(messageSound)

    const connectWebSocket = async () => {
      try {
        const res = await axios.get('/api/user_detail/')
        userId.value = res.data.id

        if (!userId.value) throw new Error('User ID not found.')

        ws.value = new WebSocket(`${process.env.VUE_APP_WS_BASE_URL}ws/schedule/unread/user/${userId.value}/`)

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
        console.error('Failed to connect WebSocket:', err)
      }
    }

    onMounted(async () => {
      await chatStore.fetchUnreadEvents()
      lastUnreadTotal.value = chatStore.unreadTotal
      connectWebSocket()
    })

    onBeforeUnmount(() => {
      if (ws.value) ws.value.close()
    })

    return {
      chatStore,
      envelopeIcon,
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
