<template>
  <Teleport to="body">
    <div
      v-if="isOpen"
      class="assistant-panel-root"
      :class="{ 'assistant-panel-root--mobile': isMobile }">
      <div
        class="assistant-panel-backdrop"
        aria-hidden="true"
        @click="close" />
      <aside
        class="assistant-panel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="assistant-panel-title"
        @keydown.esc.stop.prevent="close">
        <header class="assistant-panel__header">
          <div class="text-start flex-grow-1 pe-2">
            <h2 id="assistant-panel-title" class="assistant-panel__title mb-0">
              JobRhythm Assistant
            </h2>
            <div class="assistant-panel__context text-muted" :title="contextLabel">
              Context: {{ contextLabel }}
            </div>
          </div>
          <button
            type="button"
            class="btn-close"
            aria-label="Close Assistant"
            @click="close" />
        </header>

        <div ref="messageList" class="assistant-panel__messages" tabindex="-1">
          <div v-if="!messages.length && status === 'idle'" class="assistant-empty">
            <p class="mb-2 text-muted small">
              Ask about purchases, vendors, and spending. Results are structured
              (tables, KPIs, charts) — never free HTML.
            </p>
            <div class="assistant-suggestions">
              <button
                v-for="(prompt, index) in suggestions"
                :key="index"
                type="button"
                class="assistant-chip"
                :disabled="status === 'loading'"
                @click="sendSuggestion(prompt)">
                {{ prompt }}
              </button>
            </div>
          </div>

          <div
            v-for="msg in messages"
            :key="msg.id"
            class="assistant-msg"
            :class="msg.role === 'user' ? 'assistant-msg--user' : 'assistant-msg--assistant'">
            <div class="assistant-msg__bubble">
              <div v-if="msg.text" class="assistant-msg__text">{{ msg.text }}</div>
              <BlockRenderer
                v-if="msg.role === 'assistant' && msg.blocks?.length"
                :blocks="msg.blocks"
                @navigate="onBlockNavigate" />
              <SourcesBlock
                v-if="msg.role === 'assistant' && msg.sources?.length"
                :sources="msg.sources" />
              <div
                v-if="msg.role === 'assistant' && msg.partial"
                class="small text-warning mt-1">
                Partial result — more rows may exist.
              </div>
              <div v-if="msg.error" class="assistant-msg__error mt-1">
                {{ msg.error }}
                <button
                  v-if="msg.canRetry"
                  type="button"
                  class="btn btn-sm btn-outline-secondary ms-2"
                  @click="retryLast">
                  Retry
                </button>
              </div>
            </div>
          </div>

          <div
            v-if="showFollowUpSuggestions"
            class="assistant-followups">
            <p class="assistant-followups__label mb-2">
              Try another question:
            </p>
            <div class="assistant-suggestions">
              <button
                v-for="(prompt, index) in remainingSuggestions"
                :key="`followup-${index}`"
                type="button"
                class="assistant-chip"
                :disabled="status === 'loading'"
                @click="sendSuggestion(prompt)">
                {{ prompt }}
              </button>
            </div>
          </div>

          <div v-if="status === 'loading'" class="assistant-loading text-muted small">
            <span
              class="spinner-border spinner-border-sm me-2"
              role="status"
              aria-hidden="true" />
            Analyzing…
          </div>
        </div>

        <footer class="assistant-panel__footer">
          <form class="assistant-input-row" @submit.prevent="submit">
            <label class="visually-hidden" for="assistant-input">Message</label>
            <textarea
              id="assistant-input"
              ref="inputEl"
              v-model="draft"
              class="form-control form-control-sm assistant-input"
              rows="2"
              maxlength="2000"
              placeholder="Ask about transactions or spending…"
              :disabled="status === 'loading'"
              @keydown.enter.exact.prevent="submit" />
            <button
              type="submit"
              class="btn btn-primary btn-sm assistant-send"
              :disabled="!canSend">
              Send
            </button>
          </form>
        </footer>
      </aside>
    </div>
  </Teleport>
</template>

<script>
import {
  ASSISTANT_CLOSE,
  ASSISTANT_OPEN,
  ASSISTANT_TOGGLE,
  assistantBus,
} from '@/utils/assistantBus';
import { postQuery, getAssistantErrorInfo } from '@/services/assistantApi';
import { useAssistantContext } from '@/composables/useAssistantContext';
import BlockRenderer from './BlockRenderer.vue';
import SourcesBlock from './blocks/SourcesBlock.vue';

const SUGGESTIONS = [
  'Show me Home Depot transactions over $1,500 this month.',
  'How much did we spend with Home Depot this month?',
  'Show purchases by vendor this month.',
  'Compare purchases by supplier for the last six months.',
  'Show the five vendors with the highest spending.',
  'Graph spending for the last three months.',
];

let msgSeq = 0;
function nextMsgId() {
  msgSeq += 1;
  return `msg-${Date.now()}-${msgSeq}`;
}

export default {
  name: 'AssistantPanel',
  components: {
    BlockRenderer,
    SourcesBlock,
  },
  setup() {
    const { context, contextLabel } = useAssistantContext();
    return { pageContext: context, contextLabel };
  },
  data() {
    return {
      isOpen: false,
      isMobile: false,
      draft: '',
      status: 'idle', // idle | loading | error
      messages: [],
      suggestions: SUGGESTIONS,
      lastUserMessage: null,
      _mediaQuery: null,
    };
  },
  computed: {
    canSend() {
      return this.status !== 'loading' && String(this.draft || '').trim().length > 0;
    },
    askedSuggestionSet() {
      const asked = new Set();
      for (const msg of this.messages) {
        if (msg.role === 'user' && typeof msg.text === 'string') {
          asked.add(msg.text.trim().toLowerCase());
        }
      }
      return asked;
    },
    remainingSuggestions() {
      return this.suggestions.filter(
        (prompt) => !this.askedSuggestionSet.has(prompt.trim().toLowerCase()),
      );
    },
    showFollowUpSuggestions() {
      return (
        this.messages.length > 0 &&
        this.status !== 'loading' &&
        this.remainingSuggestions.length > 0
      );
    },
  },
  mounted() {
    this._onOpen = () => this.open();
    this._onClose = () => this.close();
    this._onToggle = () => (this.isOpen ? this.close() : this.open());
    assistantBus.on(ASSISTANT_OPEN, this._onOpen);
    assistantBus.on(ASSISTANT_CLOSE, this._onClose);
    assistantBus.on(ASSISTANT_TOGGLE, this._onToggle);

    this._mediaQuery = window.matchMedia('(max-width: 767.98px)');
    this._onMedia = () => {
      this.isMobile = !!this._mediaQuery.matches;
    };
    this._onMedia();
    if (this._mediaQuery.addEventListener) {
      this._mediaQuery.addEventListener('change', this._onMedia);
    } else if (this._mediaQuery.addListener) {
      this._mediaQuery.addListener(this._onMedia);
    }

    this._onKeydown = (event) => {
      if (event.key === 'Escape' && this.isOpen) {
        this.close();
      }
    };
    window.addEventListener('keydown', this._onKeydown);
  },
  beforeUnmount() {
    assistantBus.off(ASSISTANT_OPEN, this._onOpen);
    assistantBus.off(ASSISTANT_CLOSE, this._onClose);
    assistantBus.off(ASSISTANT_TOGGLE, this._onToggle);
    window.removeEventListener('keydown', this._onKeydown);
    if (this._mediaQuery) {
      if (this._mediaQuery.removeEventListener) {
        this._mediaQuery.removeEventListener('change', this._onMedia);
      } else if (this._mediaQuery.removeListener) {
        this._mediaQuery.removeListener(this._onMedia);
      }
    }
    this.unlockBodyScroll();
  },
  methods: {
    open() {
      this.isOpen = true;
      this.lockBodyScroll();
      this.$nextTick(() => {
        this.$refs.inputEl?.focus?.();
        this.scrollToBottom();
      });
    },
    close() {
      this.isOpen = false;
      this.unlockBodyScroll();
    },
    lockBodyScroll() {
      if (typeof document !== 'undefined') {
        document.body.style.overflow = 'hidden';
      }
    },
    unlockBodyScroll() {
      if (typeof document !== 'undefined') {
        document.body.style.overflow = '';
      }
    },
    sendSuggestion(prompt) {
      this.draft = prompt;
      this.submit();
    },
    async submit() {
      const message = String(this.draft || '').trim();
      if (!message || this.status === 'loading') return;

      this.draft = '';
      this.lastUserMessage = message;
      this.messages.push({
        id: nextMsgId(),
        role: 'user',
        text: message,
      });
      this.status = 'loading';
      this.scrollToBottom();

      try {
        const data = await postQuery(message, this.pageContext || {});
        const assistantMsg = {
          id: nextMsgId(),
          role: 'assistant',
          text: typeof data?.message === 'string' ? data.message : '',
          blocks: Array.isArray(data?.blocks) ? data.blocks : [],
          sources: Array.isArray(data?.sources) ? data.sources : [],
          partial: !!(data?.meta && data.meta.partial),
          error: null,
          canRetry: false,
        };
        this.messages.push(assistantMsg);
        this.status = 'idle';
      } catch (error) {
        const info = getAssistantErrorInfo(error);
        this.messages.push({
          id: nextMsgId(),
          role: 'assistant',
          text: '',
          blocks: [],
          sources: [],
          error: info.message,
          canRetry: info.status !== 403 && info.status !== 401,
        });
        this.status = 'error';
      }

      this.scrollToBottom();
    },
    retryLast() {
      if (!this.lastUserMessage || this.status === 'loading') return;
      this.draft = this.lastUserMessage;
      // Drop the last error assistant message for a cleaner retry.
      const last = this.messages[this.messages.length - 1];
      if (last?.role === 'assistant' && last.error) {
        this.messages.pop();
      }
      const lastUser = this.messages[this.messages.length - 1];
      if (lastUser?.role === 'user' && lastUser.text === this.lastUserMessage) {
        this.messages.pop();
      }
      this.submit();
    },
    onBlockNavigate() {
      // Entity links open in a new browser tab; keep the Assistant panel open.
    },
    scrollToBottom() {
      this.$nextTick(() => {
        const el = this.$refs.messageList;
        if (el) {
          el.scrollTop = el.scrollHeight;
        }
      });
    },
  },
};
</script>

<style scoped>
.assistant-panel-root {
  position: fixed;
  inset: 0;
  z-index: 1080;
  display: flex;
  justify-content: flex-end;
  pointer-events: none;
}

.assistant-panel-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  pointer-events: auto;
}

.assistant-panel {
  position: relative;
  display: flex;
  flex-direction: column;
  width: min(460px, 100%);
  max-width: 100%;
  height: 100%;
  background: #fff;
  box-shadow: -4px 0 24px rgba(0, 0, 0, 0.18);
  pointer-events: auto;
  text-align: left;
}

.assistant-panel-root--mobile .assistant-panel {
  width: 100%;
}

.assistant-panel__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 0.85rem 1rem;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  background: #212529;
  color: #fff;
}

.assistant-panel__title {
  font-size: 1.05rem;
  font-weight: 650;
  color: #fff;
}

.assistant-panel__context {
  font-size: 0.72rem;
  color: rgba(255, 255, 255, 0.7) !important;
  margin-top: 0.15rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 340px;
}

.assistant-panel__header .btn-close {
  filter: invert(1) grayscale(100%);
  opacity: 0.85;
}

.assistant-panel__messages {
  flex: 1;
  overflow-y: auto;
  padding: 0.85rem 1rem;
  background: #f4f6f8;
}

.assistant-empty {
  text-align: left;
}

.assistant-suggestions {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.assistant-followups {
  margin: 0.25rem 0 0.85rem;
  padding: 0.65rem 0.7rem;
  border-radius: 0.65rem;
  background: rgba(13, 110, 253, 0.04);
  border: 1px dashed rgba(13, 110, 253, 0.28);
  text-align: left;
}

.assistant-followups__label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #495057;
}

.assistant-chip {
  text-align: left;
  border: 1px solid rgba(13, 110, 253, 0.25);
  background: #fff;
  color: #0d6efd;
  border-radius: 0.5rem;
  padding: 0.45rem 0.65rem;
  font-size: 0.8rem;
  line-height: 1.3;
  cursor: pointer;
}

.assistant-chip:hover:not(:disabled) {
  background: rgba(13, 110, 253, 0.06);
}

.assistant-chip:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.assistant-msg {
  display: flex;
  margin-bottom: 0.75rem;
}

.assistant-msg--user {
  justify-content: flex-end;
}

.assistant-msg--assistant {
  justify-content: flex-start;
}

.assistant-msg__bubble {
  max-width: 100%;
  padding: 0.55rem 0.7rem;
  border-radius: 0.65rem;
  background: #fff;
  border: 1px solid rgba(0, 0, 0, 0.06);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
}

.assistant-msg--user .assistant-msg__bubble {
  background: #0d6efd;
  color: #fff;
  border-color: transparent;
  max-width: 92%;
}

.assistant-msg__text {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.9rem;
  line-height: 1.4;
  margin-bottom: 0.25rem;
}

.assistant-msg--user .assistant-msg__text {
  margin-bottom: 0;
}

.assistant-msg__error {
  color: #842029;
  background: #f8d7da;
  border-radius: 0.35rem;
  padding: 0.4rem 0.5rem;
  font-size: 0.82rem;
}

.assistant-loading {
  display: flex;
  align-items: center;
  padding: 0.35rem 0;
}

.assistant-panel__footer {
  border-top: 1px solid rgba(0, 0, 0, 0.08);
  padding: 0.65rem 0.75rem;
  background: #fff;
}

.assistant-input-row {
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
}

.assistant-input {
  resize: none;
  flex: 1;
}

.assistant-send {
  min-width: 4.25rem;
}
</style>
