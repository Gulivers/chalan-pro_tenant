<template>
  <section class="jr-mm-panel">
    <JRButton
      v-if="canRequest"
      type="button"
      @click="openRequest">
      Request Material
    </JRButton>
    <p v-if="loading" class="jr-mm-panel__status">Loading requests…</p>
    <DataTable
      v-else-if="requests.length"
      :key="`${workAccountId}-${eventId}`"
      v-model:expandedRowGroups="expandedRowGroups"
      class="jr-mm-groups"
      :value="requests"
      dataKey="id"
      expandableRowGroups
      rowGroupMode="subheader"
      groupRowsBy="id"
      :rowClass="hiddenGroupRow"
      :pt="{ rowToggleButton: { 'aria-label': 'Show or hide this request' } }">
      <template #groupheader="{ data }">
        <span class="jr-mm-group">
          <router-link
            v-if="canView"
            class="jr-mm-group__number"
            :to="{ name: 'material-request-detail', params: { id: data.id } }">
            {{ data.document_number }}
          </router-link>
          <strong v-else>{{ data.document_number }}</strong>
          <JRBadge :value="data.status_name || '—'" :severity="statusSeverity(data.status)" />
          <span v-if="data.phase" class="jr-mm-group__meta">{{ data.phase }}</span>
        </span>
      </template>
      <Column field="id" header="" />
      <template #groupfooter="{ data }">
        <MaterialRequestDetail
          :key="data.id"
          :request-id="data.id"
          embedded
          hide-heading
          :editable="canEdit" />
      </template>
    </DataTable>
    <p v-else class="jr-mm-panel__status">No material requests for this work order yet.</p>
  </section>
</template>

<script>
import axios from 'axios';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import { JRBadge, JRButton } from '@/ui';
import MaterialRequestDetail from './MaterialRequestDetail.vue';

export default {
  name: 'MissingMaterialPanel',
  components: { Column, DataTable, JRBadge, JRButton, MaterialRequestDetail },
  props: {
    eventId: { type: Number, required: true },
    workAccountId: { type: Number, required: true },
  },
  data() {
    return {
      requests: [],
      expandedRowGroups: [],
      loading: false,
      alive: true,
    };
  },
  beforeUnmount() {
    this.alive = false;
  },
  computed: {
    canRequest() {
      return this.hasPermission('apptransactions.add_document');
    },
    canView() {
      return this.hasPermission('apptransactions.view_document');
    },
    canEdit() {
      return this.hasPermission('apptransactions.change_document');
    },
  },
  watch: {
    eventId: 'reload',
    workAccountId: 'reload',
  },
  mounted() {
    this.reload();
  },
  methods: {
    hiddenGroupRow() {
      return 'jr-mm-group-row';
    },
    statusSeverity(code) {
      if (code === 'delivered') return 'success';
      if (code === 'preparing') return 'warning';
      if (code === 'closed') return 'secondary';
      return 'info';
    },
    reload() {
      this.expandedRowGroups = [];
      this.requests = [];
      this.load();
    },
    async load() {
      const eventId = Number(this.eventId);
      const workAccountId = Number(this.workAccountId);
      if (!eventId || !workAccountId) {
        this.requests = [];
        this.loading = false;
        return;
      }
      this.loading = true;
      try {
        const { data } = await axios.get('/api/material-requests/', {
          params: {
            work_order: eventId,
            work_account: workAccountId,
            page: 1,
            per_page: 200,
          },
        });
        if (
          !this.alive ||
          eventId !== Number(this.eventId) ||
          workAccountId !== Number(this.workAccountId)
        ) {
          return;
        }
        this.requests = Array.isArray(data?.items) ? data.items : [];
      } catch {
        if (
          !this.alive ||
          eventId !== Number(this.eventId) ||
          workAccountId !== Number(this.workAccountId)
        ) {
          return;
        }
        this.requests = [];
      } finally {
        if (
          this.alive &&
          eventId === Number(this.eventId) &&
          workAccountId === Number(this.workAccountId)
        ) {
          this.loading = false;
        }
      }
    },
    openRequest() {
      this.$router.push({
        name: 'missing-material',
        params: {
          workAccountId: this.workAccountId,
          eventId: this.eventId,
        },
      });
    },
  },
};
</script>

<style scoped>
.jr-mm-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 0.5rem 0 1rem;
}
.jr-mm-panel__status {
  margin: 0;
  color: var(--color-jr-muted, #4b5563);
}
.jr-mm-groups :deep(.p-datatable-thead) {
  display: none;
}
.jr-mm-groups :deep(tr.jr-mm-group-row) {
  display: none;
}
.jr-mm-group {
  display: inline-flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.65rem;
  vertical-align: middle;
}
.jr-mm-group__number {
  color: var(--color-jr-text, #111827);
  font-size: 0.9375rem;
  font-weight: 600;
  text-decoration: none;
}
.jr-mm-group__number:hover {
  text-decoration: underline;
}
.jr-mm-group__meta {
  color: var(--color-jr-muted, #4b5563);
  font-size: 0.8125rem;
}
</style>
