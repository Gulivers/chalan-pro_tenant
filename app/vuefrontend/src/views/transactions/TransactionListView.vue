<template>
  <TxCard class="shadow-sm mt-0">
    <!-- Header del card -->
    <template #header>
      <div
        class="d-flex flex-wrap justify-content-between align-items-center w-100 gap-2">
        <h5 class="text-primary mb-0 fw-semibold listview-title">
          Transactions
        </h5>
        <router-link
          v-if="hasPermission('apptransactions.add_document')"
          to="/transactions/form"
          class="btn btn-success btn-sm">
          + New Transaction
        </router-link>
      </div>
    </template>

    <!-- Toolbar: stats + refresh -->
    <div
      class="listview-toolbar d-flex flex-wrap align-items-center gap-2 mb-3">
      <span class="badge bg-primary stats-badge">{{ stats.total }} Total</span>
      <span class="badge bg-success stats-badge">
        {{ stats.active }} Active
      </span>
      <span class="badge bg-secondary stats-badge">
        {{ stats.inactive }} Voided
      </span>
      <span
        class="listview-toolbar-divider d-none d-sm-inline"
        aria-hidden="true"></span>
      <button
        type="button"
        class="btn btn-outline-success btn-sm listview-refresh-btn"
        @click.prevent="refreshList">
        Refresh List
      </button>
    </div>

    <!-- Filters: entries per page + search -->
    <div class="listview-filters row g-2 g-md-3 mb-3 align-items-end">
      <div class="col-12 col-sm-6 col-lg-4 col-xl-3">
        <label
          for="per-page-select"
          class="form-label small listview-filter-label mb-1">
          Entries per page:
        </label>
        <select
          id="per-page-select"
          v-model="perPage"
          class="form-select form-select-sm">
          <option v-for="n in [10, 25, 50, 100]" :key="n" :value="n">
            {{ n }}
          </option>
        </select>
      </div>
      <div class="col-12 col-sm-6 col-lg-5 col-xl-4 ms-lg-auto">
        <label
          for="search-input"
          class="form-label small listview-filter-label mb-1">
          Search:
        </label>
        <div class="search-wrapper position-relative">
          <input
            id="search-input"
            v-model="search"
            type="text"
            class="form-control form-control-sm"
            :placeholder="
              smartSearch ? smartSearchPlaceholder : classicSearchPlaceholder
            "
            autocomplete="off"
            @input="onSearchInput" />
          <button
            v-show="search && search.length"
            @mousedown.prevent
            @click="clearSearch"
            type="button"
            class="btn-clear-x"
            title="Clear">
            ×
          </button>
        </div>
        <div class="form-check form-check-sm mt-1">
          <input
            id="smart-search-toggle"
            v-model="smartSearch"
            class="form-check-input"
            type="checkbox"
            @change="onSmartSearchToggle" />
          <label
            class="form-check-label small text-muted"
            for="smart-search-toggle">
            Smart search (AI)
          </label>
        </div>
        <div
          v-if="smartSearch && searchMeta.summary"
          class="small text-muted mt-1">
          {{ searchMeta.summary }}
        </div>
      </div>
    </div>

    <!-- Main Table with Overlay -->
    <BOverlay
      :show="isLoading || smartSearchLoading || similarSearchLoading"
      rounded="sm"
      opacity="0.85"
      variant="light">
      <template #overlay>
        <div class="text-center">
          <BSpinner type="border" variant="secondary" class="mb-3" />
          <div class="h5 text-primary">Loading Transactions...</div>
          <div class="text-muted">Please wait while we fetch the data</div>
        </div>
      </template>

      <BTable
        ref="transactionTable"
        :provider="provider"
        :fields="fields"
        :filter="tableFilter"
        :per-page="perPage"
        :current-page="currentPage"
        no-provider-sorting
        bordered
        hover
        responsive
        striped>
        <template #cell(document_type_code)="data">
          {{ data.item.document_type_code || "—" }}
        </template>

        <template #cell(builder_name)="data">
          {{ data.item.builder_name || "—" }}
        </template>

        <template #cell(work_account_display)="data">
          {{ data.item.work_account_display || "—" }}
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
          <span
            v-if="data.item.is_active"
            class="badge bg-success">
            Active
          </span>
          <span v-else class="badge bg-secondary">Voided</span>
        </template>

        <template #cell(actions)="data">
          <div class="btn-group btn-group-sm" role="group">
            <router-link
              v-if="hasPermission('apptransactions.view_document')"
              :to="`/transactions/form?id=${data.item.id}&mode=view`"
              class="btn btn-outline-success me-1">
              View
            </router-link>
            <button
              v-if="hasPermission('apptransactions.view_document')"
              @click="findSimilarTransactions(data.item.id)"
              class="btn btn-outline-info me-1"
              title="Find similar transactions">
              Similar
            </button>
            <button
              v-if="hasPermission('apptransactions.view_document')"
              @click="printTransaction(data.item.id)"
              class="btn btn-outline-dark me-1">
              Print
            </button>
            <router-link
              v-if="hasPermission('apptransactions.change_document')"
              :to="`/transactions/form?id=${data.item.id}`"
              class="btn btn-outline-primary me-1">
              Edit
            </router-link>
            <button
              v-if="hasPermission('apptransactions.delete_document')"
              @click="
                deleteTransaction(data.item.id, data.item.document_type_code)
              "
              class="btn btn-outline-danger">
              Delete
            </button>
          </div>
        </template>
      </BTable>

      <div class="d-flex justify-content-end mt-3">
        <BPagination
          v-model="currentPage"
          :total-rows="totalRows"
          :per-page="perPage" />
      </div>
    </BOverlay>
  </TxCard>
</template>

<script setup>
import TxCard from "@/components/layout/TxCard.vue";
import "@/assets/css/base.css";

import {
  ref,
  computed,
  nextTick,
  onBeforeUnmount,
  getCurrentInstance,
} from "vue";
import axios from "axios";
import Swal from "sweetalert2";
import { BOverlay, BSpinner, BTable, BPagination } from "bootstrap-vue-next";

const ENDPOINT = "/api/documents-provider/";

const { proxy } = getCurrentInstance();

const transactionTable = ref(null);
const isLoading = ref(true);
const stats = ref({ total: 0, active: 0, inactive: 0 });
const totalRows = ref(0);
const search = ref("");
const smartSearch = ref(false);
const smartSearchLoading = ref(false);
const smartSearchDocumentIds = ref(null);
const similarSearchDocumentIds = ref(null);
const similarSearchLoading = ref(false);
const searchMeta = ref({ summary: "" });
const searchDebounceTimer = ref(null);
const classicSearchPlaceholder =
  "Search by document type, party, notes...";
const smartSearchPlaceholder =
  "e.g. Harbor Freight purchases over $500, breakers for Pulte...";
const perPage = ref(25);
const currentPage = ref(1);

const fields = [
  {
    key: "id",
    label: "ID",
    sortable: true,
    thClass: "text-center",
    tdClass: "text-center",
  },
  {
    key: "document_type_code",
    label: "Type",
    sortable: true,
    thClass: "text-start",
    tdClass: "text-start",
  },
  {
    key: "builder_name",
    label: "Party",
    sortable: true,
    thClass: "text-start",
    tdClass: "text-start",
  },
  {
    key: "work_account_display",
    label: "Work Account",
    sortable: true,
    thClass: "text-start",
    tdClass: "text-start",
  },
  {
    key: "date",
    label: "Date",
    sortable: true,
    thClass: "text-center",
    tdClass: "text-center",
  },
  {
    key: "total_amount",
    label: "Total",
    sortable: true,
    thClass: "text-end",
    tdClass: "text-end",
  },
  {
    key: "total_discount",
    label: "Discount",
    sortable: true,
    thClass: "text-end",
    tdClass: "text-end",
  },
  {
    key: "is_active",
    label: "Status",
    thClass: "text-center",
    tdClass: "text-center",
    sortable: true,
  },
  {
    key: "actions",
    label: "Actions",
    thClass: "text-center",
    tdClass: "text-center",
    thStyle: { width: "12%", whiteSpace: "nowrap" },
    tdStyle: { whiteSpace: "nowrap" },
  },
];

const tableFilter = computed(() => {
  if (smartSearch.value || Array.isArray(similarSearchDocumentIds.value)) {
    return "";
  }
  return search.value;
});

const provider = async (context) => {
  try {
    if (!isLoading.value) {
      isLoading.value = true;
    }

    const page = context.currentPage || 1;
    const perPageValue = context.perPage || 25;
    const params = new URLSearchParams({
      page: String(page),
      per_page: String(perPageValue),
      ordering: "-id",
    });

    if (smartSearch.value && Array.isArray(smartSearchDocumentIds.value)) {
      if (!smartSearchDocumentIds.value.length) {
        stats.value = { total: 0, active: 0, inactive: 0 };
        totalRows.value = 0;
        return [];
      }
      params.set("document_ids", smartSearchDocumentIds.value.join(","));
    } else if (Array.isArray(similarSearchDocumentIds.value)) {
      if (!similarSearchDocumentIds.value.length) {
        stats.value = { total: 0, active: 0, inactive: 0 };
        totalRows.value = 0;
        return [];
      }
      params.set("document_ids", similarSearchDocumentIds.value.join(","));
    } else {
      const classicSearch = search.value.trim();
      if (classicSearch) {
        params.set("search", classicSearch);
      }
    }

    const response = await axios.get(`${ENDPOINT}?${params}`);

    if (response.data?.items) {
      if (response.data.stats) {
        stats.value = response.data.stats;
      }
      totalRows.value = response.data.totalRows || 0;
      return response.data.items;
    }

    throw new Error("Invalid response format");
  } catch (err) {
    console.error("Error loading transactions:", err);
    proxy?.notifyError?.("Error loading transactions.");
    return [];
  } finally {
    setTimeout(() => {
      isLoading.value = false;
    }, 300);
  }
};

const refreshList = () => {
  isLoading.value = true;
  transactionTable.value?.refresh();
};

const buildSearchSummary = (payload) => {
  if (payload?.notice) {
    return payload.notice;
  }
  const parts = [];
  if (payload?.count != null) {
    parts.push(`${payload.count} match${payload.count === 1 ? "" : "es"}`);
  }
  const builder = payload?.resolved_entities?.builder?.name;
  const workAccount = payload?.resolved_entities?.work_account?.title;
  const docType = payload?.resolved_entities?.document_type?.type_code;
  if (workAccount) parts.push(`Work Account: ${workAccount}`);
  if (builder) parts.push(`Party: ${builder}`);
  if (docType) parts.push(`Type: ${docType}`);
  const filters = payload?.applied_filters || {};
  if (filters.document_total_gte != null) {
    parts.push(`Doc total >= $${filters.document_total_gte}`);
  }
  if (filters.line_final_price_gte != null) {
    parts.push(`Line >= $${filters.line_final_price_gte}`);
  }
  if (filters.date_from || filters.date_to) {
    parts.push(`${filters.date_from || "…"} → ${filters.date_to || "…"}`);
  }
  return parts.join(" · ");
};

const runSmartSearch = async (query) => {
  similarSearchDocumentIds.value = null;
  smartSearchLoading.value = true;
  try {
    const response = await axios.post("/api/search/transactions/", {
      query,
      limit: 100,
    });
    smartSearchDocumentIds.value = response.data?.document_ids || [];
    searchMeta.value = {
      summary: buildSearchSummary(response.data),
    };
    currentPage.value = 1;
    transactionTable.value?.refresh();
  } catch (err) {
    smartSearchDocumentIds.value = [];
    searchMeta.value = { summary: "" };
    const detail =
      err?.response?.data?.detail ||
      "Smart search is unavailable. Check the search index and OpenAI configuration.";
    proxy?.notifyError?.(
      typeof detail === "string" ? detail : "Smart search failed."
    );
    transactionTable.value?.refresh();
  } finally {
    smartSearchLoading.value = false;
  }
};

const findSimilarTransactions = async (documentId) => {
  smartSearch.value = false;
  smartSearchDocumentIds.value = null;
  search.value = "";
  similarSearchLoading.value = true;
  try {
    const response = await axios.post("/api/search/transactions/similar/", {
      document_id: documentId,
      limit: 50,
    });
    similarSearchDocumentIds.value = response.data?.document_ids || [];
    const seedSnippet = response.data?.seed?.snippet || "";
    const count = response.data?.count ?? 0;
    searchMeta.value = {
      summary: `Similar to #${documentId}: ${count} match${count === 1 ? "" : "es"}${seedSnippet ? ` · ${seedSnippet.slice(0, 80)}` : ""}`,
    };
    currentPage.value = 1;
    transactionTable.value?.refresh();
  } catch (err) {
    similarSearchDocumentIds.value = null;
    searchMeta.value = { summary: "" };
    const detail =
      err?.response?.data?.detail ||
      "Similar search is unavailable. Reindex document lines if needed.";
    proxy?.notifyError?.(
      typeof detail === "string" ? detail : "Similar search failed."
    );
  } finally {
    similarSearchLoading.value = false;
  }
};

const resetToDefaultList = async () => {
  if (searchDebounceTimer.value) {
    clearTimeout(searchDebounceTimer.value);
    searchDebounceTimer.value = null;
  }
  smartSearchDocumentIds.value = null;
  similarSearchDocumentIds.value = null;
  searchMeta.value = { summary: "" };
  currentPage.value = 1;
  await nextTick();
  refreshList();
};

const onSearchInput = () => {
  similarSearchDocumentIds.value = null;
  if (!smartSearch.value) {
    searchMeta.value = { summary: "" };
    if (!search.value.trim()) {
      resetToDefaultList();
    }
    return;
  }

  if (searchDebounceTimer.value) {
    clearTimeout(searchDebounceTimer.value);
  }

  const query = search.value.trim();
  if (!query) {
    resetToDefaultList();
    return;
  }

  searchDebounceTimer.value = setTimeout(() => {
    runSmartSearch(query);
  }, 450);
};

const onSmartSearchToggle = () => {
  similarSearchDocumentIds.value = null;
  smartSearchDocumentIds.value = null;
  searchMeta.value = { summary: "" };
  if (smartSearch.value && search.value.trim()) {
    runSmartSearch(search.value.trim());
  } else {
    transactionTable.value?.refresh();
  }
};

const clearSearch = async () => {
  search.value = "";
  await resetToDefaultList();
};

onBeforeUnmount(() => {
  if (searchDebounceTimer.value) {
    clearTimeout(searchDebounceTimer.value);
  }
});

const formatDate = (dateString) => {
  if (!dateString) return "—";
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
};

const currency = (amount) => {
  const num = Number(amount || 0);
  return num.toLocaleString("en-US", { style: "currency", currency: "USD" });
};

const deleteTransaction = (id, documentTypeCode) => {
  proxy?.confirmDelete?.(
    "Are you sure?",
    `Delete transaction "${documentTypeCode}"? This action cannot be undone.`,
    async () => {
      try {
        await axios.delete(`/api/documents/${id}/`);
        proxy?.notifyToastSuccess?.("The transaction has been deleted.");
        refreshList();
      } catch (err) {
        console.error("Error deleting transaction", err);
        const detail =
          err?.response?.data?.detail || "Error deleting the transaction.";
        proxy?.notifyError?.(detail);
      }
    }
  );
};

const isMobileDevice = () => {
  return (
    /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
      navigator.userAgent
    ) || window.innerWidth <= 768
  );
};

const printTransaction = async (documentId) => {
  try {
    const response = await axios.get(`/api/documents/${documentId}/pdf/`, {
      headers: {
        Authorization: `Token ${localStorage.getItem("authToken")}`,
      },
    });

    if (!response.data || !response.data.file) {
      throw new Error("No se recibió el archivo PDF");
    }

    const byteCharacters = atob(response.data.file);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    const blob = new Blob([byteArray], { type: "application/pdf" });
    const url = window.URL.createObjectURL(blob);

    if (isMobileDevice()) {
      const link = document.createElement("a");
      link.href = url;
      link.download = response.data.filename || `transaction_${documentId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      proxy?.notifyToastSuccess?.("PDF generated and downloaded successfully.");
    } else {
      const newWindow = window.open(url, "_blank");
      if (!newWindow) {
        const link = document.createElement("a");
        link.href = url;
        link.download =
          response.data.filename || `transaction_${documentId}.pdf`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        proxy?.notifyToastSuccess?.(
          "PDF generated and downloaded successfully."
        );
      } else {
        proxy?.notifyToastSuccess?.("PDF opened in new window.");
      }
    }

    setTimeout(() => {
      window.URL.revokeObjectURL(url);
    }, 1000);
  } catch (error) {
    console.error("Error al descargar PDF:", error);
    await Swal.fire({
      icon: "error",
      title: "Error",
      text: "Could not generate the PDF document. Please try again.",
      confirmButtonText: "OK",
    });
  }
};
</script>

<style scoped>
.listview-title {
  font-size: 1.1rem;
  letter-spacing: -0.01em;
}
.listview-toolbar {
  padding: 0.5rem 0.75rem;
  background-color: rgba(13, 110, 253, 0.06);
  border: 1px solid rgba(13, 110, 253, 0.12);
  border-radius: 0.375rem;
}
.listview-toolbar .stats-badge {
  font-size: 0.7rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  line-height: 1.2;
}
.listview-toolbar-divider {
  width: 1px;
  height: 1.25rem;
  background-color: rgba(0, 0, 0, 0.12);
  margin: 0 0.15rem;
}
.listview-refresh-btn {
  padding: 0.2rem 0.6rem;
  font-size: 0.8rem;
}
.listview-filter-label {
  font-size: 0.8rem;
  color: var(--bs-secondary-color);
}
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
