<template>
  <div class="jr-pilot jr-house-chat">
    <div v-if="debugMode" class="jr-house-chat__debug" role="status">
      <strong>Debug:</strong> eventId = {{ eventId }}
    </div>

    <div class="jr-house-chat__window">
      <div class="jr-house-chat__header">
        <h3 class="jr-house-chat__title">Chat for Job</h3>
        <span v-if="messages.length" class="jr-house-chat__count">
          {{ messages.length }} {{ messages.length === 1 ? 'message' : 'messages' }}
        </span>
      </div>

      <div
        ref="chatContainer"
        class="jr-house-chat__messages"
        aria-live="polite">
        <JREmptyState
          v-if="!messages.length"
          title="No messages yet"
          description="Start the conversation for this work order." />
        <div
          v-for="message in messages"
          :key="message.id"
          class="jr-house-chat__bubble"
          :class="
            message.author?.id === user?.id
              ? 'jr-house-chat__bubble--mine'
              : 'jr-house-chat__bubble--theirs'
          ">
          <div class="jr-house-chat__meta">
            <span class="jr-house-chat__author">{{ message.author?.username || 'User' }}</span>
            <span class="jr-house-chat__dot" aria-hidden="true">·</span>
            <time class="jr-house-chat__time">{{ parseDate(message.timestamp) }}</time>
          </div>
          <div class="jr-house-chat__text">{{ message.message }}</div>
        </div>
      </div>

      <form class="jr-house-chat__composer" @submit.prevent="sendMessage">
        <JRInput
          inputId="house-chat-input"
          v-model="newMessage"
          type="text"
          placeholder="Type a message…"
          autocomplete="off"
          :disabled="!canSendMessage" />
        <JRButton
          type="submit"
          size="sm"
          :disabled="!canSendMessage || !newMessage.trim()"
          aria-label="Send message">
          Send
        </JRButton>
      </form>
    </div>
  </div>
</template>

<script>
import "@assets/css/base.css";
import axios from "axios";
import { useAuthStore } from "@stores/auth";
import dayjs from "dayjs";
import { JRButton, JREmptyState, JRInput } from "@ui";

export default {
  name: "ScheduleHouseChatComponent",
  components: {
    JRButton,
    JREmptyState,
    JRInput,
  },
  props: {
    eventId: {
      type: Number,
      required: true,
    },
    workAccountId: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      user: null,
      newMessage: "",
      messages: [],
      websocket: null,
      wsUrl: null,
      canSendMessage: null,
      debugMode: false,
      resolvedWorkAccountId: null,
    };
  },
  async mounted() {
    const authStore = useAuthStore();
    this.user = authStore.user?.value ?? null;
    if (!this.user) {
      const user = await this.getAuthenticatedUser();
      if (user) {
        authStore.setUser(user);
        this.user = user;
      }
    }
    this.canSendMessage = this.hasPermission(
      "appschedule.add_eventchatmessage"
    );

    await this.loadWorkAccountId();

    this.wsUrl = this.buildWsUrl(
      `ws/schedule/event/${this.$props.eventId}/chat/`
    );
    this.connectWebSocket();
    this.getMessages();
    this.$nextTick(() => {
      setTimeout(() => this.scrollToBottom(), 300);
    });
  },
  beforeUnmount() {
    this.disconnectWebSocket();
  },
  methods: {
    async loadWorkAccountId() {
      if (this.workAccountId) {
        this.resolvedWorkAccountId = this.workAccountId;
        return;
      }
      try {
        const { data } = await axios.get(`/api/event/${this.$props.eventId}/`);
        if (data && data.work_account) {
          this.resolvedWorkAccountId = data.work_account;
        }
      } catch (e) {
        console.error("Error fetching event data:", e);
      }
    },
    parseDate(date) {
      const timestamp = dayjs(date);
      return timestamp.format("MMM DD YYYY, HH:mm");
    },

    async sendMessage() {
      if (this.newMessage.trim() === "") return;

      try {
        const response = await axios.post(
          `/api/events/${this.$props.eventId}/chat/messages/`,
          {
            message: this.newMessage.trim(),
          }
        );

        if ([200, 201].includes(response.status)) {
          const created = response.data;
          if (
            created?.id != null &&
            !this.messages.some((m) => m.id === created.id)
          ) {
            this.messages.push(created);
          }
          this.newMessage = "";
          this.$nextTick(() => this.scrollToBottom());
        } else {
          console.log("Error al enviar:", response);
        }
      } catch (e) {
        console.error("Error sending message:", e);
      }
    },

    connectWebSocket() {
      if (!this.wsUrl) {
        console.warn(
          "WebSocket URL no configurada (Chat); se omite la conexión."
        );
        return;
      }
      this.websocket = new WebSocket(this.wsUrl);
      this.websocket.onopen = () => {
        console.log("WebSocket connection established.");
      };

      this.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "chat.updated" && data.data) {
          const currentUserId = this.user?.id;
          const incoming = data.data;
          const alreadyPresent =
            incoming.id != null &&
            this.messages.some((m) => m.id === incoming.id);
          if (alreadyPresent) return;
          if (incoming.author?.id !== currentUserId) {
            this.messages.push(incoming);
            this.$nextTick(() => this.scrollToBottom());
          }
        }
      };

      this.websocket.onclose = () => {
        console.log("WebSocket connection closed.");
      };

      this.websocket.onerror = (error) => {
        console.error("Error de WebSocket:", error);
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
        const response = await axios.get(
          `/api/events/${this.$props.eventId}/chat/messages/`
        );
        if (response.status === 200) {
          this.messages = response.data;
          this.$nextTick(() => this.scrollToBottom());
        }
      } catch (error) {
        console.error("Error fetching event chats data:", error);
      }
    },
    scrollToBottom() {
      const container = this.$refs.chatContainer;
      if (container) {
        container.scrollTop = container.scrollHeight;
      }
    },
  },
};
</script>

<style scoped>
.jr-house-chat {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-height: 22rem;
}

.jr-house-chat__debug {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface-muted, #f9fafb);
  color: var(--color-jr-muted, #4b5563);
  font-size: 0.75rem;
}

.jr-house-chat__window {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 18rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-panel, 0.75rem);
  background: var(--color-jr-surface, #fff);
  overflow: hidden;
}

.jr-house-chat__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface-muted, #f9fafb);
}

.jr-house-chat__title {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text, #111827);
  text-align: left;
}

.jr-house-chat__count {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-jr-muted, #4b5563);
}

.jr-house-chat__messages {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  flex: 1;
  max-height: 50vh;
  min-height: 12rem;
  overflow-y: auto;
  padding: 1rem 1.125rem;
  scrollbar-width: thin;
  scrollbar-color: var(--color-jr-hover-border, #d1d5db) var(--color-jr-surface-muted, #f9fafb);
}

.jr-house-chat__bubble {
  max-width: 82%;
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-panel, 0.75rem);
  font-size: 0.875rem;
  line-height: 1.45;
}

.jr-house-chat__bubble--mine {
  align-self: flex-end;
  background: color-mix(
    in srgb,
    var(--color-jr-primary, #2563eb) 10%,
    var(--color-jr-surface, #fff)
  );
  border-color: color-mix(
    in srgb,
    var(--color-jr-primary, #2563eb) 25%,
    var(--color-jr-border, #e5e7eb)
  );
  color: var(--color-jr-text, #111827);
}

.jr-house-chat__bubble--theirs {
  align-self: flex-start;
  background: var(--color-jr-surface-muted, #f9fafb);
  border-color: var(--color-jr-border, #e5e7eb);
  color: var(--color-jr-text, #111827);
}

.jr-house-chat__meta {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin-bottom: 0.25rem;
  font-size: 0.75rem;
  color: var(--color-jr-muted, #4b5563);
}

.jr-house-chat__bubble--mine .jr-house-chat__meta {
  justify-content: flex-end;
}

.jr-house-chat__author {
  font-weight: 600;
  color: var(--color-jr-text, #111827);
}

.jr-house-chat__dot {
  color: var(--color-jr-muted, #4b5563);
}

.jr-house-chat__time {
  color: var(--color-jr-muted, #4b5563);
}

.jr-house-chat__text {
  white-space: pre-wrap;
  word-break: break-word;
}

.jr-house-chat__composer {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface-muted, #f9fafb);
}

.jr-house-chat__composer :deep(.p-inputtext) {
  flex: 1;
  width: 100%;
}

.jr-house-chat__composer :deep(.jr-button) {
  flex-shrink: 0;
}
</style>
