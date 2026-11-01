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
        class="assistant-panel jr-pilot"
        role="dialog"
        aria-modal="true"
        aria-labelledby="assistant-panel-title"
        @keydown.esc.stop.prevent="close">
        <header class="assistant-panel__header">
          <div class="min-w-0 flex-1 pe-2 text-start">
            <h2 id="assistant-panel-title" class="assistant-panel__title mb-0">
              JobRhythm Assistant
            </h2>
            <div class="assistant-panel__context" :title="contextLabel">
              Context: {{ contextLabel }}
            </div>
          </div>
          <button
            type="button"
            class="assistant-panel__close"
            aria-label="Close Assistant"
            @click="close">
            Close
          </button>
        </header>

        <div ref="messageList" class="assistant-panel__messages" tabindex="-1">
          <div v-if="!messages.length && status === 'idle'" class="assistant-empty">
            <p class="mb-2 text-sm text-jr-muted">
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
                class="mt-1 text-sm text-jr-warning">
                Partial result — more rows may exist.
              </div>
              <div v-if="msg.error" class="assistant-msg__error mt-1">
                {{ msg.error }}
                <JRButton
                  v-if="msg.canRetry"
                  type="button"
                  size="sm"
                  variant="secondary"
                  class="ms-2"
                  @click="retryLast">
                  Retry
                </JRButton>
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

          <div v-if="status === 'loading'" class="assistant-loading text-sm text-jr-muted">
            <ProgressSpinner
              style="width: 1.25rem; height: 1.25rem"
              strokeWidth="6"
              aria-label="Analyzing" />
            Analyzing…
          </div>
        </div>

        <ActiveFilterChips
          :active-filters="activeFilters"
          :disabled="status === 'loading'"
          @remove="onRemoveFilterChip"
          @clear-all="onClearFilters" />

        <footer class="assistant-panel__footer">
          <form class="assistant-input-row" @submit.prevent="submit">
            <label class="jr-sr-only" for="assistant-input">Message</label>
            <JRTextarea
              inputId="assistant-input"
              ref="inputEl"
              v-model="draft"
              class="assistant-input"
              :rows="2"
              maxlength="2000"
              placeholder="Ask about transactions or spending…"
              :disabled="status === 'loading'"
              @keydown.enter.exact.prevent="submit" />
            <JRButton
              type="submit"
              size="sm"
              variant="primary"
              class="assistant-send"
              :disabled="!canSend">
              Send
            </JRButton>
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
import ProgressSpinner from 'primevue/progressspinner';
import { JRButton, JRTextarea } from '@/ui';
import ActiveFilterChips from './ActiveFilterChips.vue';
import BlockRenderer from './BlockRenderer.vue';
import SourcesBlock from './blocks/SourcesBlock.vue';

const SUGGESTIONS = [
  'Show me transactions over $1,500 this month.',
  'How much did we spend this month?',
  'Show purchases by vendor this month.',
  'Compare purchases by supplier for the last six months.',
  'Show the five vendors with the highest spending.',
  'Graph spending for the last three months.',
];

function messageForRemovedChip(chip) {
  if (!chip || typeof chip !== 'object') return null;
  if (chip.key === 'vendor') {
    const name = String(chip.label || '').trim();
    return name ? `Remove vendor ${name}.` : 'Any vendor.';
  }
  if (chip.key === 'min_amount') {
    return 'Include all amounts.';
  }
  if (chip.key === 'comparison_period') {
    return 'Clear comparison.';
  }
  return null;
}

let msgSeq = 0;
function nextMsgId() {
  msgSeq += 1;
  return `msg-${Date.now()}-${msgSeq}`;
}

export default {
  name: 'AssistantPanel',
  components: {
    ActiveFilterChips,
    BlockRenderer,
    SourcesBlock,
    ProgressSpinner,
    JRButton,
    JRTextarea,
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
      conversationId: null,
      activeFilters: null,
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
        const field = this.$refs.inputEl;
        const node = field?.$el || field;
        node?.focus?.();
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
    onRemoveFilterChip(chip) {
      const message = messageForRemovedChip(chip);
      if (!message || this.status === 'loading') return;
      this.draft = message;
      this.submit();
    },
    onClearFilters() {
      if (this.status === 'loading') return;
      this.submitMessage('Start over.', { startOver: true });
    },
    async submit() {
      const message = String(this.draft || '').trim();
      if (!message || this.status === 'loading') return;
      this.draft = '';
      await this.submitMessage(message, {});
    },
    async submitMessage(message, options = {}) {
      const text = String(message || '').trim();
      if (!text || this.status === 'loading') return;

      this.lastUserMessage = text;
      this.messages.push({
        id: nextMsgId(),
        role: 'user',
        text,
      });
      this.status = 'loading';
      this.scrollToBottom();

      try {
        const data = await postQuery(text, this.pageContext || {}, {
          conversationId: this.conversationId,
          startOver: !!options.startOver,
        });
        const nextConversationId = data?.meta?.conversation_id;
        if (typeof nextConversationId === 'string' && nextConversationId) {
          this.conversationId = nextConversationId;
        }
        const nextFilters = data?.context?.active_filters || null;
        this.activeFilters = nextFilters;
        this.messages.push({
          id: nextMsgId(),
          role: 'assistant',
          text: typeof data?.message === 'string' ? data.message : '',
          blocks: Array.isArray(data?.blocks) ? data.blocks : [],
          sources: Array.isArray(data?.sources) ? data.sources : [],
          partial: !!(data?.meta && data.meta.partial),
          error: null,
          canRetry: false,
        });
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
  background: color-mix(in srgb, var(--color-jr-text) 35%, transparent);
  pointer-events: auto;
}

.assistant-panel {
  position: relative;
  display: flex;
  flex-direction: column;
  width: min(460px, 100%);
  max-width: 100%;
  height: 100%;
  background: var(--color-jr-surface);
  box-shadow: var(--shadow-jr-overlay);
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
  gap: 0.75rem;
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--color-jr-border);
  background: var(--color-jr-text);
  color: var(--color-jr-surface);
}

.assistant-panel__title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-surface);
}

.assistant-panel__context {
  font-size: 0.75rem;
  color: var(--color-jr-surface-muted);
  margin-top: 0.15rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 340px;
}

.assistant-panel__close {
  flex: 0 0 auto;
  border: 0;
  background: transparent;
  color: var(--color-jr-surface);
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.25rem 0.35rem;
}

.assistant-panel__close:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.assistant-panel__messages {
  flex: 1;
  overflow-y: auto;
  padding: 0.85rem 1rem;
  background: var(--color-jr-page);
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
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-info-subtle);
  border: 1px dashed var(--color-jr-border);
  text-align: left;
}

.assistant-followups__label {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-jr-muted);
}

.assistant-chip {
  text-align: left;
  border: 1px solid var(--color-jr-border);
  background: var(--color-jr-surface);
  color: var(--color-jr-primary);
  border-radius: var(--radius-jr-control);
  padding: 0.45rem 0.65rem;
  font-size: 0.8125rem;
  line-height: 1.3;
  cursor: pointer;
}

.assistant-chip:hover:not(:disabled) {
  background: var(--color-jr-surface-muted);
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
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface);
  border: 1px solid var(--color-jr-border);
}

.assistant-msg--user .assistant-msg__bubble {
  background: var(--color-jr-primary);
  color: var(--color-jr-surface);
  border-color: transparent;
  max-width: 92%;
}

.assistant-msg__text {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.9375rem;
  line-height: 1.4;
  margin-bottom: 0.25rem;
}

.assistant-msg--user .assistant-msg__text {
  margin-bottom: 0;
}

.assistant-msg__error {
  color: var(--color-jr-danger-text);
  background: var(--color-jr-danger-subtle);
  border-radius: var(--radius-jr-control);
  padding: 0.4rem 0.5rem;
  font-size: 0.75rem;
}

.assistant-loading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0;
}

.assistant-panel__footer {
  border-top: 1px solid var(--color-jr-border);
  padding: 0.65rem 0.75rem;
  background: var(--color-jr-surface);
}

.assistant-input-row {
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
}

.assistant-input {
  resize: none;
  flex: 1;
  min-width: 0;
}

.assistant-send {
  min-width: 4.25rem;
}
</style>
