<template>
  <DataTable
    class="jr-control"
    :value="value"
    :loading="loading"
    :dataKey="dataKey"
    :paginator="paginator"
    :rows="rows"
    :rowHover="rowHover"
    :stripedRows="stripedRows"
    v-bind="$attrs"
  >
    <slot />
    <template #empty>
      <slot name="empty">
        <JREmptyState :title="emptyTitle" :description="emptyDescription" />
      </slot>
    </template>
    <template v-if="$slots.header" #header>
      <slot name="header" />
    </template>
    <template v-if="$slots.footer" #footer>
      <slot name="footer" />
    </template>
  </DataTable>
</template>

<script>
import DataTable from 'primevue/datatable';
import JREmptyState from './JREmptyState.vue';

export default {
  name: 'JRDataTable',
  components: { DataTable, JREmptyState },
  inheritAttrs: false,
  props: {
    value: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
    dataKey: {
      type: String,
      default: 'id',
    },
    paginator: {
      type: Boolean,
      default: false,
    },
    rows: {
      type: Number,
      default: 20,
    },
    rowHover: {
      type: Boolean,
      default: true,
    },
    stripedRows: {
      type: Boolean,
      default: false,
    },
    emptyTitle: {
      type: String,
      default: 'No records',
    },
    emptyDescription: {
      type: String,
      default: '',
    },
  },
};
</script>
