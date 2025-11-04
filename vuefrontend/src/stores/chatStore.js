// Este script define una tienda de autenticación utilizando la Composition API de Vue
// Pinia comparte datos entre diferentes partes de la aplicación Vue 3
import { defineStore } from 'pinia'  // npm install pinia
import axios from 'axios'

export const useChatStore = defineStore('chatStore', {
  state: () => ({
    unreadEvents: []
  }),

  getters: {
    unreadTotal(state) {
      return state.unreadEvents.reduce((sum, e) => sum + e.unread_messages, 0)
    }
  },

  actions: {
    async fetchUnreadEvents() {
      try {
        const res = await axios.get('/api/unread-chat-counts/')
        const raw = res.data || {}

        if (typeof raw !== 'object') {
          throw new Error('Invalid response format')
        }

        this.unreadEvents = Object.entries(raw)
          .map(([event_id, count]) => ({
            event_id: parseInt(event_id),
            unread_messages: count
          }))
          .sort((a, b) => b.unread_messages - a.unread_messages) // orden opcional
      } catch (err) {
        console.error('ChatStore error:', err)
        this.unreadEvents = []
      }
    },

    markEventAsRead(event_id) {
      const event = this.unreadEvents.find(e => e.event_id === event_id)
      if (event) {
        event.unread_messages = 0
      }
    },

    updateUnreadEvent(event_id, count) {
      const existing = this.unreadEvents.find(e => e.event_id === event_id)
      if (existing) {
        existing.unread_messages = count
      } else {
        this.unreadEvents.push({ event_id: parseInt(event_id), unread_messages: count })
      }
    }
  }
})
