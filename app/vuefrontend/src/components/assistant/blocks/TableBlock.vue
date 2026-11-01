<template>
  <div class="assistant-table-block">
    <div v-if="block.title" class="assistant-block-title mb-2 text-sm text-jr-muted">
      {{ block.title }}
    </div>
    <div v-if="!columns.length || !rows.length" class="text-start text-sm text-jr-muted">
      No rows to display.
    </div>
    <div v-else class="overflow-x-auto">
      <table class="assistant-table mb-0">
        <thead>
          <tr>
            <th
              v-for="col in columns"
              :key="col.key"
              scope="col"
              :class="headerClass(col)">
              {{ col.label || col.key }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in rows" :key="rowKey(row, rowIndex)">
            <td
              v-for="col in columns"
              :key="`${rowIndex}-${col.key}`"
              :class="cellClass(col)">
              {{ formatCell(row, col) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <div v-if="paginationHint" class="mt-1 text-start text-sm text-jr-muted">
      {{ paginationHint }}
    </div>
  </div>
</template>

<script>
import { formatAssistantValue } from '../formatValue';

export default {
  name: 'TableBlock',
  props: {
    block: {
      type: Object,
      required: true,
    },
  },
  computed: {
    columns() {
      const cols = this.block?.columns;
      if (!Array.isArray(cols)) return [];
      return cols.filter((c) => c && typeof c === 'object' && c.key);
    },
    rows() {
      return Array.isArray(this.block?.rows) ? this.block.rows : [];
    },
    paginationHint() {
      const p = this.block?.pagination;
      if (!p || typeof p !== 'object') return '';
      const total = p.total;
      const shown = this.rows.length;
      if (typeof total === 'number' && total > shown) {
        return `Showing ${shown} of ${total}`;
      }
      return '';
    },
  },
  methods: {
    rowKey(row, index) {
      return row?.id ?? row?.document_id ?? row?.vendor_id ?? `row-${index}`;
    },
    formatCell(row, col) {
      const value = row?.[col.key];
      return formatAssistantValue(value, col.format || 'text', col.currency || 'USD');
    },
    headerClass(col) {
      return col.format === 'currency' || col.format === 'number'
        ? 'text-end'
        : 'text-start';
    },
    cellClass(col) {
      return col.format === 'currency' || col.format === 'number'
        ? 'text-end whitespace-nowrap'
        : 'text-start';
    },
  },
};
</script>

<style scoped>
.assistant-table-block {
  text-align: left;
}
.assistant-block-title {
  font-weight: 600;
}
.assistant-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}
.assistant-table th,
.assistant-table td {
  padding: 0.35rem 0.5rem;
  border-bottom: 1px solid var(--color-jr-border);
  text-align: left;
}
.assistant-table th {
  font-weight: 600;
  white-space: nowrap;
  background: var(--color-jr-surface-muted);
}
</style>
