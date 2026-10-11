<template>
  <div class="jr-pilot jr-house-notes">
    <div class="jr-house-notes__header">
      <h3 class="jr-house-notes__title">House Notes</h3>
      <span class="jr-house-notes__hint">Shared notes for crews and supervisors</span>
    </div>

    <JRScrollArea class="jr-house-notes__scroll" height="var(--jr-wov-body-height, 22rem)">
      <div ref="quillEditor" class="jr-house-notes__editor"></div>
    </JRScrollArea>

    <div class="jr-house-notes__footer">
      <div v-if="showEditor" class="jr-house-notes__status">
        <span class="jr-house-notes__status-label">Quick status:</span>
        <button
          type="button"
          class="jr-house-notes__tag jr-house-notes__tag--done"
          @click="insertEmoji('✅')">
          <span aria-hidden="true">✅</span> Mark as Done
        </button>
        <button
          type="button"
          class="jr-house-notes__tag jr-house-notes__tag--completed"
          @click="insertEmoji('😃')">
          <span aria-hidden="true">😃</span> Completed
        </button>
        <button
          type="button"
          class="jr-house-notes__tag jr-house-notes__tag--alert"
          @click="insertEmoji('⚠️')">
          <span aria-hidden="true">⚠️</span> Alert
        </button>
        <button
          type="button"
          class="jr-house-notes__tag jr-house-notes__tag--delayed"
          @click="insertEmoji('⏳')">
          <span aria-hidden="true">⏳</span> Delayed
        </button>
        <button
          type="button"
          class="jr-house-notes__tag jr-house-notes__tag--critical"
          @click="insertEmoji('🔥')">
          <span aria-hidden="true">🔥</span> Critical
        </button>
      </div>
      <div class="jr-house-notes__actions">
        <JRButton
          type="button"
          size="sm"
          :disabled="!showEditor"
          @click="saveNote">
          Save Note
        </JRButton>
      </div>
    </div>
  </div>
</template>

<script>
import { getAccessToken } from '@/auth/tokenHelpers';
import Quill from "quill";
import "quill/dist/quill.snow.css";
import axios from "axios";
import { JRButton, JRScrollArea } from "@ui";

export default {
  name: "ScheduleHouseNotesComponent",
  components: {
    JRButton,
    JRScrollArea,
  },
  props: {
    eventId: Number,
    workAccountId: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      websocket: null,
      wsUrl: null,
      showEditor: null,
      lastSavedHTML: "",
      resolvedWorkAccountId: null,
    };
  },
  async mounted() {
    this.showEditor = this.hasPermission("appschedule.add_eventnote");
    this.checkUserIdentity();
    this.quill = new Quill(this.$refs.quillEditor, {
      theme: "snow",
      placeholder: "Write notes about the construction...",
    });

    await this.loadWorkAccountId();

    this.wsUrl = this.buildWsUrl(
      `ws/schedule/event/${this.$props.eventId}/`
    );
    this.connectWebSocket();
    this.getNote();

    if (!this.showEditor) {
      this.quill.root.dataset.placeholder = "";
      this.quill.enable(false);
    }
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
    insertEmoji(emoji) {
      const sel = this.quill.getSelection();
      const pos = (sel && sel.index) ?? this.quill.getLength();
      this.quill.insertText(pos, ` ${emoji} `, "user");
    },

    insertSignature() {
      const now = new Date();
      const ts = now.toLocaleString(undefined, {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit",
      });

      const signatureHTML = `
        <p class="note-stamp" contenteditable="false">
          📝&nbsp;
          <small>${this.userName}: ${ts}</small>
        <p>&nbsp;</p>
        <p>&nbsp;</p>
      `.trim();

      const root = this.quill.root;
      const currentHTML = root.innerHTML.trim();

      if (!currentHTML.endsWith(signatureHTML)) {
        if (!currentHTML.endsWith("</p>") && !currentHTML.endsWith("</div>")) {
          this.quill.insertText(this.quill.getLength() - 1, "\n", "user");
        }
        const range = this.quill.getSelection();
        this.quill.setSelection(this.quill.getLength(), 0);
        this.quill.clipboard.dangerouslyPasteHTML(
          this.quill.getLength(),
          signatureHTML
        );
        if (range) this.quill.setSelection(range.index, range.length);
      }
    },

    async saveNote() {
      if (!this.showEditor) return;

      const currentHTMLBefore = this.quill.root.innerHTML.trim();
      if (currentHTMLBefore === this.lastSavedHTML) {
        this.notifyToastSuccess?.("Nothing changed.");
        return;
      }

      if (!this.resolvedWorkAccountId) {
        await this.loadWorkAccountId();
      }
      if (!this.resolvedWorkAccountId) {
        this.notifyError?.(
          "Could not save note: this work order has no work account."
        );
        return;
      }

      this.insertSignature();
      const notesContent = this.quill.root.innerHTML.trim();

      const ok = await this.postNote({
        notes: notesContent,
        work_account: this.resolvedWorkAccountId,
      });
      if (!ok) {
        this.notifyError?.("Could not save message");
        return;
      }

      this.lastSavedHTML = notesContent;
      this.notifyToastSuccess?.("Note saved with signature.");
    },

    connectWebSocket() {
      if (!this.wsUrl) {
        console.warn(
          "WebSocket URL no configurada (Notes); se omite la conexión."
        );
        return;
      }
      this.websocket = new WebSocket(this.wsUrl);
      this.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "note.updated") {
          this.quill.root.innerHTML = data.event.notes;
          this.lastSavedHTML = data.event.notes?.trim() || "";
          if (this.showEditor)
            this.notifyToastSuccess?.(
              "Message has been updated successfully"
            );
        }
      };
    },

    disconnectWebSocket() {
      if (this.websocket) {
        this.websocket.close();
        this.websocket = null;
      }
    },

    async getNote() {
      try {
        const { data, status } = await axios.get(
          `/api/events/${this.$props.eventId}/note/`
        );
        if (status === 200) {
          this.quill.root.innerHTML = data.notes || "";
          this.lastSavedHTML = (data.notes || "").trim();
        }
      } catch (e) {
        console.error("Error fetching notes data:", e);
      }
    },

    async postNote(payload) {
      try {
        const resp = await axios.post(
          `/api/events/${this.$props.eventId}/note/`,
          payload
        );
        return [200, 201].includes(resp.status);
      } catch (e) {
        const apiError =
          e?.response?.data?.error ||
          e?.response?.data?.work_account?.[0] ||
          e?.response?.data?.detail;
        console.error("Error saving note:", e?.response?.data || e);
        if (apiError) {
          this.notifyError?.(
            typeof apiError === "string" ? apiError : "Could not save note."
          );
        }
        return false;
      }
    },
    checkUserIdentity() {
      const token = getAccessToken();
      this.isLoggedIn = !!token;
      if (this.isLoggedIn) {
        this.getAuthenticatedUser().then((user) => {
          if (user) {
            this.userName = user.username;
          }
        });
      }
    },
  },
};
</script>

<style scoped>
.jr-house-notes {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  min-height: 0;
  height: 100%;
}

.jr-house-notes__header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
  flex: 0 0 auto;
}

.jr-house-notes__title {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text, #111827);
  text-align: left;
}

.jr-house-notes__hint {
  font-size: 0.75rem;
  color: var(--color-jr-muted, #4b5563);
}

.jr-house-notes__scroll {
  flex: 1 1 auto;
  min-height: 0;
}

.jr-house-notes__scroll :deep(.jr-scroll-area) {
  border-color: var(--color-jr-border, #e5e7eb);
}

.jr-house-notes__editor {
  min-height: 100%;
  border: none;
  background-color: var(--color-jr-surface, #fff);
  overflow: visible;
}

.jr-house-notes__editor :deep(.ql-toolbar.ql-snow) {
  border: none;
  border-bottom: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface-muted, #f9fafb);
  padding: 0.5rem 0.75rem;
  font-family: var(--font-jr-sans, sans-serif);
  position: sticky;
  top: 0;
  z-index: 1;
}

.jr-house-notes__editor :deep(.ql-container.ql-snow) {
  border: none;
  font-family: var(--font-jr-sans, sans-serif);
  font-size: 0.9375rem;
  color: var(--color-jr-text, #111827);
}

.jr-house-notes__editor :deep(.ql-editor) {
  min-height: 16rem;
  padding: 1rem 1.125rem;
  line-height: 1.55;
}

.jr-house-notes__editor :deep(.note-stamp) {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  margin-top: 0.5rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-control, 0);
  background: var(--color-jr-surface-muted, #f9fafb);
  color: var(--color-jr-muted, #4b5563);
  font-size: 0.75rem;
}

.jr-house-notes__footer {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 0.75rem;
  flex: 0 0 auto;
}

.jr-house-notes__actions {
  display: flex;
  justify-content: stretch;
}

.jr-house-notes__actions :deep(.jr-button),
.jr-house-notes__actions :deep(.p-button) {
  width: 100%;
  min-height: 2.75rem;
}

.jr-house-notes__tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  min-height: 2.25rem;
  padding: 0.375rem 0.625rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-control, 0);
  background: var(--color-jr-surface, #fff);
  color: var(--color-jr-text, #111827);
  font-family: var(--font-jr-sans, sans-serif);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease;
}

.jr-house-notes__tag:hover {
  background: var(--color-jr-surface-muted, #f9fafb);
  border-color: var(--color-jr-hover-border, #d1d5db);
}

.jr-house-notes__tag:focus-visible {
  outline: 2px solid var(--color-jr-primary, #2563eb);
  outline-offset: 1px;
}

.jr-house-notes__status {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.375rem;
}

.jr-house-notes__status-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-jr-muted, #4b5563);
  margin-right: 0.125rem;
}

@media (min-width: 769px) {
  .jr-house-notes__footer {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }

  .jr-house-notes__actions {
    justify-content: flex-end;
  }

  .jr-house-notes__actions :deep(.jr-button),
  .jr-house-notes__actions :deep(.p-button) {
    width: auto;
    min-height: 0;
  }

  .jr-house-notes__tag {
    min-height: 0;
    padding: 0.25rem 0.5rem;
  }
}
</style>
