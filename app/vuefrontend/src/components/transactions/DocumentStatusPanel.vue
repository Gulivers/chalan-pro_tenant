<template>
  <section v-if="showPanel" class="jr-doc-status-panel">
    <JRSection title="Status tracking">
      <p v-if="loading" class="jr-doc-status-panel__status" role="status">
        Loading status…
      </p>

      <template v-else>
        <p v-if="!tracking" class="jr-doc-status-panel__status" role="status">
          {{ emptyMessage }}
        </p>

        <template v-else>
          <DocumentStatusProgress
            stacked
            :statuses="workflowStatuses"
            :current-sequence="tracking.status_sequence" />

          <div
            v-if="canAdvance || canRevert"
            class="jr-doc-status-panel__actions">
            <JRButton
              v-if="canAdvance"
              type="button"
              :disabled="saving"
              @click="openConfirm('next')">
              Mark as {{ nextStatus.name }}
            </JRButton>
            <JRButton
              v-if="canRevert"
              type="button"
              variant="secondary"
              :disabled="saving"
              @click="openConfirm('previous')">
              Revert to {{ previousStatus.name }}
            </JRButton>
          </div>

          <p
            v-else-if="tracking.is_terminal"
            class="jr-doc-status-panel__status">
            This document has reached its final status.
          </p>

          <p
            v-if="error"
            class="jr-doc-status-panel__error"
            role="alert">
            {{ error }}
          </p>
        </template>
      </template>
    </JRSection>

    <JRSection v-if="tracking || history.length" title="Status History">
      <p v-if="historyLoading" class="jr-doc-status-panel__status" role="status">
        Loading history…
      </p>
      <JREmptyState
        v-else-if="!history.length"
        title="No status changes yet."
        description="Changes appear here when the document moves to another status." />
      <ol v-else class="jr-doc-status-panel__history">
        <li v-for="row in historyNewestFirst" :key="row.id">
          <strong>
            {{ row.from_status_name || 'New' }}
            →
            {{ row.to_status_name || row.to_status_code }}
          </strong>
          <span>
            {{ row.changed_by_username || '—' }}
            ·
            {{ formatWhen(row.changed_at) }}
          </span>
          <span v-if="row.notes">{{ row.notes }}</span>
        </li>
      </ol>
    </JRSection>

    <JRDialog
      :visible="confirmOpen"
      :header="confirmHeader"
      confirm-label="Confirm"
      cancel-label="Cancel"
      :confirm-disabled="saving || !pendingTarget"
      @update:visible="onConfirmVisible"
      @confirm="confirmTransition">
      <dl class="jr-doc-status-panel__confirm">
        <div>
          <dt>Current Status</dt>
          <dd>{{ tracking?.status_name || '—' }}</dd>
        </div>
        <div>
          <dt>{{ isRevert ? 'Revert to' : 'New Status' }}</dt>
          <dd>{{ pendingTarget?.name || '—' }}</dd>
        </div>
      </dl>
      <JRField label="Notes" inputId="doc-status-notes" hint="Optional">
        <JRTextarea
          inputId="doc-status-notes"
          v-model="transitionNotes"
          :rows="2"
          :disabled="saving"
          placeholder="Optional notes for this status change" />
      </JRField>
      <p
        v-if="confirmError"
        class="jr-doc-status-panel__error"
        role="alert">
        {{ confirmError }}
      </p>
    </JRDialog>
  </section>
</template>

<script>
import axios from 'axios';
import {
  JRButton,
  JRDialog,
  JREmptyState,
  JRField,
  JRSection,
  JRTextarea,
} from '@/ui';
import DocumentStatusProgress from './DocumentStatusProgress.vue';
import {
  formatStatusWhen,
  readApiError,
} from '@/utils/documentStatus';

export default {
  name: 'DocumentStatusPanel',
  components: {
    DocumentStatusProgress,
    JRButton,
    JRDialog,
    JREmptyState,
    JRField,
    JRSection,
    JRTextarea,
  },
  props: {
    documentId: {
      type: [Number, String],
      default: null,
    },
    documentTypeId: {
      type: [Number, String],
      default: null,
    },
    usesStatusTracking: {
      type: Boolean,
      default: false,
    },
    canTransition: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['update:tracking'],
  data() {
    return {
      tracking: null,
      workflowStatuses: [],
      history: [],
      loading: false,
      historyLoading: false,
      saving: false,
      error: '',
      confirmError: '',
      confirmOpen: false,
      transitionNotes: '',
      transitionDirection: null,
      alive: true,
      usesTrackingFlag: false,
    };
  },
  computed: {
    showPanel() {
      return !!(this.documentId && (this.usesStatusTracking || this.usesTrackingFlag || this.tracking));
    },
    emptyMessage() {
      if (this.usesStatusTracking || this.usesTrackingFlag) {
        return 'This document does not have a status assigned yet.';
      }
      return 'Status tracking is not enabled for this document type.';
    },
    nextStatus() {
      return this.tracking?.next_status || null;
    },
    previousStatus() {
      return this.tracking?.previous_status || null;
    },
    canAdvance() {
      return this.canTransition && !!this.nextStatus && !this.tracking?.is_terminal;
    },
    canRevert() {
      return this.canTransition && !!this.previousStatus;
    },
    isRevert() {
      return this.transitionDirection === 'previous';
    },
    pendingTarget() {
      return this.isRevert ? this.previousStatus : this.nextStatus;
    },
    confirmHeader() {
      return this.isRevert ? 'Revert Document Status' : 'Change Document Status';
    },
    historyNewestFirst() {
      return [...this.history].reverse();
    },
  },
  watch: {
    documentId: {
      immediate: true,
      handler() {
        this.reloadAll();
      },
    },
    documentTypeId() {
      this.loadWorkflow();
    },
    usesStatusTracking(value) {
      this.usesTrackingFlag = !!value;
    },
  },
  beforeUnmount() {
    this.alive = false;
  },
  methods: {
    formatWhen: formatStatusWhen,
    async reloadAll() {
      await Promise.all([this.loadTracking(), this.loadHistory(), this.loadWorkflow()]);
    },
    async loadTracking() {
      if (!this.documentId) {
        this.tracking = null;
        this.$emit('update:tracking', null);
        return;
      }
      const documentId = this.documentId;
      this.loading = true;
      this.error = '';
      try {
        const { data } = await axios.get(`/api/documents/${documentId}/status/`);
        if (!this.alive || documentId !== this.documentId) return;
        this.tracking = data;
        this.usesTrackingFlag = true;
        this.$emit('update:tracking', data);
      } catch (err) {
        if (!this.alive || documentId !== this.documentId) return;
        this.tracking = null;
        const payload = err?.response?.data || {};
        if (err?.response?.status === 404) {
          this.usesTrackingFlag = !!payload.uses_status_tracking;
          this.$emit('update:tracking', null);
          return;
        }
        this.error = readApiError(err, 'Could not load document status.');
        this.$emit('update:tracking', null);
      } finally {
        if (this.alive && documentId === this.documentId) this.loading = false;
      }
    },
    async loadHistory() {
      if (!this.documentId) {
        this.history = [];
        return;
      }
      const documentId = this.documentId;
      this.historyLoading = true;
      try {
        const { data } = await axios.get(
          `/api/documents/${documentId}/status-history/`
        );
        if (!this.alive || documentId !== this.documentId) return;
        this.history = Array.isArray(data) ? data : data?.results || [];
      } catch {
        if (!this.alive || documentId !== this.documentId) return;
        this.history = [];
      } finally {
        if (this.alive && documentId === this.documentId) {
          this.historyLoading = false;
        }
      }
    },
    async loadWorkflow() {
      if (!this.documentTypeId) {
        this.workflowStatuses = [];
        return;
      }
      const typeId = this.documentTypeId;
      try {
        const { data } = await axios.get('/api/document-statuses/', {
          params: {
            document_type: typeId,
            is_active: true,
          },
        });
        if (!this.alive || typeId !== this.documentTypeId) return;
        const list = Array.isArray(data) ? data : data?.results || [];
        this.workflowStatuses = [...list].sort(
          (a, b) => Number(a.sequence) - Number(b.sequence)
        );
      } catch {
        if (!this.alive || typeId !== this.documentTypeId) return;
        this.workflowStatuses = [];
      }
    },
    openConfirm(direction) {
      const target =
        direction === 'previous' ? this.previousStatus : this.nextStatus;
      if (!target) return;
      this.transitionDirection = direction;
      this.confirmError = '';
      this.transitionNotes = '';
      this.confirmOpen = true;
    },
    onConfirmVisible(visible) {
      this.confirmOpen = visible;
      if (!visible) this.transitionDirection = null;
    },
    async confirmTransition() {
      if (!this.documentId || !this.pendingTarget || this.saving) return;
      const expectedCode = this.tracking?.status_code;
      const targetCode = this.pendingTarget.code;
      this.saving = true;
      this.confirmError = '';
      this.error = '';
      try {
        const { data } = await axios.post(
          `/api/documents/${this.documentId}/transition-status/`,
          {
            status_code: targetCode,
            notes: this.transitionNotes || '',
          }
        );
        if (!this.alive) return;
        this.tracking = data;
        this.$emit('update:tracking', data);
        this.confirmOpen = false;
        this.transitionDirection = null;
        this.transitionNotes = '';
        await this.loadHistory();
      } catch (err) {
        if (!this.alive) return;
        this.confirmError = readApiError(
          err,
          'Could not change the document status.'
        );
        // Refresh if another user moved the document meanwhile.
        await this.loadTracking();
        if (
          this.tracking &&
          expectedCode &&
          this.tracking.status_code !== expectedCode
        ) {
          this.confirmError =
            'The status changed while this page was open. The latest status is shown.';
          this.confirmOpen = false;
          this.transitionDirection = null;
          await this.loadHistory();
        }
      } finally {
        if (this.alive) this.saving = false;
      }
    },
  },
};
</script>

<style scoped>
.jr-doc-status-panel {
  display: grid;
  gap: 1rem;
}

.jr-doc-status-panel__status {
  margin: 0.75rem 0 0;
  font-size: 0.8125rem;
  line-height: 1.4;
  color: var(--color-jr-muted);
}

.jr-doc-status-panel__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 1rem;
}

.jr-doc-status-panel__error {
  margin: 0.75rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-jr-danger, #dc2626);
}

.jr-doc-status-panel__history {
  margin: 0;
  padding: 0;
  list-style: none;
}

.jr-doc-status-panel__history li {
  display: grid;
  gap: 0.15rem;
  padding: 0.65rem 0;
  border-bottom: 1px solid var(--color-jr-border);
  font-size: 0.875rem;
}

.jr-doc-status-panel__history li:last-child {
  border-bottom: 0;
}

.jr-doc-status-panel__history span {
  color: var(--color-jr-muted);
  font-size: 0.8125rem;
}

.jr-doc-status-panel__confirm {
  display: grid;
  gap: 0.75rem;
  margin: 0 0 1rem;
}

.jr-doc-status-panel__confirm div {
  display: grid;
  gap: 0.2rem;
}

.jr-doc-status-panel__confirm dt {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-jr-muted);
}

.jr-doc-status-panel__confirm dd {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text);
}
</style>
