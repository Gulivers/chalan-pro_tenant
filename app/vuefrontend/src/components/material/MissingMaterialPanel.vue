<template>
  <section class="jr-mm-panel">
    <JRButton
      v-if="canRequest"
      type="button"
      @click="openRequest">
      Request Material
    </JRButton>
    <p v-if="loading" class="jr-mm-panel__status">Loading requests…</p>
    <div v-else-if="requests.length">
      <MaterialRequestDetail
        v-for="item in requests"
        :key="item.id"
        :request-id="item.id"
        embedded
        :editable="canEdit" />
    </div>
    <p v-else class="jr-mm-panel__status">No material requests for this work order yet.</p>
  </section>
</template>

<script>
import axios from 'axios';
import { JRButton } from '@/ui';
import MaterialRequestDetail from './MaterialRequestDetail.vue';

export default {
  name: 'MissingMaterialPanel',
  components: { JRButton, MaterialRequestDetail },
  props: {
    eventId: { type: Number, required: true },
    workAccountId: { type: Number, required: true },
  },
  data() {
    return {
      requests: [],
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
    canEdit() {
      return this.hasPermission('apptransactions.change_document');
    },
  },
  watch: {
    eventId: {
      immediate: true,
      handler() {
        this.load();
      },
    },
  },
  methods: {
    async load() {
      const eventId = this.eventId;
      this.loading = true;
      try {
        const { data } = await axios.get('/api/material-requests/', {
          params: {
            work_order: eventId,
            work_account: this.workAccountId,
            page: 1,
            per_page: 200,
          },
        });
        if (!this.alive || eventId !== this.eventId) return;
        this.requests = Array.isArray(data?.items) ? data.items : [];
      } catch {
        if (!this.alive || eventId !== this.eventId) return;
        this.requests = [];
      } finally {
        if (this.alive && eventId === this.eventId) this.loading = false;
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
</style>
