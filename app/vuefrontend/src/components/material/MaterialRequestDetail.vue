<template>
  <section class="jr-mr-detail" :class="{ 'jr-mr-detail--embedded': embedded }">
    <JRPageHeader v-if="!embedded" :title="request.document_number || 'Material Request'">
      <template #actions>
        <JRButton
          v-if="!linesEditable && canEdit"
          type="button"
          variant="ghost"
          size="sm"
          @click="goEdit">
          Edit
        </JRButton>
        <JRButton type="button" variant="ghost" size="sm" @click="goList">
          All requests
        </JRButton>
      </template>
    </JRPageHeader>

    <header v-else-if="request.id && !hideHeading" class="jr-mr-detail__embed-head">
      <router-link
        v-if="canView"
        class="jr-mr-detail__number"
        :to="{ name: 'material-request-detail', params: { id: request.id } }">
        {{ request.document_number }}
      </router-link>
      <strong v-else>{{ request.document_number }}</strong>
      <JRBadge :value="request.status_name || '—'" :severity="statusSeverity(request.status)" />
    </header>

    <p v-if="loading">Loading…</p>
    <div v-else-if="request.id">
      <p v-if="!embedded" class="jr-mr-detail__meta">
        {{ request.work_account_title }}<br />
        {{ request.phase }}<br />
        Requested by {{ request.requested_by }}
      </p>
      <p v-else class="jr-mr-detail__meta">
        {{ request.phase }}
        <span v-if="request.requested_by"> · Requested by {{ request.requested_by }}</span>
      </p>
      <p v-if="!embedded">
        <JRBadge :value="request.status_name || '—'" :severity="statusSeverity(request.status)" />
      </p>
      <p v-if="request.notes">{{ request.notes }}</p>

      <table class="jr-mr-detail__table">
        <thead>
          <tr>
            <th>Material</th>
            <th>SKU</th>
            <th>Qty</th>
            <th v-if="linesEditable"><span class="jr-sr-only">Remove</span></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="line in request.lines || []" :key="line.id">
            <td>{{ line.product_name }}</td>
            <td>{{ line.sku }}</td>
            <td>
              <div v-if="linesEditable" class="jr-mr-detail__qty">
                <button
                  type="button"
                  aria-label="Decrease quantity"
                  :disabled="saving"
                  @click="adjustLine(line, -1)">
                  −
                </button>
                <input
                  type="number"
                  min="1"
                  :aria-label="`Quantity for ${line.product_name}`"
                  :value="line.quantity"
                  :disabled="saving"
                  @change="setLineQty(line, $event)" />
                <button
                  type="button"
                  aria-label="Increase quantity"
                  :disabled="saving"
                  @click="adjustLine(line, 1)">
                  +
                </button>
              </div>
              <span v-else>{{ line.quantity }}</span>
            </td>
            <td v-if="linesEditable">
              <JRButton
                type="button"
                variant="ghost"
                size="sm"
                :disabled="saving"
                @click="removeLine(line)">
                Remove
              </JRButton>
            </td>
          </tr>
        </tbody>
      </table>

      <section
        v-if="canEdit && (request.next_status || request.previous_status)"
        class="jr-mr-detail__advance">
        <JRField :label="notesLabel" :inputId="notesId">
          <JRTextarea :inputId="notesId" v-model="transitionNotes" :rows="2" />
        </JRField>
        <div class="jr-mr-detail__moves">
          <JRButton
            v-if="request.previous_status"
            type="button"
            variant="secondary"
            :disabled="saving"
            @click="moveTo(request.previous_status)">
            Revert to {{ request.previous_status_name }}
          </JRButton>
          <JRButton
            v-if="request.next_status"
            type="button"
            :disabled="saving"
            @click="moveTo(request.next_status)">
            Mark as {{ request.next_status_name }}
          </JRButton>
        </div>
      </section>
      <p v-if="error" class="jr-mr-detail__error" role="alert">{{ error }}</p>

      <section>
        <h2>History</h2>
        <ol class="jr-mr-detail__history">
          <li v-for="row in request.history || []" :key="row.id">
            <strong>{{ row.from_status_name || 'New' }} → {{ row.to_status_name }}</strong>
            <span>{{ row.changed_by_username }} · {{ formatWhen(row.changed_at) }}</span>
            <span v-if="row.notes">{{ row.notes }}</span>
          </li>
        </ol>
      </section>
    </div>
    <p v-else-if="!loading" class="jr-mr-detail__error" role="alert">
      Could not load this material request.
    </p>
  </section>
</template>

<script>
import axios from 'axios';
import { JRPageHeader, JRButton, JRBadge, JRField, JRTextarea } from '@/ui';

export default {
  name: 'MaterialRequestDetail',
  components: { JRPageHeader, JRButton, JRBadge, JRField, JRTextarea },
  props: {
    requestId: {
      type: [Number, String],
      required: true,
    },
    embedded: {
      type: Boolean,
      default: false,
    },
    editable: {
      type: Boolean,
      default: false,
    },
    hideHeading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      request: {},
      loading: false,
      saving: false,
      transitionNotes: '',
      error: '',
      alive: true,
    };
  },
  beforeUnmount() {
    this.alive = false;
  },
  computed: {
    canView() {
      return this.hasPermission('apptransactions.view_document');
    },
    canEdit() {
      return this.hasPermission('apptransactions.change_document');
    },
    linesEditable() {
      return this.canEdit && (!this.embedded || this.editable);
    },
    notesId() {
      return `mr-transition-notes-${this.requestId}`;
    },
    notesLabel() {
      return 'Notes';
    },
  },
  watch: {
    requestId: {
      immediate: true,
      handler() {
        this.load();
      },
    },
  },
  methods: {
    statusSeverity(code) {
      if (code === 'delivered') return 'success';
      if (code === 'preparing') return 'warning';
      if (code === 'closed') return 'secondary';
      return 'info';
    },
    async load() {
      if (!this.requestId) return;
      const requestId = this.requestId;
      this.loading = true;
      this.error = '';
      try {
        const { data } = await axios.get(`/api/material-requests/${requestId}/`);
        if (!this.alive || requestId !== this.requestId) return;
        this.request = data;
      } catch {
        if (!this.alive || requestId !== this.requestId) return;
        this.request = {};
      } finally {
        if (this.alive && requestId === this.requestId) this.loading = false;
      }
    },
    async moveTo(statusCode) {
      this.saving = true;
      this.error = '';
      try {
        const { data } = await axios.post(
          `/api/material-requests/${this.request.id}/transition/`,
          { status_code: statusCode, notes: this.transitionNotes },
        );
        this.request = data;
        this.transitionNotes = '';
      } catch (err) {
        this.error = this.readError(err, 'Could not change the status.');
      } finally {
        this.saving = false;
      }
    },
    adjustLine(line, delta) {
      const next = Number(line.quantity) + delta;
      if (next <= 0) {
        this.removeLine(line);
        return;
      }
      this.saveLine(line, next);
    },
    setLineQty(line, event) {
      const quantity = Number(event.target.value);
      if (!Number.isFinite(quantity) || quantity <= 0) {
        event.target.value = line.quantity;
        this.removeLine(line);
        return;
      }
      this.saveLine(line, quantity);
    },
    removeLine(line) {
      this.confirmDelete(
        'Remove this item?',
        `${line.product_name} will be removed from this request.`,
        () => this.saveLine(line, 0),
      );
    },
    async saveLine(line, quantity) {
      this.saving = true;
      this.error = '';
      try {
        const { data } = await axios.patch(
          `/api/material-requests/${this.request.id}/lines/`,
          { lines: [{ id: line.id, quantity }] },
        );
        this.request = data;
      } catch (err) {
        this.error = this.readError(err, 'Could not update the items.');
        await this.load();
      } finally {
        this.saving = false;
      }
    },
    readError(err, fallback) {
      const data = err?.response?.data;
      const detail = data?.lines || data?.status || data?.detail || data?.non_field_errors;
      if (Array.isArray(detail)) return detail.join(' ');
      if (typeof detail === 'string') return detail;
      return fallback;
    },
    formatWhen(value) {
      if (!value) return '';
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return value;
      return date.toLocaleString();
    },
    goList() {
      this.$router.push({ name: 'material-requests' });
    },
    goEdit() {
      this.$router.push({
        name: 'material-request-detail',
        params: { id: this.request.id },
        query: { mode: 'edit' },
      });
    },
  },
};
</script>

<style scoped>
.jr-mr-detail--embedded {
  padding: 0.85rem 0 1.25rem;
  border-bottom: 1px solid var(--color-jr-border, #e5e7eb);
}
.jr-mr-detail__embed-head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem;
  margin-bottom: 0.35rem;
}
.jr-mr-detail__number {
  color: var(--color-jr-primary, #2563eb);
  font-weight: 600;
  text-decoration: none;
}
.jr-mr-detail__number:hover {
  text-decoration: underline;
}
.jr-mr-detail__meta {
  margin-top: 0;
}
.jr-mr-detail__table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0 1.5rem;
}
.jr-mr-detail__table th,
.jr-mr-detail__table td {
  text-align: left;
  padding: 0.45rem 0.25rem;
  border-bottom: 1px solid var(--color-jr-border, #e5e7eb);
  vertical-align: middle;
}
.jr-mr-detail__qty {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.jr-mr-detail__qty button {
  width: 2.25rem;
  height: 2.25rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface, #fff);
  cursor: pointer;
}
.jr-mr-detail__qty input {
  width: 4.5rem;
  height: 2.25rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  text-align: center;
}
.jr-mr-detail__advance,
.jr-mr-detail__history {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.jr-mr-detail__moves {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.jr-mr-detail__history {
  margin: 0;
  padding-left: 1.1rem;
}
.jr-mr-detail__history li {
  display: flex;
  flex-direction: column;
  margin-bottom: 0.75rem;
}
.jr-mr-detail__error {
  color: var(--color-jr-danger, #dc2626);
}
.jr-sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
</style>
