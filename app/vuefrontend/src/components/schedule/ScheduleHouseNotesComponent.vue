<template>
  <div class="house-notes-container">
    <h4 class="text-center mb-3">House Notes</h4>
    <div ref="quillEditor" class="quill-editor"></div>

    <div class="d-flex justify-content-between align-items-center flex-wrap mt-3">
      <div class="status-buttons" v-if="showEditor">
        <button class="btn btn-outline-success btn-sm me-1 mb-1" @click="insertEmoji('✅')">Mark as Done ✅</button>
        <button class="btn btn-outline-info btn-sm me-1 mb-1" @click="insertEmoji('😃')">Completed 😃</button>
        <button class="btn btn-outline-warning btn-sm me-1 mb-1" @click="insertEmoji('⚠️')">Alert ⚠️</button>
        <button class="btn btn-outline-danger btn-sm me-1 mb-1" @click="insertEmoji('⏳')">Delayed ⏳</button>
        <button class="btn btn-outline-dark btn-sm me-1 mb-1" @click="insertEmoji('🔥')">Critical 🔥</button>
      </div>
      <button class="btn btn-primary mt-2" @click="saveNote" :disabled="!showEditor">💾 Save Note</button>
    </div>
  </div>
</template>

<script>
  import Quill from 'quill';
  import 'quill/dist/quill.snow.css';
  import axios from 'axios';

  export default {
    props: {
      eventId: Number, // Event object received from ScheduleEventModal
      required: true,
    },
    data() {
      return {
        websocket: null,
        wsUrl: null,
        showEditor: null,
        lastSavedHTML: '',
        workAccountId: null,
      };
    },
    async mounted() {
      this.showEditor = this.hasPermission('appschedule.add_eventnote');
      this.checkUserIdentity();
      // Quill
      this.quill = new Quill(this.$refs.quillEditor, {
        theme: 'snow',
        placeholder: 'Write notes about the construction...',
      });

      // Obtener work_account_id del evento
      await this.loadWorkAccountId();
      
      // WebSocket + carga inicial (usar work_account si está disponible)
      if (this.workAccountId) {
        this.wsUrl = this.buildWsUrl(`ws/schedule/work-account/${this.workAccountId}/notes/`);
      } else {
        // Fallback a event_id si no hay work_account
        this.wsUrl = this.buildWsUrl(`ws/schedule/event/${this.$props.eventId}/`);
      }
      this.connectWebSocket();
      this.getNote();

      if (!this.showEditor) {
        this.quill.root.dataset.placeholder = '';
        this.quill.enable(false);
      }
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
      // Insertar emojis en el cursor actual
      insertEmoji(emoji) {
        const sel = this.quill.getSelection();
        const pos = (sel && sel.index) ?? this.quill.getLength();
        this.quill.insertText(pos, ` ${emoji} `, 'user');
      },

      // Firma (usuario + timestamp) al final del documento
      insertSignature() {
        const now = new Date();
        const ts = now.toLocaleString(undefined, {
          year: 'numeric',
          month: 'short',
          day: 'numeric',
          hour: 'numeric',
          minute: '2-digit',
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

        // Evitar firma duplicada inmediata
        if (!currentHTML.endsWith(signatureHTML)) {
          // Si no termina en bloque, agrega salto
          if (!currentHTML.endsWith('</p>') && !currentHTML.endsWith('</div>')) {
            this.quill.insertText(this.quill.getLength() - 1, '\n', 'user');
          }
          const range = this.quill.getSelection();
          this.quill.setSelection(this.quill.getLength(), 0);
          this.quill.clipboard.dangerouslyPasteHTML(this.quill.getLength(), signatureHTML);
          if (range) this.quill.setSelection(range.index, range.length);
        }
      },

      async saveNote() {
        if (!this.showEditor) return;

        const currentHTMLBefore = this.quill.root.innerHTML.trim();
        if (currentHTMLBefore === this.lastSavedHTML) {
          this.notifyToastSuccess?.('Nothing changed.');
          return;
        }

        // Inserta firma y guarda
        this.insertSignature();
        const notesContent = this.quill.root.innerHTML.trim();

        const ok = await this.postNote({
          notes: notesContent,
        });
        if (!ok) {
          this.notifyError?.('Could not save message');
          return;
        }

        this.lastSavedHTML = notesContent;
        this.notifyToastSuccess?.('Note saved with signature.');
      },

      connectWebSocket() {
        if (!this.wsUrl) {
          console.warn('WebSocket URL no configurada (Notes); se omite la conexión.');
          return;
        }
        this.websocket = new WebSocket(this.wsUrl);
        this.websocket.onmessage = event => {
          const data = JSON.parse(event.data);
          if (data.type === 'note.updated') {
            this.quill.root.innerHTML = data.event.notes;
            this.lastSavedHTML = data.event.notes?.trim() || '';
            if (this.showEditor) this.notifyToastSuccess?.('Message has been updated successfully');
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
          const { data, status } = await axios.get(`/api/events/${this.$props.eventId}/note/`);
          if (status === 200) {
            this.quill.root.innerHTML = data.notes || '';
            this.lastSavedHTML = (data.notes || '').trim();
          }
        } catch (e) {
          console.error('Error fetching notes data:', e);
        }
      },

      async postNote(payload) {
        try {
          // El backend ahora usa work_account internamente, así que solo necesitamos enviar notes
          const resp = await axios.post(`/api/events/${this.$props.eventId}/note/`, payload);
          return [200, 201].includes(resp.status);
        } catch (e) {
          console.error('Error saving note:', e);
          return false;
        }
      },
      checkUserIdentity() {
        const token = localStorage.getItem('authToken');
        this.isLoggedIn = !!token;
        if (this.isLoggedIn) {
          this.getAuthenticatedUser().then(user => {
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
  .house-notes-container {
    padding: 1rem;
  }

  .quill-editor {
    min-height: max(300px, 40vh);
    border: 1px solid #ccc;
    padding: 10px;
    border-radius: 5px;
    background-color: white;
  }

  .status-buttons {
    margin-bottom: 10px;
  }

  .status-buttons button {
    margin: 5px;
    font-size: 0.75rem;
    padding: 0.25rem 0.5rem;
  }
</style>
