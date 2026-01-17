<template>
  <div class="house-contracts-container">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h5 class="mb-0">📜 Contracts</h5>
      <button 
        v-if="this.hasPermission('ctrctsapp.add_contract')"
        class="btn btn-primary btn-sm" 
        @click="goToContractForm">
        <i class="bi bi-plus-circle"></i> Add Contract
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Loading contracts...</p>
    </div>

    <div v-else-if="contracts.length === 0" class="text-center py-5 text-muted">
      <i class="bi bi-file-earmark-text" style="font-size: 3rem; opacity: 0.3;"></i>
      <p class="mt-3">No contracts found for this work account.</p>
    </div>

    <div v-else>
      <!-- Contracts Table -->
      <BTable
        :items="contracts"
        :fields="fields"
        bordered
        hover
        responsive
        striped
        small>
        <template #cell(doc_type)="data">
          <span class="badge" :class="data.item.doc_type === 'Bid' ? 'bg-warning' : 'bg-info'">
            {{ data.item.doc_type }}
          </span>
        </template>

        <template #cell(type)="data">
          <span class="badge bg-secondary">{{ data.item.type }}</span>
        </template>

        <template #cell(date_created)="data">
          {{ formatDate(data.item.date_created) }}
        </template>

        <template #cell(house_model)="data">
          {{ data.item.house_model?.name || '—' }}
        </template>

        <template #cell(sqft)="data">
          <span class="text-end">{{ data.item.sqft ? data.item.sqft.toLocaleString() : '—' }}</span>
        </template>

        <template #cell(total)="data">
          <span class="text-end fw-bold">{{ currency(data.item.total) }}</span>
        </template>

        <template #cell(actions)="data">
          <div class="btn-group btn-group-sm" role="group">
            <button
              v-if="this.hasPermission('ctrctsapp.view_contract')"
              @click="viewContract(data.item.id)"
              class="btn btn-outline-success me-1"
              title="View">
              View
            </button>
            <button
              v-if="this.hasPermission('ctrctsapp.view_contract')"
              @click="printContract(data.item.id)"
              class="btn btn-outline-dark me-1"
              title="Print PDF">
              Print
            </button>
            <button
              v-if="this.hasPermission('ctrctsapp.change_contract')"
              @click="editContract(data.item.id)"
              class="btn btn-outline-primary me-1"
              title="Edit">
              Edit
            </button>
          </div>
        </template>
      </BTable>
    </div>
  </div>
</template>

<script>
import { BTable } from 'bootstrap-vue-next';
import axios from 'axios';
import dayjs from 'dayjs';
import Swal from 'sweetalert2';

export default {
  name: 'ScheduleHouseContractsComponent',
  components: {
    BTable,
  },
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
      workAccountId: null,
      fields: [
        { key: 'id', label: 'ID', sortable: true, thClass: 'text-center', tdClass: 'text-center', thStyle: { width: '60px' } },
        { key: 'doc_type', label: 'Doc Type', sortable: true, thClass: 'text-center', tdClass: 'text-center', thStyle: { width: '100px' } },
        { key: 'type', label: 'Type', sortable: true, thClass: 'text-center', tdClass: 'text-center', thStyle: { width: '80px' } },
        { key: 'date_created', label: 'Date', sortable: true, thClass: 'text-center', tdClass: 'text-center', thStyle: { width: '120px' } },
        { key: 'house_model', label: 'Model', sortable: true, thClass: 'text-center', tdClass: 'text-center', thStyle: { width: '100px' } },
        { key: 'sqft', label: 'SqFt', sortable: true, thClass: 'text-end', tdClass: 'text-end', thStyle: { width: '100px' } },
        { key: 'total', label: 'Total', sortable: true, thClass: 'text-end', tdClass: 'text-end', thStyle: { width: '120px' } },
        { key: 'actions', label: 'Actions', thClass: 'text-center', tdClass: 'text-center', thStyle: { width: '200px' } },
      ],
    };
  },
  watch: {
    eventId: {
      immediate: true,
      async handler(newVal) {
        if (newVal) {
          await this.loadWorkAccountId();
          this.getContracts();
        }
      },
    },
  },
  methods: {
    hasPermission(permission) {
      const userPermissions = JSON.parse(localStorage.getItem('userPermissions'));
      return userPermissions && userPermissions.permissions.includes(permission);
    },
    async loadWorkAccountId() {
      try {
        const { data } = await axios.get(`/api/event/${this.eventId}/`);
        if (data && data.work_account) {
          this.workAccountId = data.work_account;
        }
      } catch (e) {
        console.error('Error fetching event data for contracts:', e);
      }
    },
    async getContracts() {
      this.loading = true;
      try {
        // Primero obtener los IDs de contratos del evento
        const resp = await axios.get(`/api/event/${this.eventId}/contracts/`);
        if (resp.status === 200) {
          const contractIds = resp.data || [];
          
          // Si solo tenemos IDs, obtener los detalles completos de cada contrato
          if (contractIds.length > 0 && typeof contractIds[0] === 'number') {
            const contractPromises = contractIds.map(id => 
              axios.get(`/api/contract/${id}/`).then(r => r.data).catch(() => null)
            );
            const contractsData = await Promise.all(contractPromises);
            this.contracts = contractsData.filter(c => c !== null);
          } else {
            // Si ya vienen como objetos completos
            this.contracts = contractIds;
          }
        }
      } catch (error) {
        console.error('Error fetching contracts:', error);
        this.contracts = [];
      } finally {
        this.loading = false;
      }
    },
    formatDate(dateString) {
      if (!dateString) return '—';
      return dayjs(dateString).format('MMM DD, YYYY');
    },
    currency(amount) {
      const num = Number(amount || 0);
      return num.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
    },
    viewContract(contractId) {
      this.$router.push({ name: 'contract-view', params: { id: contractId } });
    },
    editContract(contractId) {
      const url = this.$router.resolve({ name: 'contract-edit', params: { id: contractId } });
      window.open(url.href, '_blank');
    },
    async printContract(contractId) {
      try {
        const response = await axios.get(`/api/contract-pdf/${contractId}/`, {
          headers: {
            'Authorization': `Token ${localStorage.getItem('authToken')}`
          },
          responseType: 'json'
        });

        if (!response.data || !response.data.file) {
          throw new Error('No PDF file received');
        }

        // Decodificar base64 y crear blob
        const byteCharacters = atob(response.data.file);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
                         (window.innerWidth <= 768);

        if (isMobile) {
          // En móvil: descargar directamente
          const link = document.createElement('a');
          link.href = url;
          link.download = response.data.filename || `contract_${contractId}.pdf`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          this.notifyToastSuccess?.('PDF downloaded successfully.');
        } else {
          // En desktop: abrir en nueva ventana
          const newWindow = window.open(url, '_blank');
          if (!newWindow) {
            // Si no se puede abrir, descargar
            const link = document.createElement('a');
            link.href = url;
            link.download = response.data.filename || `contract_${contractId}.pdf`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            this.notifyToastSuccess?.('PDF downloaded successfully.');
          } else {
            this.notifyToastSuccess?.('PDF opened in new window.');
          }
        }
        
        // Limpiar la URL después de un tiempo
        setTimeout(() => {
          window.URL.revokeObjectURL(url);
        }, 1000);
        
      } catch (error) {
        console.error('Error downloading contract PDF:', error);
        await Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'Could not generate the PDF document. Please try again.',
          confirmButtonText: 'OK'
        });
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
          const query = { event_id: this.eventId };
          if (this.workAccountId) {
            query.work_account_id = this.workAccountId;
          }
          const resolved = this.$router.resolve({ 
            name: 'contract-form', 
            query 
          });
          const href = resolved?.href || `/contract-form?${new URLSearchParams(query).toString()}`;
          window.location.href = href;
        } catch (_) {
          const queryString = new URLSearchParams({
            event_id: this.eventId,
            ...(this.workAccountId && { work_account_id: this.workAccountId })
          }).toString();
          window.location.href = `/contract-form?${queryString}`;
        }
      });
    },
  },
};
</script>

<style scoped>
.house-contracts-container {
  padding: 0.5rem;
  min-height: 300px;
}

:deep(.table) {
  font-size: 0.875rem;
  margin-bottom: 0;
}

:deep(.table thead th) {
  background-color: #f8f9fa;
  font-weight: 600;
  border-bottom: 2px solid #dee2e6;
  vertical-align: middle;
}

:deep(.table tbody tr:hover) {
  background-color: #f8f9fa;
}

.btn-group-sm > .btn {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  border-radius: 0.2rem;
}

.btn-group-sm > .btn + .btn {
  margin-left: 0.25rem;
}
</style>

