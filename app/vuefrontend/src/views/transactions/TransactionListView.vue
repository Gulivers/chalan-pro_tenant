<template>
  <TxCard class="shadow-sm mt-0">
    <!-- Header del card -->
    <template #header>
      <div class="d-flex justify-content-between align-items-center w-100">
        <h6 class="text-primary mb-0">Transactions</h6>
        <router-link to="/transactions/form" class="btn btn-success">+ New Transaction</router-link>
      </div>
    </template>

    <!-- Filtros -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <!-- entries per page (izq) -->
      <div class="col-md-3">
        <div class="input-group">
          <select v-model="perPage" class="form-select">
            <option v-for="n in [5, 10, 25, 50]" :key="n" :value="n">{{ n }}</option>
          </select>
          <span class="text-primary p-2">entries per page</span>
        </div>
      </div>

      <!-- search (der) -->
      <div class="col-md-4">
        <div class="d-flex align-items-center gap-2">
          <span class="text-primary p-2">Search:</span>
          <div class="search-wrapper flex-grow-1">
            <input
              v-model="search"
              type="text"
              class="form-control"
              placeholder="Search by document type, party, notes..."
              autocomplete="off" />
            <button
              v-show="search && search.length"
              @mousedown.prevent
              @click="search = ''"
              type="button"
              class="btn-clear-x"
              title="Clear">
              ×
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- tabla -->
    <b-table
      :items="filteredItems"
      :fields="fields"
      :per-page="perPage"
      :current-page="currentPage"
      bordered
      hover
      responsive
      striped>
      <template #cell(document_type_code)="data">
        {{ documentTypesMap[data.item.document_type] || '—' }}
      </template>

      <template #cell(party_name)="data">
        {{ partiesMap[data.item.party] || '—' }}
      </template>

      <template #cell(work_account_display)="data">
        {{ workAccountsMap[data.item.work_account] || '—' }}
      </template>

      <template #cell(date)="data">
        {{ formatDate(data.item.date) }}
      </template>

      <template #cell(total_amount)="data">
        <span class="text-end">{{ currency(data.item.total_amount) }}</span>
      </template>

      <template #cell(total_discount)="data">
        <span class="text-end">{{ currency(data.item.total_discount) }}</span>
      </template>

      <template #cell(is_active)="data">
        <td class="text-center">
          <span v-if="data.item.is_active" class="badge bg-success">Active</span>
          <span v-else class="badge bg-secondary">Voided</span>
        </td>
      </template>

      <template #cell(lines_count)="data">
        <td class="text-center">
          <span class="badge bg-info">{{ data.item.lines?.length || 0 }}</span>
        </td>
      </template>

      <template #cell(actions)="data">
        <td class="text-center">
          <div class="btn-group btn-group-sm" role="group">
            <router-link :to="`/transactions/form?id=${data.item.id}&mode=view`" class="btn btn-outline-success me-1">
              View 
            </router-link>
            <button
              @click="printTransaction(data.item.id)"
              class="btn btn-outline-dark me-1">
              Print
            </button>
            <router-link :to="`/transactions/form?id=${data.item.id}`" class="btn btn-outline-primary me-1">
              Edit
            </router-link>
            <button
              @click="deleteTransaction(data.item.id, data.item.document_type_code)"
              class="btn btn-outline-danger">
              Delete
            </button>
          </div>
        </td>
      </template>
    </b-table>

    <!-- paginación a la derecha -->
    <div class="d-flex justify-content-end mt-3">
      <b-pagination v-model="currentPage" :total-rows="filteredItems.length" :per-page="perPage" />
    </div>
  </TxCard>
</template>

<script setup>
  import TxCard from '@/components/layout/TxCard.vue';
  import '@/assets/css/base.css';

  import { ref, computed, onMounted, getCurrentInstance } from 'vue';
  import axios from 'axios';
  import Swal from 'sweetalert2';

  const { proxy } = getCurrentInstance();

  const transactions = ref([]);
  const documentTypesMap = ref({}); // id -> type_code
  const partiesMap = ref({}); // id -> name
  const workAccountsMap = ref({}); // id -> display
  const search = ref('');
  const perPage = ref(10);
  const currentPage = ref(1);

  const fields = [
    { key: 'id', label: 'ID', sortable: true, thClass: 'text-center', tdClass: 'text-center' },
    { key: 'document_type_code', label: 'Type', sortable: true },
    { key: 'party_name', label: 'Party', sortable: true },
    { key: 'work_account_display', label: 'Work Account', sortable: true },
    { key: 'date', label: 'Date', sortable: true, thClass: 'text-center', tdClass: 'text-center' },
    // { key: 'lines_count', label: 'Lines', thClass: 'text-center', tdClass: 'text-center', sortable: true },
    { key: 'total_amount', label: 'Total', sortable: true, thClass: 'text-end', tdClass: 'text-end' },
    { key: 'total_discount', label: 'Discount', sortable: true, thClass: 'text-end', tdClass: 'text-end' },
    { key: 'is_active', label: 'Status', thClass: 'text-center', tdClass: 'text-center', sortable: true },
    { key: 'actions', label: 'Actions', thClass: 'text-center', tdClass: 'text-center' },
  ];

  // Helpers para DRF con o sin paginación
  const normalizeList = data => (Array.isArray(data) ? data : data?.results ?? []);

  const fetchTransactions = async () => {
    try {
      const res = await axios.get('/api/documents/?ordering=-id');
      transactions.value = normalizeList(res.data);
    } catch (err) {
      console.error('Error fetching transactions', err);
      proxy?.notifyError?.('Error loading transactions.');
    }
  };

  const fetchDocumentTypes = async () => {
    try {
      const res = await axios.get('/api/document-types/?ordering=type_code');
      const arr = normalizeList(res.data);
      documentTypesMap.value = Object.fromEntries(arr.map(dt => [dt.id, dt.type_code]));
    } catch (err) {
      console.error('Error fetching document types', err);
      proxy?.notifyError?.('Error loading document types.');
    }
  };

  const fetchParties = async () => {
    try {
      const res = await axios.get('/api/parties/?ordering=name');
      const arr = normalizeList(res.data);
      partiesMap.value = Object.fromEntries(arr.map(p => [p.id, p.name]));
    } catch (err) {
      console.error('Error fetching parties', err);
      proxy?.notifyError?.('Error loading parties.');
    }
  };

  const fetchWorkAccounts = async () => {
    try {
      const res = await axios.get('/api/work-accounts/?ordering=-id');
      const arr = normalizeList(res.data);
      workAccountsMap.value = Object.fromEntries(arr.map(wa => [wa.id, wa.title]));
    } catch (err) {
      console.error('Error fetching work accounts', err);
      proxy?.notifyError?.('Error loading work accounts.');
    }
  };

  onMounted(async () => {
    await Promise.all([fetchTransactions(), fetchDocumentTypes(), fetchParties(), fetchWorkAccounts()]);
  });

  const filteredItems = computed(() => {
    if (!search.value) return transactions.value;
    const q = search.value.toLowerCase();
    return transactions.value.filter(item => {
      const hay = [
        documentTypesMap.value[item.document_type] || '',
        partiesMap.value[item.party] || '',
        workAccountsMap.value[item.work_account] || '',
        item.notes || '',
      ].map(v => (v || '').toString().toLowerCase());
      return hay.some(t => t.includes(q));
    });
  });

  const formatDate = dateString => {
    if (!dateString) return '—';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
    });
  };

  const currency = amount => {
    const num = Number(amount || 0);
    return num.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
  };

  const deleteTransaction = (id, documentTypeCode) => {
    proxy?.confirmDelete?.(
      'Are you sure?',
      `Delete transaction "${documentTypeCode}"? This action cannot be undone.`,
      async () => {
        try {
          await axios.delete(`/api/documents/${id}/`);
          transactions.value = transactions.value.filter(t => t.id !== id);
          proxy?.notifyToastSuccess?.('The transaction has been deleted.');
        } catch (err) {
          console.error('Error deleting transaction', err);
          // Manejo de tu custom_exception_handler (409 in use)
          const detail = err?.response?.data?.detail || 'Error deleting the transaction.';
          proxy?.notifyError?.(detail);
        }
      }
    );
  };

  // Función helper para detectar si es dispositivo móvil
  const isMobileDevice = () => {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
           (window.innerWidth <= 768);
  };

  // Función para imprimir PDF de transacción
  const printTransaction = async (documentId) => {
    try {
      const response = await axios.get(`/api/documents/${documentId}/pdf/`, {
        headers: {
          'Authorization': `Token ${localStorage.getItem('authToken')}`
        }
      });

      if (!response.data || !response.data.file) {
        throw new Error('No se recibió el archivo PDF');
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
      
      if (isMobileDevice()) {
        // En móvil: descargar directamente
        const link = document.createElement('a');
        link.href = url;
        link.download = response.data.filename || `transaction_${documentId}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        proxy?.notifyToastSuccess?.('PDF generated and downloaded successfully.');
      } else {
        // En desktop: abrir en nueva ventana
        const newWindow = window.open(url, '_blank');
        if (!newWindow) {
          // Si no se puede abrir nueva ventana (bloqueador de popups), descargar
          const link = document.createElement('a');
          link.href = url;
          link.download = response.data.filename || `transaction_${documentId}.pdf`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          proxy?.notifyToastSuccess?.('PDF generated and downloaded successfully.');
        } else {
          proxy?.notifyToastSuccess?.('PDF opened in new window.');
        }
      }
      
      // Limpiar la URL después de un tiempo
      setTimeout(() => {
        window.URL.revokeObjectURL(url);
      }, 1000);
      
    } catch (error) {
      console.error('Error al descargar PDF:', error);
      await Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Could not generate the PDF document. Please try again.',
        confirmButtonText: 'OK'
      });
    }
  };
</script>

<style scoped>
  /* Reusa estilos de PartyListView: clear de input */
  .search-wrapper {
    position: relative;
  }
  .btn-clear-x {
    position: absolute;
    right: 0.5rem;
    top: 50%;
    transform: translateY(-50%);
    border: none;
    background: transparent;
    font-size: 1.25rem;
    line-height: 1;
  }
</style>
