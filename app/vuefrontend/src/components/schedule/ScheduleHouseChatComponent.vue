<template>
  <div class="h-100">
    <div class="d-flex flex-column h-100 p-lg-3 p-1">
      <!-- Debug: Show received eventId prop -->
      <div class="alert alert-info" v-if="debugMode">
        <strong>Debug:</strong> eventId = {{ eventId }}
      </div>

      <!-- Chat window with full height -->
      <div class="chat-window border rounded p-3 d-flex flex-column flex-grow-1">
        <h5 class="border-bottom pb-2 text-center">Chat for Job</h5>

        <div ref="chatContainer" class="chat-messages d-flex flex-column overflow-auto">
          <div v-for="message in messages" :key="message.id" class="my-2 p-2 rounded d-inline-block" style="max-width: 95%"
               :class="message.author?.id === user?.id ? 'bg-light text-black ms-auto ' : 'bg-secondary text-white me-auto'">
            <div class="w-100" style="font-size: .7rem">{{message.author?.username}} : {{parseDate(message.timestamp)}}</div>
            {{ message.message }}
          </div>
        </div>
      </div>

      <div class="mt-3 d-flex">
        <input v-model="newMessage" @keyup.enter="sendMessage" class="form-control me-2"
               placeholder="Type a message..." :disabled="!canSendMessage">
        <button @click="sendMessage" class="btn btn-outline-success" :disabled="!canSendMessage">
          <img src="@assets/img/ico-send.svg" alt="Add" width="25" height="25">
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import '@assets/css/base.css';
import axios from "axios";
import {useAuthStore} from '@stores/auth'
import dayjs from 'dayjs'

export default {
  props: {
    eventId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      user: null,
      newMessage: '',
      messages: [],
      websocket: null,
      wsUrl: null,
      canSendMessage: null,
      debugMode: false,
      workAccountId: null,
    };
  },
  async mounted() {
    const authStore = useAuthStore()
    this.user = authStore.user.value
    this.canSendMessage = this.hasPermission('appschedule.add_eventchatmessage')
    
    // Obtener work_account_id del evento
    await this.loadWorkAccountId();
    
    // WebSocket + carga inicial (usar work_account si está disponible)
    if (this.workAccountId) {
      this.wsUrl = this.buildWsUrl(`ws/schedule/work-account/${this.workAccountId}/chat/`)
    } else {
      // Fallback a event_id si no hay work_account
      this.wsUrl = this.buildWsUrl(`ws/schedule/event/${this.$props.eventId}/chat/`)
    }
    console.log(`connect to WS ${this.wsUrl}`)
    this.connectWebSocket()
    this.getMessages()
    this.$nextTick(() => {
      setTimeout(() => this.scrollToBottom(), 300); // Delay por si la animación o slot tarda
    });

  },
  beforeUnmount() {
    this.disconnectWebSocket();
  },
  methods: {
    async loadWorkAccountId() {
      try {
        const { data } = await axios.get(`/api/event/${this.$props.eventId}/`);
        if (data && data.work_account) {
          this.workAccountId = data.work_account;
        }
      } catch (e) {
        console.error('Error fetching event data:', e);
      }
    },
    parseDate(date){
      const timestamp = dayjs(date)
      return timestamp.format('MMM DD YYYY, HH:mm')
    },

    async sendMessage() {
      if (this.newMessage.trim() === '') return;

      try {
        // El backend ahora usa work_account internamente, así que solo necesitamos enviar el mensaje
        const response = await axios.post(`/api/events/${this.$props.eventId}/chat/messages/`, {
          message: this.newMessage.trim(),
        });

        if ([200, 201].includes(response.status)) {
          this.messages.push(response.data);  // 👈 Agregarlo de una vez
          this.newMessage = '';
          this.$nextTick(() => this.scrollToBottom());
        } else {
          console.log('Error al enviar:', response);
        }
      } catch (e) {
        console.error('Error sending message:', e);
      }
    },

    connectWebSocket() {
      if (!this.wsUrl) {
        console.warn('WebSocket URL no configurada (Chat); se omite la conexión.');
        return;
      }
      this.websocket = new WebSocket(this.wsUrl);
      this.websocket.onopen = () => {
        console.log('WebSocket connection established.');
      };

      this.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'chat.updated') {
          // Evita duplicar si el autor es el usuario actual
          if (data.data.author?.id !== this.user.id) {
            this.messages.push(data.data);
            this.$nextTick(() => this.scrollToBottom());
          }
        }
      };

      this.websocket.onclose = () => {
        console.log('WebSocket connection closed.');
        // Opcional: Intenta reconectar después de un tiempo
        // setTimeout(this.connectWebSocket, 3000);
      };

      this.websocket.onerror = (error) => {
        console.error('Error de WebSocket:', error);
      };
    },
    disconnectWebSocket() {
      if (this.websocket) {
        this.websocket.close();
        this.websocket = null;
      }
    },
    async getMessages() {
      try {
        const response = await axios.get(`/api/events/${this.$props.eventId}/chat/messages/`);
        if (response.status === 200) {
          console.log(this.user)
          console.log('getMessages:', response.data)
          this.messages = response.data;
          this.$nextTick(() => this.scrollToBottom());
        }
      } catch (error) {
        console.error('Error fetching event chats data:', error);
      }
    },
    scrollToBottom() {
      const container = this.$refs.chatContainer;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    }
  }
};
</script>

<style>
.chat-messages {
  max-height: 60vh;
  overflow-y: auto;
  padding-bottom: 10px;
}

.container-fluid {
  height: 100%;
}

.chat-window {
  height: 100%;
  min-height: 200px;
}
</style>
