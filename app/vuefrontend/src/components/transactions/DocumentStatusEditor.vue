<template>
  <JRSection title="Document Statuses">
    <p class="jr-doc-status-editor__note">
      Workflow for this document type. Sequence order controls transitions
      (one step at a time). Add an active initial status before enabling
      status tracking on documents.
    </p>

    <p
      v-if="readOnly"
      class="jr-doc-status-editor__note"
      role="status">
      These statuses are managed by the system and cannot be edited here.
    </p>

    <p v-if="loading" class="jr-doc-status-editor__status" role="status">
      Loading statuses…
    </p>

    <p
      v-else-if="error"
      class="jr-doc-status-editor__error"
      role="alert">
      {{ error }}
    </p>

    <template v-else>
      <div class="jr-doc-status-editor__table-wrap">
        <table class="jr-doc-status-editor__table">
          <thead>
            <tr>
              <th scope="col">Sequence</th>
              <th scope="col">Code</th>
              <th scope="col">Name</th>
              <th scope="col">Initial</th>
              <th scope="col">Terminal</th>
              <th scope="col">Active</th>
              <th v-if="canMutate" scope="col">
                <span class="jr-sr-only">Actions</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in sortedRows" :key="rowKey(row)">
              <td>
                <JRInput
                  v-if="canMutate && (isDraft(row) || canChange)"
                  :inputId="`status-seq-${rowKey(row)}`"
                  type="number"
                  :modelValue="String(row.sequence ?? '')"
                  :disabled="saving"
                  @update:modelValue="row.sequence = toInt($event, 1)" />
                <span v-else>{{ row.sequence }}</span>
              </td>
              <td>
                <JRInput
                  v-if="canMutate && (isDraft(row) || canChange)"
                  :inputId="`status-code-${rowKey(row)}`"
                  :modelValue="row.code"
                  maxlength="32"
                  placeholder="requested"
                  :disabled="saving"
                  @update:modelValue="row.code = normalizeCode($event)" />
                <span v-else class="jr-doc-status-editor__code">{{ row.code }}</span>
              </td>
              <td>
                <JRInput
                  v-if="canMutate && (isDraft(row) || canChange)"
                  :inputId="`status-name-${rowKey(row)}`"
                  :modelValue="row.name"
                  maxlength="80"
                  placeholder="Requested"
                  :disabled="saving"
                  @update:modelValue="row.name = ($event || '').toString()" />
                <span v-else>{{ row.name }}</span>
              </td>
              <td class="jr-doc-status-editor__flag">
                <JRCheckbox
                  :inputId="`status-initial-${rowKey(row)}`"
                  :modelValue="!!row.is_initial"
                  ariaLabel="Initial status"
                  :disabled="!canMutate || saving || (!isDraft(row) && !canChange)"
                  @update:modelValue="setInitial(row, $event)" />
              </td>
              <td class="jr-doc-status-editor__flag">
                <JRCheckbox
                  :inputId="`status-terminal-${rowKey(row)}`"
                  v-model="row.is_terminal"
                  ariaLabel="Terminal status"
                  :disabled="!canMutate || saving || (!isDraft(row) && !canChange)" />
              </td>
              <td class="jr-doc-status-editor__flag">
                <JRCheckbox
                  :inputId="`status-active-${rowKey(row)}`"
                  v-model="row.is_active"
                  ariaLabel="Active status"
                  :disabled="!canMutate || saving || (!isDraft(row) && !canChange)" />
              </td>
              <td v-if="canMutate" class="jr-doc-status-editor__actions">
                <JRButton
                  v-if="isDraft(row)"
                  type="button"
                  size="sm"
                  :disabled="saving"
                  @click="saveRow(row)">
                  Add
                </JRButton>
                <template v-else>
                  <JRButton
                    type="button"
                    variant="ghost"
                    size="sm"
                    :disabled="saving || !canChange"
                    @click="saveRow(row)">
                    Save
                  </JRButton>
                  <JRButton
                    type="button"
                    variant="ghost"
                    size="sm"
                    :disabled="saving || !canDelete"
                    @click="removeRow(row)">
                    Delete
                  </JRButton>
                </template>
              </td>
            </tr>
            <tr v-if="!sortedRows.length">
              <td :colspan="canMutate ? 7 : 6">
                No statuses yet. Add the initial status first, then the rest of the workflow.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="canAdd" class="jr-doc-status-editor__toolbar">
        <JRButton
          type="button"
          variant="secondary"
          size="sm"
          :disabled="saving || hasDraft"
          @click="addDraft">
          + Add status
        </JRButton>
      </div>

      <p
        v-if="rowError"
        class="jr-doc-status-editor__error"
        role="alert">
        {{ rowError }}
      </p>
    </template>
  </JRSection>
</template>

<script>
import axios from 'axios';
import { JRButton, JRCheckbox, JRInput, JRSection } from '@/ui';
import { readApiError } from '@/utils/documentStatus';

let draftSeq = 0;

function emptyDraft(sequence) {
  draftSeq += 1;
  return {
    _draftId: `draft-${draftSeq}`,
    id: null,
    sequence,
    code: '',
    name: '',
    is_initial: false,
    is_terminal: false,
    is_active: true,
  };
}

export default {
  name: 'DocumentStatusEditor',
  components: { JRButton, JRCheckbox, JRInput, JRSection },
  props: {
    documentTypeId: {
      type: [Number, String],
      required: true,
    },
    readOnly: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      rows: [],
      loading: false,
      saving: false,
      error: '',
      rowError: '',
      alive: true,
    };
  },
  computed: {
    canAdd() {
      return (
        !this.readOnly &&
        !!this.hasPermission?.('apptransactions.add_documentstatus')
      );
    },
    canChange() {
      return (
        !this.readOnly &&
        !!this.hasPermission?.('apptransactions.change_documentstatus')
      );
    },
    canDelete() {
      return (
        !this.readOnly &&
        !!this.hasPermission?.('apptransactions.delete_documentstatus')
      );
    },
    canMutate() {
      return this.canAdd || this.canChange || this.canDelete;
    },
    sortedRows() {
      return [...this.rows].sort(
        (a, b) => Number(a.sequence) - Number(b.sequence)
      );
    },
    hasDraft() {
      return this.rows.some((row) => this.isDraft(row));
    },
    nextSequence() {
      return (
        this.rows.reduce(
          (acc, row) => Math.max(acc, Number(row.sequence) || 0),
          0
        ) + 1
      );
    },
  },
  watch: {
    documentTypeId: {
      immediate: true,
      handler() {
        this.load();
      },
    },
  },
  beforeUnmount() {
    this.alive = false;
  },
  methods: {
    rowKey(row) {
      return row.id || row._draftId;
    },
    isDraft(row) {
      return !row.id;
    },
    toInt(value, fallback = 1) {
      const n = Math.floor(Number(value));
      return Number.isFinite(n) && n > 0 ? n : fallback;
    },
    normalizeCode(value) {
      return (value || '')
        .toString()
        .trim()
        .toLowerCase()
        .replace(/\s+/g, '_');
    },
    setInitial(row, value) {
      const on = !!value;
      row.is_initial = on;
      if (on) {
        this.rows.forEach((other) => {
          if (other !== row) other.is_initial = false;
        });
      }
    },
    addDraft() {
      if (this.hasDraft || !this.canAdd) return;
      const draft = emptyDraft(this.nextSequence);
      if (!this.rows.length) draft.is_initial = true;
      this.rows = [...this.rows, draft];
      this.rowError = '';
    },
    async load() {
      if (!this.documentTypeId) {
        this.rows = [];
        return;
      }
      const typeId = this.documentTypeId;
      this.loading = true;
      this.error = '';
      this.rowError = '';
      try {
        const { data } = await axios.get('/api/document-statuses/', {
          params: { document_type: typeId },
        });
        if (!this.alive || typeId !== this.documentTypeId) return;
        const list = Array.isArray(data) ? data : data?.results || [];
        this.rows = list.map((row) => ({
          id: row.id,
          sequence: row.sequence,
          code: row.code,
          name: row.name,
          is_initial: !!row.is_initial,
          is_terminal: !!row.is_terminal,
          is_active: !!row.is_active,
        }));
      } catch (err) {
        if (!this.alive || typeId !== this.documentTypeId) return;
        this.rows = [];
        this.error = readApiError(err, 'Could not load document statuses.');
      } finally {
        if (this.alive && typeId === this.documentTypeId) this.loading = false;
      }
    },
    validateRow(row) {
      if (!row.sequence || Number(row.sequence) < 1) {
        return 'Sequence must be a positive number.';
      }
      if (!row.code) return 'Code is required.';
      if (!row.name?.trim()) return 'Name is required.';
      return '';
    },
    async saveRow(row) {
      this.rowError = this.validateRow(row);
      if (this.rowError) return;
      this.saving = true;
      try {
        const payload = {
          document_type: Number(this.documentTypeId),
          sequence: Number(row.sequence),
          code: this.normalizeCode(row.code),
          name: row.name.trim(),
          is_initial: !!row.is_initial,
          is_terminal: !!row.is_terminal,
          is_active: !!row.is_active,
        };
        if (this.isDraft(row)) {
          await axios.post('/api/document-statuses/', payload);
        } else {
          await axios.patch(`/api/document-statuses/${row.id}/`, {
            sequence: payload.sequence,
            code: payload.code,
            name: payload.name,
            is_initial: payload.is_initial,
            is_terminal: payload.is_terminal,
            is_active: payload.is_active,
          });
        }
        await this.load();
      } catch (err) {
        this.rowError = readApiError(err, 'Could not save this status.');
      } finally {
        this.saving = false;
      }
    },
    async removeRow(row) {
      if (this.isDraft(row)) {
        this.rows = this.rows.filter((item) => item !== row);
        return;
      }
      const ok = window.confirm(
        `Delete status "${row.name}"? If it is already used, deactivate it instead.`
      );
      if (!ok) return;
      this.saving = true;
      this.rowError = '';
      try {
        await axios.delete(`/api/document-statuses/${row.id}/`);
        await this.load();
      } catch (err) {
        this.rowError = readApiError(
          err,
          'Could not delete this status. Deactivate it if it is already in use.'
        );
      } finally {
        this.saving = false;
      }
    },
  },
};
</script>

<style scoped>
.jr-doc-status-editor__note,
.jr-doc-status-editor__status {
  margin: 0 0 0.75rem;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-doc-status-editor__error {
  margin: 0.75rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-jr-danger, #dc2626);
}

.jr-doc-status-editor__table-wrap {
  overflow: auto;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel, 0.75rem);
  background: var(--color-jr-surface, #fff);
}

.jr-doc-status-editor__table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  margin: 0;
}

.jr-doc-status-editor__table th,
.jr-doc-status-editor__table td {
  padding: 0.55rem 0.65rem;
  border-bottom: 1px solid var(--color-jr-border);
  text-align: left;
  vertical-align: middle;
}

.jr-doc-status-editor__table thead th {
  background: var(--color-jr-surface-muted);
  font-weight: 600;
  color: var(--color-jr-text);
  white-space: nowrap;
}

.jr-doc-status-editor__table tbody tr:last-child td {
  border-bottom: none;
}

.jr-doc-status-editor__code {
  font-size: 0.8125rem;
  font-weight: 600;
}

.jr-doc-status-editor__flag {
  text-align: center;
  width: 4.5rem;
}

.jr-doc-status-editor__actions {
  white-space: nowrap;
}

.jr-doc-status-editor__actions :deep(.jr-button) {
  margin-right: 0.25rem;
}

.jr-doc-status-editor__toolbar {
  margin-top: 0.75rem;
}

.jr-doc-status-editor__table :deep(.jr-input),
.jr-doc-status-editor__table :deep(.p-inputtext) {
  min-width: 6rem;
  width: 100%;
}
</style>
