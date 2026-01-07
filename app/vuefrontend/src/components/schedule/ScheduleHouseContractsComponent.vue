<template>
  <div class="house-contracts-container">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4 class="mb-0">Contracts</h4>
      <button class="btn btn-primary btn-sm" @click="goToContractForm">
        <i class="bi bi-plus-circle"></i> Add Contract
      </button>
    </div>
    
    <div v-if="loading" class="text-center py-4">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    
    <div v-else-if="contracts.length === 0" class="text-center py-4 text-muted">
      <p>No contracts available for this work account.</p>
    </div>
    
    <ul v-else class="list-group">
      <li v-for="item in contracts" :key="item" class="list-group-item d-flex justify-content-between align-items-center">
        <a :href="`contract-view/view/${item}`" target="_blank" class="text-decoration-none">
          Contract {{ item }}
        </a>
        <span class="badge bg-primary rounded-pill">View</span>
      </li>
    </ul>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'ScheduleHouseContractsComponent',
  props: {
    eventId: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      contracts: [],
      loading: false,
    };
  },
  async mounted() {
    await this.getContracts();
  },
  methods: {
    async getContracts() {
      this.loading = true;
      try {
        const resp = await axios.get(`/api/event/${this.$props.eventId}/contracts/`);
        if (resp.status === 200) {
          this.contracts = resp.data || [];
        }
      } catch (error) {
        console.error('Error fetching contracts:', error);
        this.contracts = [];
      } finally {
        this.loading = false;
      }
    },
    goToContractForm() {
      // Cierra el modal (si existe) y navega luego de un tick para evitar backdrop
      try {
        const modalEl = document.querySelector('.modal.show');
        if (modalEl) {
          const inst = window.bootstrap?.Modal?.getInstance?.(modalEl);
          inst?.hide?.();
        }
        document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
        document.body.classList.remove('modal-open');
        document.body.style.removeProperty('padding-right');
      } catch (e) {
        // no-op
      }
      // Navegación
      this.$nextTick(() => {
        try {
          const resolved = this.$router.resolve({ name: 'contract-form', query: { event_id: this.$props.eventId } });
          const href = resolved?.href || `/contract-form?event_id=${this.$props.eventId}`;
          window.location.href = href;
        } catch (_) {
          window.location.href = `/contract-form?event_id=${this.$props.eventId}`;
        }
      });
    },
  },
};
</script>

<style scoped>
.house-contracts-container {
  padding: 1rem;
}

.list-group-item {
  cursor: pointer;
  transition: background-color 0.2s;
}

.list-group-item:hover {
  background-color: #f8f9fa;
}
</style>

