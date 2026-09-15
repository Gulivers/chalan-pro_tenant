// Este script define una tienda de autenticación utilizando la Composition API de Vue
// Pinia comparte datos entre diferentes partes de la aplicación Vue 3
import { defineStore } from 'pinia'  // npm install pinia
import axios from 'axios'

export const useChatStore = defineStore('chatStore', {
  state: () => ({
    unreadEvents: [],
    eventsMap: {},
    loadingDetails: false
  }),

  getters: {
    unreadTotal(state) {
      return state.unreadEvents.reduce((sum, e) => sum + (e.unread_messages || 0), 0)
    },
    unreadNotifications(state) {
      return state.unreadEvents
        .filter(e => (e.unread_messages || 0) > 0)
        .map(e => {
          const d = state.eventsMap[e.event_id] || {}
          return {
            id: e.event_id,
            unread_messages: e.unread_messages,
            title: d.title || `Work Order #${e.event_id}`,
            crew_title: d.crew_title || '',
            crew_category: d.crew_category || '',
            work_account: d.work_account || null,
            work_account_title: d.work_account_title || '',
            date: d.date || '',
            extended_service: !!d.extended_service,
            ...d
          }
        })
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
            unread_messages: Number(count) || 0
          }))
          .filter(e => e.unread_messages > 0)
          .sort((a, b) => b.unread_messages - a.unread_messages)

        await this.loadMissingEventDetails()
      } catch (err) {
        console.error('ChatStore error:', err)
        this.unreadEvents = []
      }
    },

    async loadMissingEventDetails() {
      const missingIds = this.unreadEvents
        .map(e => e.event_id)
        .filter(id => id && !this.eventsMap[id])

      if (missingIds.length === 0) return

      this.loadingDetails = true
      try {
        await Promise.all(
          missingIds.map(async (id) => {
            try {
              const { data } = await axios.get(`/api/event/${id}/`)
              if (data) {
                this.eventsMap[id] = data
              }
            } catch (err) {
              console.warn(`[chatStore] Failed to fetch event ${id} details:`, err)
            }
          })
        )
      } finally {
        this.loadingDetails = false
      }
    },

    markEventAsRead(event_id) {
      const event = this.unreadEvents.find(e => e.event_id === event_id)
      if (event) {
        event.unread_messages = 0
      }
      this.unreadEvents = this.unreadEvents.filter(e => (e.unread_messages || 0) > 0)
    },

    async markAllAsRead() {
      const eventIds = this.unreadEvents.map(e => e.event_id)
      await Promise.all(
        eventIds.map(id => axios.post(`/api/mark-chat-read/${id}/`).catch(() => {}))
      )
      this.unreadEvents = []
    },

    async updateUnreadEvent(event_id, count) {
      const numericCount = Number(count) || 0
      const existing = this.unreadEvents.find(e => e.event_id === event_id)
      if (existing) {
        existing.unread_messages = numericCount
      } else if (numericCount > 0) {
        this.unreadEvents.push({ event_id: parseInt(event_id), unread_messages: numericCount })
      }
      this.unreadEvents = this.unreadEvents.filter(e => (e.unread_messages || 0) > 0)
      if (numericCount > 0 && !this.eventsMap[event_id]) {
        await this.loadMissingEventDetails()
      }
    }
  }
})
