<template>
  <div class="house-transactions-container">
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h5 class="mb-0">💰 Transactions</h5>
      <button @click="() => goToTransactionForm()" class="btn btn-success btn-sm">
        <i class="bi bi-plus-circle"></i> New Transaction
      </button>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2 text-muted">Loading transactions...</p>
    </div>

    <div v-else-if="transactions.length === 0" class="text-center py-5 text-muted">
      <i class="bi bi-inbox" style="font-size: 3rem; opacity: 0.3;"></i>
      <p class="mt-3">No transactions found for this work account.</p>
      <button @click="() => goToTransactionForm()" class="btn btn-primary btn-sm mt-2">
        Create First Transaction
      </button>
    </div>

    <div v-else>
      <!-- Search -->
      <div class="mb-3">
        <div class="input-group">
          <span class="input-group-text"><i class="bi bi-search"></i></span>
          <input
            v-model="search"
            type="text"
            class="form-control"
            placeholder="Search by type, notes..."
            autocomplete="off"
          />
          <button
            v-if="search"
            @click="search = ''"
            class="btn btn-outline-secondary"
            type="button">
            Clear
          </button>
        </div>
      </div>

      <!-- Transactions Table -->
      <BTable
        :items="filteredTransactions"
        :fields="fields"
        :per-page="perPage"
        :current-page="currentPage"
        bordered
        hover
        responsive
        striped
        small>
        <template #cell(document_type_code)="data">
          <span class="badge bg-info">{{ documentTypesMap[data.item.document_type] || '—' }}</span>
        </template>

        <template #cell(date)="data">
          {{ formatDate(data.item.date) }}
        </template>

        <template #cell(total_amount)="data">
          <span class="text-end fw-bold">{{ currency(data.item.total_amount) }}</span>
        </template>

        <template #cell(is_active)="data">
          <span v-if="data.item.is_active" class="badge bg-success">Active</span>
          <span v-else class="badge bg-secondary">Voided</span>
        </template>

        <template #cell(notes)="data">
          <span class="text-truncate d-inline-block" style="max-width: 200px;" :title="data.item.notes">
            {{ data.item.notes || '—' }}
          </span>
        </template>

        <template #cell(actions)="data">
          <div class="btn-group btn-group-sm" role="group">
            <button
              @click="() => goToTransactionForm(data.item.id, 'view')"
              class="btn btn-outline-success me-1"
              title="View">
              View
            </button>
            <button
              @click="() => printTransaction(data.item.id)"
              class="btn btn-outline-dark me-1" 
              title="Print PDF">
              Print
            </button>
            <button
              @click="() => goToTransactionForm(data.item.id)"
              class="btn btn-outline-primary me-1"
              title="Edit">
              Edit
            </button>
          </div>
        </template>
      </BTable>

      <!-- Pagination -->
      <div v-if="filteredTransactions.length > perPage" class="d-flex justify-content-end mt-3">
        <BPagination
          v-model="currentPage"
          :total-rows="filteredTransactions.length"
          :per-page="perPage"
          size="sm"
        />
      </div>
    </div>
  </div>
</template>

<script>
import { BTable, BPagination } from 'bootstrap-vue-next';
import axios from 'axios';
import Swal from 'sweetalert2';
import dayjs from 'dayjs';

export default {
  name: 'ScheduleHouseTransactionsComponent',
  components: {
    BTable,
    BPagination,
  },
  props: {
    eventId: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      transactions: [],
      documentTypesMap: {},
      loading: false,
      search: '',
      perPage: 10,
      currentPage: 1,
      workAccountId: null,
      fields: [
        { key: 'id', label: 'ID', sortable: true, thClass: 'text-center', tdClass: 'text-center', thStyle: { width: '60px' } },
        { key: 'document_type_code', label: 'Type', sortable: true, thStyle: { width: '100px' } },
        { key: 'date', label: 'Date', sortable: true, thClass: 'text-center', tdClass: 'text-center', thStyle: { width: '200px' } },
        { key: 'total_amount', label: 'Total', sortable: true, thClass: 'text-end', tdClass: 'text-end', thStyle: { width: '120px' } },
        { key: 'notes', label: 'Notes', thStyle: { width: '200px' } },
        { key: 'is_active', label: 'Status', thClass: 'text-center', tdClass: 'text-center', thStyle: { width: '80px' } },
        { key: 'actions', label: 'Actions', thClass: 'text-center', tdClass: 'text-center', thStyle: { width: '140px' } },
      ],
    };
  },
  computed: {
    filteredTransactions() {
      if (!this.search) return this.transactions;
      const q = this.search.toLowerCase();
      return this.transactions.filter(item => {
        const typeCode = this.documentTypesMap[item.document_type] || '';
        const notes = item.notes || '';
        return (
          typeCode.toLowerCase().includes(q) ||
          notes.toLowerCase().includes(q) ||
          item.id.toString().includes(q)
        );
      });
    },
  },
  watch: {
    eventId: {
      immediate: true,
      async handler(newVal) {
        if (newVal) {
          await this.loadWorkAccountId();
          if (this.workAccountId) {
            await Promise.all([this.fetchTransactions(), this.fetchDocumentTypes()]);
          } else {
            console.warn('No work_account found for event:', newVal);
            this.transactions = [];
            this.loading = false;
          }
        }
      },
    },
  },
  async mounted() {
    // La carga inicial se maneja en el watch de eventId
    if (this.eventId) {
      await this.loadWorkAccountId();
      if (this.workAccountId) {
        await Promise.all([this.fetchTransactions(), this.fetchDocumentTypes()]);
      }
    }
  },
  methods: {
    async loadWorkAccountId() {
      try {
        const { data } = await axios.get(`/api/event/${this.eventId}/`);
        console.log('🔍 Event data loaded:', { eventId: this.eventId, work_account: data?.work_account, fullData: data });
        
        if (data && data.work_account) {
          // Manejar tanto ID numérico como objeto con id
          if (typeof data.work_account === 'number') {
            this.workAccountId = data.work_account;
          } else if (typeof data.work_account === 'object' && data.work_account !== null && data.work_account.id) {
            this.workAccountId = data.work_account.id;
          } else {
            this.workAccountId = data.work_account;
          }
          console.log('✅ WorkAccount ID set to:', this.workAccountId, '(type:', typeof this.workAccountId, ')');
        } else {
          console.warn('⚠️ Event does not have a work_account. Data:', data);
          this.workAccountId = null;
        }
      } catch (e) {
        console.error('❌ Error fetching event data:', e);
        console.error('Error details:', e.response?.data || e.message);
        this.workAccountId = null;
      }
    },
    async fetchTransactions() {
      if (!this.workAccountId) {
        console.warn('Cannot fetch transactions: workAccountId is not set');
        this.transactions = [];
        this.loading = false;
        return;
      }
      
      this.loading = true;
      try {
        // Filtrar por work_account directamente en el query param
        const url = `/api/documents/?work_account=${this.workAccountId}&ordering=-id`;
        console.log('Fetching transactions from:', url);
        const response = await axios.get(url);
        const normalizeList = data => (Array.isArray(data) ? data : data?.results ?? []);
        const transactionsList = normalizeList(response.data);
        console.log(`Found ${transactionsList.length} transactions for work_account ${this.workAccountId}`);
        this.transactions = transactionsList;
      } catch (error) {
        console.error('Error fetching transactions:', error);
        console.error('Error details:', error.response?.data || error.message);
        this.notifyError?.('Error loading transactions.');
        this.transactions = [];
      } finally {
        this.loading = false;
      }
    },
    async fetchDocumentTypes() {
      try {
        const response = await axios.get('/api/document-types/?ordering=type_code');
        const normalizeList = data => (Array.isArray(data) ? data : data?.results ?? []);
        const arr = normalizeList(response.data);
        this.documentTypesMap = Object.fromEntries(arr.map(dt => [dt.id, dt.type_code]));
      } catch (error) {
        console.error('Error fetching document types:', error);
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
    async goToTransactionForm(transactionId = null, mode = null) {
      // Validar que transactionId sea un número válido y no un objeto PointerEvent
      if (transactionId !== null && transactionId !== undefined) {
        if (typeof transactionId === 'object' || isNaN(Number(transactionId))) {
          console.warn('⚠️ transactionId inválido (probablemente un PointerEvent):', transactionId);
          transactionId = null;
          mode = null;
        } else {
          transactionId = Number(transactionId);
        }
      }
      
      // Asegurar que workAccountId esté cargado antes de navegar
      if (!this.workAccountId && this.eventId) {
        console.log('🔍 workAccountId no disponible, cargando...');
        await this.loadWorkAccountId();
      }
      
      // Limpia backdrops y clases CSS residuales antes de navegar
      // La navegación con window.location.href cerrará automáticamente el ScheduleEventModal
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
      
      // Construir query params (similar a contracts)
      const queryParams = new URLSearchParams();
      
      // Siempre incluir event_id si está disponible
      if (this.eventId) {
        queryParams.append('event_id', String(this.eventId));
      }
      
      // Agregar id y mode solo si transactionId es un número válido
      if (transactionId !== null && transactionId !== undefined && !isNaN(transactionId)) {
        queryParams.append('id', String(transactionId));
        if (mode) {
          queryParams.append('mode', String(mode));
        }
      }
      
      // Agregar work_account_id solo si está disponible y es válido
      if (this.workAccountId !== null && this.workAccountId !== undefined) {
        const workAccountIdStr = String(this.workAccountId);
        if (workAccountIdStr && workAccountIdStr !== 'null' && workAccountIdStr !== 'undefined') {
          queryParams.append('work_account_id', workAccountIdStr);
          console.log('✅ Navegando con work_account_id:', this.workAccountId);
        }
      } else {
        console.warn('⚠️ No work_account_id disponible para el evento:', this.eventId);
      }
      
      const queryString = queryParams.toString();
      const url = `/transactions/form${queryString ? `?${queryString}` : ''}`;
      
      console.log('🚀 Navegando a:', url);
      
      // Navegación
      this.$nextTick(() => {
        window.location.href = url;
      });
    },
    async printTransaction(documentId) {
      try {
        const response = await axios.get(`/api/documents/${documentId}/pdf/`, {
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
          link.download = response.data.filename || `transaction_${documentId}.pdf`;
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
            link.download = response.data.filename || `transaction_${documentId}.pdf`;
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
        console.error('Error downloading PDF:', error);
        await Swal.fire({
          icon: 'error',
          title: 'Error',
          text: 'Could not generate the PDF document. Please try again.',
          confirmButtonText: 'OK'
        });
      }
    },
  },
};
</script>

<style scoped>
.house-transactions-container {
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

:deep(.table-responsive) {
  border-radius: 0.375rem;
  border: 1px solid #dee2e6;
}

/* Badge styles */
.badge {
  font-size: 0.75rem;
  padding: 0.35em 0.65em;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .house-transactions-container {
    padding: 0.25rem;
  }
  
  :deep(.table) {
    font-size: 0.8rem;
  }
  
  :deep(.btn-group-sm .btn) {
    padding: 0.2rem 0.4rem;
    font-size: 0.8rem;
  }
}
</style>

