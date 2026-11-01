<template>
  <div class="jr-wo-status">
    <p v-if="loading" class="jr-wo-status__muted" role="status">
      Loading status and progress…
    </p>

    <JREmptyState
      v-else-if="notApplicable"
      title="Status does not apply here"
      description="This entry is not an active work order, so it has no status or progress checklist." />

    <JREmptyState
      v-else-if="forbidden"
      title="You cannot view work order status"
      description="You do not have permission to view the status and progress of this work order. The rest of this viewer still works." />

    <template v-else-if="tracking">
      <JRSection title="Work Order Status">
        <template #actions>
          <JRButton
            type="button"
            variant="ghost"
            size="sm"
            :disabled="loading || savingTransition"
            @click="reloadAll">
            Refresh
          </JRButton>
        </template>

        <div class="jr-wo-status__current">
          <div class="jr-wo-status__current-main">
            <span class="jr-wo-status__label">Current status</span>
            <div class="jr-wo-status__current-row">
              <strong class="jr-wo-status__current-name">{{ tracking.status_name }}</strong>
              <JRBadge
                :value="tracking.is_terminal ? 'Closed' : 'Active'"
                :severity="currentSeverity" />
            </div>
            <p v-if="statusMeta" class="jr-wo-status__meta">{{ statusMeta }}</p>
            <p v-if="tracking.notes" class="jr-wo-status__meta">
              Note: {{ tracking.notes }}
            </p>
          </div>
        </div>

        <div v-if="allStatuses.length" class="jr-wo-status__actions">
          <span class="jr-wo-status__label" id="wo-status-group-label">Work order status</span>
          <div
            class="jr-wo-status__action-row"
            role="group"
            aria-labelledby="wo-status-group-label">
            <JRButton
              v-for="target in allStatuses"
              :key="target.code"
              type="button"
              :variant="target.isCurrent ? 'primary' : 'secondary'"
              size="sm"
              :class="{ 'jr-wo-status__status-btn--current': target.isCurrent }"
              :disabled="target.isCurrent || !canChange || savingTransition || savingCheckId !== null"
              :aria-current="target.isCurrent ? 'true' : undefined"
              :title="target.isCurrent ? 'Current status' : undefined"
              @click="openConfirm(target)">
              {{ target.name }}{{ target.isCurrent ? ' · Current' : '' }}
            </JRButton>
          </div>
        </div>
        <p v-if="tracking.is_terminal" class="jr-wo-status__muted">
          This work order is closed.
          <template v-if="!canChange">Ask a supervisor if it needs to reopen.</template>
        </p>
        <p v-else-if="!canChange" class="jr-wo-status__muted">
          You can view this status, but you do not have permission to change it.
        </p>

        <p v-if="error" class="jr-wo-status__error" role="alert">{{ error }}</p>
      </JRSection>

      <JRSection title="Progress Checklist">
        <div v-if="progress.length" class="jr-wo-status__progress-head">
          <p class="jr-wo-status__count" role="status">
            {{ doneCount }} of {{ progress.length }} progress items done
          </p>
          <div
            class="jr-wo-status__bar"
            role="progressbar"
            :aria-valuenow="doneCount"
            :aria-valuemin="0"
            :aria-valuemax="progress.length"
            aria-label="Progress items completed">
            <span :style="{ width: `${progressPercent}%` }" />
          </div>
        </div>
        <div
          v-if="progress.length && (missingForInspection.length || missingForCompletion.length)"
          class="jr-wo-status__needed-group">
          <p v-if="missingForInspection.length" class="jr-wo-status__needed">
            <strong>Still needed before inspection:</strong>
            {{ namesOf(missingForInspection) }}
          </p>
          <p v-if="missingForCompletion.length" class="jr-wo-status__needed">
            <strong>Still needed before closing:</strong>
            {{ namesOf(missingForCompletion) }}
          </p>
        </div>
        <p v-if="progressLoading" class="jr-wo-status__muted" role="status">
          Loading checklist…
        </p>
        <JREmptyState
          v-else-if="!progress.length"
          title="No checklist for this work order"
          description="There is no progress checklist for this crew category yet. Status changes still work; an admin can add a checklist in Django Admin." />
        <ol v-else class="jr-wo-status__checks">
          <li
            v-for="check in sortedProgress"
            :key="check.id"
            class="jr-wo-status__check"
            :class="{ 'jr-wo-status__check--done': check.is_done }">
            <JRCheckbox
              :inputId="`wo-progress-${check.id}`"
              :modelValue="!!check.is_done"
              :ariaLabel="`Mark ${check.item_name} as done`"
              :disabled="!canChange || savingCheckId !== null || savingTransition"
              @update:modelValue="toggleCheck(check, $event)" />
            <div class="jr-wo-status__check-main">
              <span class="jr-wo-status__check-name">{{ check.item_name }}</span>
              <span class="jr-wo-status__meta">
                <template v-if="check.is_done">
                  Done<template v-if="check.completed_by_username">
                    by {{ check.completed_by_username }}</template><template v-if="check.completed_at">
                    · {{ formatWhen(check.completed_at) }}</template>
                </template>
                <template v-else>Pending</template>
                <template v-if="check.notes"> · {{ check.notes }}</template>
              </span>
            </div>
            <div class="jr-wo-status__badges">
              <JRBadge v-if="check.is_done" value="Done" severity="success" />
              <template v-else>
                <JRBadge
                  v-if="check.is_required_for_inspection"
                  value="Needed for inspection"
                  severity="warning" />
                <JRBadge
                  v-if="check.is_required_for_completion"
                  value="Needed to close"
                  severity="info" />
                <JRBadge
                  v-if="check.is_informational"
                  value="For reference"
                  severity="secondary" />
                <JRBadge
                  v-if="!check.is_required_for_inspection && !check.is_required_for_completion && !check.is_informational"
                  value="Optional"
                  severity="secondary" />
              </template>
            </div>
          </li>
        </ol>
        <p v-if="progressError" class="jr-wo-status__error" role="alert">
          {{ progressError }}
        </p>

        <Message
          v-if="materialHint"
          severity="info"
          :closable="false"
          class="jr-wo-status__message">
          {{ materialHint }}
        </Message>
      </JRSection>

      <JRSection title="Status History">
        <template #actions>
          <JRButton
            type="button"
            variant="ghost"
            size="sm"
            :aria-expanded="historyOpen ? 'true' : 'false'"
            @click="historyOpen = !historyOpen">
            {{ historyOpen ? 'Hide' : 'Show' }}
          </JRButton>
        </template>
        <template v-if="historyOpen">
          <p v-if="historyLoading" class="jr-wo-status__muted" role="status">
            Loading history…
          </p>
          <JREmptyState
            v-else-if="!history.length"
            title="No status changes yet"
            description="Changes appear here when this work order moves to another status." />
          <ol v-else class="jr-wo-status__history">
            <li v-for="row in historyNewestFirst" :key="row.id">
              <strong>
                {{ row.from_status_name || 'New' }} → {{ row.to_status_name || row.to_status_code }}
              </strong>
              <span>
                {{ row.changed_by_username || '—' }} · {{ formatWhen(row.changed_at) }}
              </span>
              <span v-if="row.notes">{{ row.notes }}</span>
            </li>
          </ol>
        </template>
        <p v-else class="jr-wo-status__muted">
          {{ history.length }} change{{ history.length === 1 ? '' : 's' }} recorded.
        </p>
      </JRSection>
    </template>

    <JREmptyState
      v-else-if="error"
      title="Status could not be loaded"
      :description="error" />

    <JRDialog
      :visible="confirmOpen"
      header="Change Work Order Status"
      confirm-label="Save status"
      cancel-label="Cancel"
      :confirm-disabled="savingTransition || !pendingTarget"
      @update:visible="onConfirmVisible"
      @confirm="confirmTransition">
      <dl class="jr-wo-status__confirm">
        <div>
          <dt>Current status</dt>
          <dd>{{ tracking?.status_name || '—' }}</dd>
        </div>
        <div>
          <dt>New status</dt>
          <dd>{{ pendingTarget?.name || '—' }}</dd>
        </div>
      </dl>

      <Message
        v-if="pendingMissing.length"
        severity="warn"
        :closable="false"
        class="jr-wo-status__message">
        Before this change can be saved, these progress items still need to be done:
        <ul class="jr-wo-status__missing">
          <li v-for="item in pendingMissing" :key="item.code || item.name">{{ item.name }}</li>
        </ul>
        You can go back and check them off in the Progress Checklist.
      </Message>

      <JRField label="Notes" inputId="wo-status-notes" hint="Optional">
        <JRTextarea
          inputId="wo-status-notes"
          v-model="transitionNotes"
          :rows="2"
          :disabled="savingTransition"
          placeholder="Optional note for this status change" />
      </JRField>

      <div v-if="confirmError" class="jr-wo-status__confirm-error" role="alert">
        <p>{{ confirmError }}</p>
        <ul v-if="confirmMissing.length" class="jr-wo-status__missing">
          <li v-for="item in confirmMissing" :key="item.code || item.name">{{ item.name }}</li>
        </ul>
      </div>
    </JRDialog>
  </div>
</template>

<script>
import axios from 'axios';
import Message from 'primevue/message';
import {
  JRButton,
  JRCheckbox,
  JRDialog,
  JREmptyState,
  JRField,
  JRBadge,
  JRSection,
  JRTextarea,
} from '@/ui';
import {
  formatStatusWhen,
  missingRequirementsFromError,
  readWorkOrderError,
  workOrderStatusSeverity,
} from '@/utils/workOrderStatus';

export default {
  name: 'WorkOrderStatusPanel',
  components: {
    JRButton,
    JRCheckbox,
    JRDialog,
    JREmptyState,
    JRField,
    JRBadge,
    JRSection,
    JRTextarea,
    Message,
  },
  props: {
    eventId: {
      type: [Number, String],
      default: null,
    },
  },
  emits: ['status-changed', 'progress-changed'],
  data() {
    return {
      tracking: null,
      progress: [],
      history: [],
      materialSuggestions: null,
      loading: false,
      progressLoading: false,
      historyLoading: false,
      savingTransition: false,
      savingCheckId: null,
      error: '',
      progressError: '',
      notApplicable: false,
      forbidden: false,
      historyOpen: false,
      confirmOpen: false,
      pendingTarget: null,
      transitionNotes: '',
      confirmError: '',
      confirmMissing: [],
      alive: true,
    };
  },
  computed: {
    canView() {
      return !!this.hasPermission?.('appschedule.view_event');
    },
    canChange() {
      return !!this.hasPermission?.('appschedule.change_event');
    },
    currentSeverity() {
      return workOrderStatusSeverity(this.tracking);
    },
    allowedStatuses() {
      return Array.isArray(this.tracking?.allowed_statuses)
        ? this.tracking.allowed_statuses
        : [];
    },
    /** Current status + every allowed target, in workflow sequence order. */
    allStatuses() {
      if (!this.tracking) return [];
      const current = {
        code: this.tracking.status_code,
        name: this.tracking.status_name,
        sequence: this.tracking.status_sequence,
        is_terminal: !!this.tracking.is_terminal,
        requires_inspection_ready: !!this.tracking.requires_inspection_ready,
        requires_completion_ready: !!this.tracking.requires_completion_ready,
        isCurrent: true,
      };
      const targets = this.allowedStatuses.map((status) => ({
        ...status,
        isCurrent: false,
      }));
      return [current, ...targets].sort(
        (a, b) => Number(a.sequence || 0) - Number(b.sequence || 0),
      );
    },
    missingForInspection() {
      return this.tracking?.missing_for_inspection || [];
    },
    missingForCompletion() {
      return this.tracking?.missing_for_completion || [];
    },
    sortedProgress() {
      return [...this.progress].sort(
        (a, b) => Number(a.item_sequence) - Number(b.item_sequence),
      );
    },
    doneCount() {
      return this.progress.filter((check) => check.is_done).length;
    },
    progressPercent() {
      if (!this.progress.length) return 0;
      return Math.round((this.doneCount / this.progress.length) * 100);
    },
    statusMeta() {
      if (!this.tracking?.status_changed_at) return '';
      const who = this.tracking.changed_by_username;
      return `Since ${formatStatusWhen(this.tracking.status_changed_at)}${who ? ` · by ${who}` : ''}`;
    },
    historyNewestFirst() {
      return [...this.history].reverse();
    },
    pendingMissing() {
      if (!this.pendingTarget) return [];
      if (this.pendingTarget.requires_inspection_ready) {
        return this.missingForInspection;
      }
      if (this.pendingTarget.requires_completion_ready || this.pendingTarget.is_terminal) {
        return this.missingForCompletion;
      }
      return [];
    },
    materialHint() {
      const docs = this.materialSuggestions?.documents;
      if (!Array.isArray(docs) || !docs.length) return '';
      const pendingDelivery = this.progress.some(
        (check) => check.item_code === 'material_delivered' && !check.is_done,
      );
      if (!pendingDelivery) return '';
      return (
        'Related transaction documents exist for this work order. ' +
        'They are shown for reference only — please confirm material delivery manually by checking “Material Delivered” above.'
      );
    },
  },
  watch: {
    eventId: {
      immediate: true,
      handler() {
        this.reloadAll();
      },
    },
  },
  beforeUnmount() {
    this.alive = false;
  },
  methods: {
    formatWhen: formatStatusWhen,
    namesOf(list) {
      return (list || []).map((item) => item.name || item.code).filter(Boolean).join(', ');
    },
    async reloadAll() {
      this.tracking = null;
      this.progress = [];
      this.history = [];
      this.materialSuggestions = null;
      this.notApplicable = false;
      this.forbidden = false;
      this.error = '';
      this.progressError = '';
      if (!this.eventId) return;
      const ok = await this.loadStatus();
      if (!ok || !this.alive) return;
      await Promise.all([
        this.loadProgress(),
        this.loadHistory(),
        this.loadMaterialSuggestions(),
      ]);
    },
    async loadStatus() {
      if (!this.eventId) return false;
      const eventId = this.eventId;
      this.loading = true;
      try {
        const { data } = await axios.get(`/api/events/${eventId}/work-order-status/`);
        if (!this.alive || eventId !== this.eventId) return false;
        this.tracking = data;
        return true;
      } catch (err) {
        if (!this.alive || eventId !== this.eventId) return false;
        const statusCode = err?.response?.status;
        if (statusCode === 404) {
          this.notApplicable = true;
        } else if (statusCode === 403) {
          this.forbidden = true;
        } else {
          this.error = readWorkOrderError(err, 'Could not load the work order status.');
        }
        return false;
      } finally {
        if (this.alive && eventId === this.eventId) this.loading = false;
      }
    },
    async loadProgress() {
      if (!this.eventId) return;
      const eventId = this.eventId;
      this.progressLoading = true;
      this.progressError = '';
      try {
        const { data } = await axios.get(`/api/events/${eventId}/work-order-progress/`);
        if (!this.alive || eventId !== this.eventId) return;
        this.progress = Array.isArray(data) ? data : data?.results || [];
      } catch (err) {
        if (!this.alive || eventId !== this.eventId) return;
        if (err?.response?.status === 403) {
          this.progressError =
            'You do not have permission to view the progress checklist.';
        } else if (err?.response?.status !== 404) {
          this.progressError = readWorkOrderError(err, 'Could not load the progress checklist.');
        }
      } finally {
        if (this.alive && eventId === this.eventId) this.progressLoading = false;
      }
    },
    async loadHistory() {
      if (!this.eventId) return;
      const eventId = this.eventId;
      this.historyLoading = true;
      try {
        const { data } = await axios.get(
          `/api/events/${eventId}/work-order-status/history/`,
        );
        if (!this.alive || eventId !== this.eventId) return;
        this.history = Array.isArray(data) ? data : data?.results || [];
      } catch {
        if (!this.alive || eventId !== this.eventId) return;
        this.history = [];
      } finally {
        if (this.alive && eventId === this.eventId) this.historyLoading = false;
      }
    },
    async loadMaterialSuggestions() {
      if (!this.eventId) return;
      const eventId = this.eventId;
      try {
        const { data } = await axios.get(
          `/api/events/${eventId}/work-order-progress/material-suggestions/`,
        );
        if (!this.alive || eventId !== this.eventId) return;
        this.materialSuggestions = data;
      } catch {
        if (this.alive && eventId === this.eventId) this.materialSuggestions = null;
      }
    },
    openConfirm(target) {
      if (!target || target.isCurrent) return;
      if (target.code && target.code === this.tracking?.status_code) return;
      this.pendingTarget = target;
      this.transitionNotes = '';
      this.confirmError = '';
      this.confirmMissing = [];
      this.confirmOpen = true;
    },
    onConfirmVisible(visible) {
      this.confirmOpen = visible;
      if (!visible) {
        this.pendingTarget = null;
        this.confirmError = '';
        this.confirmMissing = [];
      }
    },
    async confirmTransition() {
      if (!this.eventId || !this.pendingTarget || this.savingTransition) return;
      const target = this.pendingTarget;
      this.savingTransition = true;
      this.confirmError = '';
      this.confirmMissing = [];
      this.error = '';
      try {
        const { data } = await axios.post(
          `/api/events/${this.eventId}/work-order-status/transition/`,
          { status_code: target.code, notes: this.transitionNotes || '' },
        );
        if (!this.alive) return;
        this.tracking = data;
        this.confirmOpen = false;
        this.pendingTarget = null;
        this.transitionNotes = '';
        this.notifyToastSuccess?.(`Status changed to ${data.status_name}.`);
        this.$emit('status-changed', data);
        await this.loadHistory();
      } catch (err) {
        if (!this.alive) return;
        this.confirmMissing = missingRequirementsFromError(err);
        this.confirmError =
          err?.response?.status === 403
            ? 'You do not have permission to change the work order status.'
            : readWorkOrderError(err, 'Could not change the work order status.');
        await this.loadStatus();
      } finally {
        if (this.alive) this.savingTransition = false;
      }
    },
    async toggleCheck(check, isDone) {
      if (!this.eventId || !check?.id || this.savingCheckId !== null) return;
      this.savingCheckId = check.id;
      this.progressError = '';
      try {
        const { data } = await axios.patch(
          `/api/events/${this.eventId}/work-order-progress/${check.id}/`,
          { is_done: !!isDone, notes: check.notes || '' },
        );
        if (!this.alive) return;
        this.progress = this.progress.map((item) =>
          item.id === data.id ? data : item,
        );
        this.$emit('progress-changed', data);
        await this.loadStatus();
      } catch (err) {
        if (!this.alive) return;
        this.progressError =
          err?.response?.status === 403
            ? 'You do not have permission to update the progress checklist.'
            : readWorkOrderError(err, 'Could not update this progress item.');
      } finally {
        if (this.alive) this.savingCheckId = null;
      }
    },
  },
};
</script>

<style scoped>
.jr-wo-status {
  display: grid;
  gap: 1rem;
  align-content: start;
  overflow-y: auto;
  min-height: 0;
  padding-right: 0.125rem;
}

.jr-wo-status__muted {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--color-jr-muted);
}

.jr-wo-status__current {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem 1rem;
}

.jr-wo-status__current-main {
  display: grid;
  gap: 0.25rem;
  min-width: 0;
}

.jr-wo-status__label {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-jr-muted);
}

.jr-wo-status__current-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.jr-wo-status__current-name {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-wo-status__meta {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.4;
  color: var(--color-jr-muted);
  overflow-wrap: anywhere;
}

.jr-wo-status__progress-head {
  display: grid;
  gap: 0.45rem;
  margin-bottom: 0.5rem;
}

.jr-wo-status__count {
  margin: 0;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-jr-text);
  white-space: nowrap;
}

.jr-wo-status__bar {
  height: 0.375rem;
  background: var(--color-jr-surface-muted);
  border: 1px solid var(--color-jr-border);
}

.jr-wo-status__bar > span {
  display: block;
  height: 100%;
  background: var(--color-jr-primary);
}

.jr-wo-status__message {
  margin-top: 0.75rem;
}

/* Compact “still needed” hints inside the checklist — subtle, not banners. */
.jr-wo-status__needed-group {
  display: grid;
  gap: 0.3rem;
  margin-bottom: 0.6rem;
}

.jr-wo-status__needed {
  margin: 0;
  padding: 0.3rem 0.5rem;
  border-left: 2px solid var(--color-jr-warning);
  background: var(--color-jr-warning-subtle);
  color: var(--color-jr-warning-text);
  font-size: 0.75rem;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.jr-wo-status__needed strong {
  font-weight: 600;
}

.jr-wo-status__actions {
  display: grid;
  gap: 0.5rem;
  margin-top: 1rem;
}

.jr-wo-status__action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

/* Current status stays in the action blue even though it is disabled. */
.jr-wo-status__status-btn--current:disabled {
  opacity: 1;
  cursor: default;
}

.jr-wo-status__error {
  margin: 0.75rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-jr-danger);
}

.jr-wo-status__checks {
  display: grid;
  margin: 0;
  padding: 0;
  list-style: none;
}

.jr-wo-status__check {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 0.35rem 0.65rem;
  align-items: start;
  padding: 0.65rem 0;
  border-bottom: 1px solid var(--color-jr-border);
}

.jr-wo-status__check:last-child {
  border-bottom: 0;
}

.jr-wo-status__check-main {
  display: grid;
  gap: 0.15rem;
  min-width: 0;
}

.jr-wo-status__check-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-jr-text);
  overflow-wrap: anywhere;
}

.jr-wo-status__check--done .jr-wo-status__check-name {
  color: var(--color-jr-muted);
}

.jr-wo-status__badges {
  grid-column: 2;
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.jr-wo-status__history {
  margin: 0;
  padding: 0;
  list-style: none;
}

.jr-wo-status__history li {
  display: grid;
  gap: 0.15rem;
  padding: 0.65rem 0;
  border-bottom: 1px solid var(--color-jr-border);
  font-size: 0.875rem;
}

.jr-wo-status__history li:last-child {
  border-bottom: 0;
}

.jr-wo-status__history span {
  color: var(--color-jr-muted);
  font-size: 0.8125rem;
  overflow-wrap: anywhere;
}

.jr-wo-status__confirm {
  display: grid;
  gap: 0.75rem;
  margin: 0 0 1rem;
}

.jr-wo-status__confirm div {
  display: grid;
  gap: 0.2rem;
}

.jr-wo-status__confirm dt {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-jr-muted);
}

.jr-wo-status__confirm dd {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-wo-status__missing {
  margin: 0.35rem 0 0;
  padding-left: 1.1rem;
}

.jr-wo-status__confirm-error {
  margin-top: 0.75rem;
  font-size: 0.8125rem;
  color: var(--color-jr-danger);
}

.jr-wo-status__confirm-error p {
  margin: 0;
}

@media (min-width: 640px) {
  .jr-wo-status__check {
    grid-template-columns: auto minmax(0, 1fr) auto;
  }

  .jr-wo-status__badges {
    grid-column: auto;
    justify-content: flex-end;
  }
}
</style>
