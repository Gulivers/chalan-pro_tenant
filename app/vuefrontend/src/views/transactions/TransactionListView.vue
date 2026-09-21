<template>
  <JRPage>
    <JRPageHeader title="Transactions">
      <template #actions>
        <JRButton
          v-if="hasPermission('apptransactions.add_document')"
          type="button"
          @click="goToCreateForm">
          + New Transaction
        </JRButton>
      </template>
    </JRPageHeader>

    <JRToolbar>
      <template #start>
        <div class="jr-tx-list__search">
          <label class="jr-sr-only" for="tx-filter-input">
            Search transactions
          </label>
          <span class="jr-tx-list__search-icon" aria-hidden="true">
            <SearchIcon />
          </span>
          <JRInput
            inputId="tx-filter-input"
            v-model="filter"
            type="search"
            placeholder="Search by document type, party, notes…"
            autocomplete="off"
            :spellcheck="false"
            autocapitalize="none"
            autocorrect="off"
            enterkeyhint="search" />
        </div>
      </template>

      <template v-if="!isMobile" #stats>
        <div class="jr-tx-list__summary" aria-live="polite">
          <JRBadge :value="`${stats.total} Total`" severity="secondary" />
          <JRBadge
            :value="`${stats.active} Active`"
            :severity="stats.active > 0 ? 'success' : 'secondary'" />
          <JRBadge
            :value="`${stats.inactive} Voided`"
            severity="secondary" />
        </div>
      </template>

      <template #actions>
        <template v-if="!isMobile">
          <JRSelect
            class="jr-tx-list__entries"
            inputId="tx-per-page"
            ariaLabel="Entries per page"
            v-model="perPage"
            :options="pageOptions"
            optionLabel="label"
            optionValue="value" />
          <JRButton
            type="button"
            variant="ghost"
            size="sm"
            class="jr-tx-list__refresh"
            @click="refreshTable">
            <RefreshIcon />
            Refresh
          </JRButton>
        </template>
        <template v-else>
          <button
            id="tx-list-tools-trigger"
            type="button"
            class="jr-icon-btn"
            aria-label="List tools"
            aria-haspopup="menu"
            :aria-expanded="toolsMenuOpen ? 'true' : 'false'"
            aria-controls="tx-list-tools-menu"
            @click="toggleToolsMenu">
            <svg
              width="16"
              height="16"
              viewBox="0 0 16 16"
              aria-hidden="true"
              fill="currentColor">
              <circle cx="8" cy="3" r="1.4" />
              <circle cx="8" cy="8" r="1.4" />
              <circle cx="8" cy="13" r="1.4" />
            </svg>
          </button>
          <Menu
            id="tx-list-tools-menu"
            ref="toolsMenu"
            class="jr-overlay jr-row-menu"
            :model="toolsMenuModel"
            :popup="true"
            ariaLabel="List tools"
            @show="toolsMenuOpen = true"
            @hide="toolsMenuOpen = false" />
        </template>
      </template>
    </JRToolbar>

    <div v-if="isMobile" class="jr-tx-list__mobile">
      <JREmptyState
        v-if="!transactions.length && !isLoading"
        :title="emptyTitle"
        :description="emptyDescription">
        <JRButton
          v-if="loadError"
          type="button"
          variant="ghost"
          size="sm"
          @click="refreshTable">
          Refresh
        </JRButton>
        <JRButton
          v-else-if="hasSearch"
          type="button"
          variant="ghost"
          size="sm"
          @click="clearSearch">
          Clear search
        </JRButton>
      </JREmptyState>
      <p v-if="isLoading && !transactions.length" class="jr-tx-list__loading">
        Loading transactions…
      </p>
      <p
        v-else-if="isLoading && transactions.length"
        class="jr-tx-list__loading"
        aria-live="polite">
        Updating…
      </p>
      <ul
        v-if="transactions.length"
        class="jr-tx-list__rows"
        :aria-busy="isLoading ? 'true' : 'false'">
        <li v-for="item in transactions" :key="item.id" class="jr-tx-row">
          <div class="jr-tx-row__main">
            <router-link
              v-if="canView"
              class="jr-tx-row__name jr-tx-row__name--link"
              :to="transactionViewTo(item.id)"
              :aria-label="`View transaction ${item.id}`">
              {{ item.document_type_code || "—" }}
            </router-link>
            <span v-else class="jr-tx-row__name">
              {{ item.document_type_code || "—" }}
            </span>
            <p class="jr-tx-row__meta">
              <span>#{{ item.id }}</span>
              <span aria-hidden="true"> · </span>
              <span>{{ item.builder_name || "—" }}</span>
            </p>
            <p class="jr-tx-row__meta">
              <span>{{ item.work_account_display || "—" }}</span>
              <span aria-hidden="true"> · </span>
              <span>{{ formatDate(item.date) }}</span>
            </p>
            <p class="jr-tx-row__meta">
              <span class="jr-tx-row__amount">{{
                currency(item.total_amount)
              }}</span>
              <JRBadge
                :value="item.is_active ? 'Active' : 'Voided'"
                :severity="item.is_active ? 'success' : 'secondary'" />
            </p>
          </div>
          <div class="jr-tx-row__aside">
            <JRRowActions
              v-if="hasRowActions"
              :actions="getRowActions(item)"
              :compact="true"
              :entity-label="transactionLabel(item)" />
          </div>
        </li>
      </ul>
      <Paginator
        v-if="totalRows > 0"
        class="jr-tx-list__pager"
        :rows="perPage"
        :totalRecords="totalRows"
        :first="tableFirst"
        template="PrevPageLink CurrentPageReport NextPageLink"
        currentPageReportTemplate="{first}–{last} of {totalRecords}"
        @page="onTablePage" />
    </div>

    <div
      v-else
      class="jr-tx-list__table"
      :aria-busy="isLoading ? 'true' : 'false'">
      <JRDataTable
        :value="transactions"
        :loading="isLoading"
        dataKey="id"
        lazy
        :paginator="totalRows > 0"
        :rows="perPage"
        :totalRecords="totalRows"
        :first="tableFirst"
        :sortField="sortField"
        :sortOrder="sortOrder"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport"
        currentPageReportTemplate="{first}–{last} of {totalRecords}"
        scrollable
        stripedRows
        :tableStyle="tableMinWidth"
        :emptyTitle="isLoading ? '' : emptyTitle"
        :emptyDescription="isLoading ? '' : emptyDescription"
        @page="onTablePage"
        @sort="onTableSort">
        <template #empty>
          <JREmptyState
            v-if="!isLoading"
            :title="emptyTitle"
            :description="emptyDescription">
            <JRButton
              v-if="loadError"
              type="button"
              variant="ghost"
              size="sm"
              @click="refreshTable">
              Refresh
            </JRButton>
            <JRButton
              v-else-if="hasSearch"
              type="button"
              variant="ghost"
              size="sm"
              @click="clearSearch">
              Clear search
            </JRButton>
          </JREmptyState>
        </template>

        <Column field="document_type_code" header="Type">
          <template #body="{ data }">
            <router-link
              v-if="canView"
              class="jr-tx-row__name jr-tx-row__name--link"
              :to="transactionViewTo(data.id)"
              :aria-label="`View transaction ${data.id}`">
              {{ data.document_type_code || "—" }}
            </router-link>
            <strong v-else>{{ data.document_type_code || "—" }}</strong>
          </template>
        </Column>
        <Column field="builder_name" header="Party">
          <template #body="{ data }">
            {{ data.builder_name || "—" }}
          </template>
        </Column>
        <Column v-if="!isTablet" field="work_account_display" header="Work Account">
          <template #body="{ data }">
            {{ data.work_account_display || "—" }}
          </template>
        </Column>
        <Column field="date" header="Date" sortable>
          <template #body="{ data }">
            {{ formatDate(data.date) }}
          </template>
        </Column>
        <Column
          field="total_amount"
          header="Total"
          sortable
          headerClass="jr-col-num"
          bodyClass="jr-col-num">
          <template #body="{ data }">
            {{ currency(data.total_amount) }}
          </template>
        </Column>
        <Column
          v-if="!isTablet"
          field="total_discount"
          header="Discount"
          sortable
          headerClass="jr-col-num"
          bodyClass="jr-col-num">
          <template #body="{ data }">
            {{ currency(data.total_discount) }}
          </template>
        </Column>
        <Column field="is_active" header="Status">
          <template #body="{ data }">
            <JRBadge
              :value="data.is_active ? 'Active' : 'Voided'"
              :severity="data.is_active ? 'success' : 'secondary'" />
          </template>
        </Column>
        <Column
          v-if="hasRowActions"
          header="Actions"
          :sortable="false"
          :headerClass="
            isTablet
              ? 'jr-col-actions jr-col-actions--compact'
              : 'jr-col-actions'
          "
          :bodyClass="
            isTablet
              ? 'jr-col-actions jr-col-actions--compact'
              : 'jr-col-actions'
          ">
          <template #body="{ data }">
            <JRRowActions
              :actions="getRowActions(data)"
              :compact="isTablet"
              :entity-label="transactionLabel(data)" />
          </template>
        </Column>
      </JRDataTable>
    </div>
  </JRPage>
</template>

<script>
import { getAccessToken } from '@/auth/tokenHelpers';
import axios from "axios";
import {
  ref,
  computed,
  watch,
  onMounted,
  onUnmounted,
  getCurrentInstance,
} from "vue";
import { useRouter } from "vue-router";
import Column from "primevue/column";
import Menu from "primevue/menu";
import Paginator from "primevue/paginator";
import EyeIcon from "@primevue/icons/eye";
import PencilIcon from "@primevue/icons/pencil";
import RefreshIcon from "@primevue/icons/refresh";
import SearchIcon from "@primevue/icons/search";
import TrashIcon from "@primevue/icons/trash";
import UploadIcon from "@primevue/icons/upload";
import {
  JRPage,
  JRPageHeader,
  JRToolbar,
  JRButton,
  JRSelect,
  JRInput,
  JRBadge,
  JRDataTable,
  JREmptyState,
  JRRowActions,
} from "@ui";

const ENDPOINT = "/api/documents-provider/";
const PHONE_MQ = "(max-width: 767.98px)";
const TABLET_MQ = "(min-width: 768px) and (max-width: 1023.98px)";

function readViewport() {
  if (typeof window === "undefined" || !window.matchMedia) {
    return { isMobile: false, isTablet: false };
  }
  return {
    isMobile: window.matchMedia(PHONE_MQ).matches,
    isTablet: window.matchMedia(TABLET_MQ).matches,
  };
}

export default {
  name: "TransactionListView",
  components: {
    Column,
    Menu,
    Paginator,
    RefreshIcon,
    SearchIcon,
    JRPage,
    JRPageHeader,
    JRToolbar,
    JRButton,
    JRSelect,
    JRInput,
    JRBadge,
    JRDataTable,
    JREmptyState,
    JRRowActions,
  },

  setup() {
    const router = useRouter();
    const { proxy } = getCurrentInstance();

    const transactions = ref([]);
    const stats = ref({ total: 0, active: 0, inactive: 0 });
    const isLoading = ref(true);
    const loadError = ref(false);
    const currentPage = ref(1);
    const perPage = ref(25);
    const filter = ref("");
    const totalRows = ref(0);
    const sortField = ref("id");
    const sortOrder = ref(-1);
    const toolsMenu = ref(null);
    const toolsMenuOpen = ref(false);
    let searchTimer = null;

    const initialViewport = readViewport();
    const isMobile = ref(initialViewport.isMobile);
    const isTablet = ref(initialViewport.isTablet);
    let phoneQuery = null;
    let tabletQuery = null;
    let onViewport = null;

    const pageOptions = [
      { value: 10, label: "10" },
      { value: 25, label: "25" },
      { value: 50, label: "50" },
      { value: 100, label: "100" },
    ];

    const tableFirst = computed(() => (currentPage.value - 1) * perPage.value);
    const tableMinWidth = computed(() =>
      isTablet.value ? "min-width: 40rem" : "min-width: 56rem"
    );
    const hasSearch = computed(() =>
      Boolean(filter.value && filter.value.trim())
    );
    const emptyTitle = computed(() => {
      if (loadError.value) return "Could not load transactions";
      if (hasSearch.value) return "No matching transactions";
      return "No transactions";
    });
    const emptyDescription = computed(() => {
      if (loadError.value) return "Try Refresh.";
      const query = filter.value.trim();
      if (query) return `No transactions match “${query}”.`;
      return "No transactions yet.";
    });

    const canView = computed(() =>
      !!proxy?.hasPermission?.("apptransactions.view_document")
    );
    const hasRowActions = computed(
      () =>
        canView.value ||
        !!proxy?.hasPermission?.("apptransactions.change_document") ||
        !!proxy?.hasPermission?.("apptransactions.delete_document")
    );

    const clearSearch = () => {
      filter.value = "";
      if (typeof document !== "undefined") {
        document.getElementById("tx-filter-input")?.focus();
      }
    };

    const formatDate = (dateString) => {
      if (!dateString) return "—";
      // Parse YYYY-MM-DD as a local calendar date. `new Date('YYYY-MM-DD')` is UTC
      // midnight and shifts the day backward in US timezones (e.g. 2026-08-01 → 07/31).
      const raw = String(dateString).slice(0, 10);
      const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(raw);
      const date = match
        ? new Date(Number(match[1]), Number(match[2]) - 1, Number(match[3]))
        : new Date(dateString);
      if (Number.isNaN(date.getTime())) return "—";
      return date.toLocaleDateString("en-US", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      });
    };

    const currency = (amount) => {
      const num = Number(amount || 0);
      return num.toLocaleString("en-US", {
        style: "currency",
        currency: "USD",
      });
    };

    const getOrderingFromSortBy = ({ sortField: field, sortOrder: order }) => {
      const fieldMap = {
        id: "id",
        date: "date",
        total_amount: "total_amount",
        total_discount: "total_discount",
      };
      const djangoField = fieldMap[field];
      if (!djangoField) return "-id";
      return order === -1 ? `-${djangoField}` : djangoField;
    };

    const loadTransactions = async () => {
      if (!isLoading.value) isLoading.value = true;
      try {
        const params = new URLSearchParams({
          page: String(currentPage.value),
          per_page: String(perPage.value),
          ordering: getOrderingFromSortBy({
            sortField: sortField.value,
            sortOrder: sortOrder.value,
          }),
        });
        const classicSearch = filter.value.trim();
        if (classicSearch) {
          params.set("search", classicSearch);
        }
        const { data } = await axios.get(`${ENDPOINT}?${params}`);
        transactions.value = data.items || [];
        totalRows.value = data.totalRows || 0;
        if (data.stats) stats.value = data.stats;
        loadError.value = false;
      } catch (e) {
        console.error("documents provider error:", e);
        loadError.value = true;
        transactions.value = [];
        totalRows.value = 0;
        proxy?.notifyError?.("Error loading transactions.");
      } finally {
        setTimeout(() => {
          isLoading.value = false;
        }, 300);
      }
    };

    const onTablePage = (event) => {
      currentPage.value = (event.page ?? 0) + 1;
      if (event.rows && event.rows !== perPage.value) {
        perPage.value = event.rows;
      }
    };

    const onTableSort = (event) => {
      sortField.value = event.sortField || "id";
      sortOrder.value = event.sortOrder ?? -1;
      currentPage.value = 1;
    };

    const refreshTable = () => {
      isLoading.value = true;
      loadTransactions();
    };

    const goToCreateForm = () => {
      router.push({ name: "transactions-form" });
    };

    const transactionViewTo = (id) => ({
      name: "transactions-form",
      query: { id: String(id), mode: "view" },
    });

    const transactionEditTo = (id) => ({
      name: "transactions-form",
      query: { id: String(id) },
    });

    const transactionLabel = (item) =>
      item?.document_type_code
        ? `Transaction ${item.document_type_code}`
        : `Transaction ${item?.id ?? ""}`;

    const viewItem = (id) => router.push(transactionViewTo(id));
    const editItem = (id) => router.push(transactionEditTo(id));

    const isMobileUa = () =>
      /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator.userAgent
      ) || window.innerWidth <= 768;

    const printItem = async (documentId) => {
      try {
        const response = await axios.get(`/api/documents/${documentId}/pdf/`, {
          headers: {
            Authorization: `Bearer ${getAccessToken()}`,
          },
        });

        if (!response.data?.file) {
          throw new Error("No PDF file received");
        }

        const byteCharacters = atob(response.data.file);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i += 1) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: "application/pdf" });
        const url = window.URL.createObjectURL(blob);
        const filename =
          response.data.filename || `transaction_${documentId}.pdf`;

        if (isMobileUa()) {
          const link = document.createElement("a");
          link.href = url;
          link.download = filename;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          proxy?.notifyToastSuccess?.(
            "PDF generated and downloaded successfully."
          );
        } else {
          const newWindow = window.open(url, "_blank");
          if (!newWindow) {
            const link = document.createElement("a");
            link.href = url;
            link.download = filename;
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
        console.error("Error generating transaction PDF:", error);
        proxy?.notifyError?.(
          "Could not generate the PDF document. Please try again."
        );
      }
    };

    const deleteItem = (item) => {
      const label = item?.document_type_code || `#${item?.id}`;
      proxy?.confirmDelete?.(
        "Are you sure?",
        `Delete transaction "${label}"? This action cannot be undone.`,
        async () => {
          try {
            await axios.delete(`/api/documents/${item.id}/`);
            proxy?.notifyToastSuccess?.("The transaction has been deleted.");
            refreshTable();
          } catch (err) {
            console.error("Error deleting transaction", err);
            const detail =
              err?.response?.data?.detail || "Error deleting the transaction.";
            proxy?.notifyError?.(detail);
          }
        }
      );
    };

    const getRowActions = (item) => {
      const actions = [];
      if (proxy?.hasPermission?.("apptransactions.view_document")) {
        actions.push({
          key: "view",
          label: "View",
          severity: "success",
          icon: EyeIcon,
          command: () => viewItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("apptransactions.view_document")) {
        actions.push({
          key: "print",
          label: "Print",
          severity: "secondary",
          buttonClass: "jr-row-actions__btn--print",
          icon: UploadIcon,
          command: () => printItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("apptransactions.change_document")) {
        actions.push({
          key: "edit",
          label: "Edit",
          severity: "primary",
          icon: PencilIcon,
          command: () => editItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("apptransactions.delete_document")) {
        actions.push({
          key: "delete",
          label: "Delete",
          severity: "danger",
          icon: TrashIcon,
          command: () => deleteItem(item),
        });
      }
      return actions;
    };

    const toolsMenuModel = computed(() => [
      {
        label: "Refresh",
        icon: "pi pi-refresh",
        command: () => refreshTable(),
      },
    ]);

    const toggleToolsMenu = (event) => {
      toolsMenu.value?.toggle?.(event);
    };

    onMounted(() => {
      if (typeof window !== "undefined" && window.matchMedia) {
        phoneQuery = window.matchMedia(PHONE_MQ);
        tabletQuery = window.matchMedia(TABLET_MQ);
        onViewport = () => {
          const viewport = readViewport();
          isMobile.value = viewport.isMobile;
          isTablet.value = viewport.isTablet;
        };
        onViewport();
        if (phoneQuery.addEventListener) {
          phoneQuery.addEventListener("change", onViewport);
          tabletQuery.addEventListener("change", onViewport);
        } else {
          phoneQuery.addListener(onViewport);
          tabletQuery.addListener(onViewport);
        }
      }
      loadTransactions();
    });

    onUnmounted(() => {
      if (searchTimer) clearTimeout(searchTimer);
      if (onViewport) {
        if (phoneQuery?.removeEventListener) {
          phoneQuery.removeEventListener("change", onViewport);
          tabletQuery.removeEventListener("change", onViewport);
        } else {
          phoneQuery?.removeListener?.(onViewport);
          tabletQuery?.removeListener?.(onViewport);
        }
      }
    });

    watch([currentPage, perPage, sortField, sortOrder], (next, prev) => {
      if (prev && next[1] !== prev[1] && next[0] !== 1) {
        currentPage.value = 1;
        return;
      }
      loadTransactions();
    });

    watch(filter, () => {
      if (searchTimer) clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        if (currentPage.value !== 1) {
          currentPage.value = 1;
        } else {
          loadTransactions();
        }
      }, 300);
    });

    return {
      transactions,
      stats,
      isLoading,
      loadError,
      perPage,
      filter,
      totalRows,
      sortField,
      sortOrder,
      tableFirst,
      tableMinWidth,
      pageOptions,
      hasSearch,
      emptyTitle,
      emptyDescription,
      clearSearch,
      isMobile,
      isTablet,
      hasRowActions,
      canView,
      getRowActions,
      refreshTable,
      onTablePage,
      onTableSort,
      goToCreateForm,
      transactionViewTo,
      transactionLabel,
      formatDate,
      currency,
      toolsMenu,
      toolsMenuOpen,
      toolsMenuModel,
      toggleToolsMenu,
    };
  },
};
</script>

<style scoped>
.jr-tx-list__search {
  position: relative;
  min-width: 0;
  width: 100%;
}

.jr-tx-list__search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  z-index: 1;
  display: flex;
  color: var(--color-jr-muted);
  pointer-events: none;
  transform: translateY(-50%);
}

.jr-tx-list__search-icon :deep(svg) {
  width: 1rem;
  height: 1rem;
}

.jr-tx-list__search :deep(.p-inputtext) {
  padding-left: 2.25rem;
}

@media (max-width: 767.98px) {
  :deep(.jr-page-header) {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
  }

  :deep(.jr-page-header__actions) {
    flex-shrink: 0;
  }

  :deep(.jr-toolbar) {
    flex-direction: row;
    flex-wrap: nowrap;
    align-items: center;
    gap: 0.5rem;
    padding: 0.35rem 0 0.5rem;
    margin-bottom: 0.5rem;
  }

  :deep(.jr-toolbar__start) {
    flex: 1 1 auto;
    min-width: 0;
  }

  :deep(.jr-toolbar__actions) {
    flex: 0 0 auto;
  }
}

.jr-tx-list__summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
  pointer-events: none;
}

:deep(.jr-toolbar__actions .jr-tx-list__entries.p-select),
:deep(.jr-toolbar__actions .jr-tx-list__entries.jr-control) {
  width: 6.25rem;
  min-width: 6.25rem;
  flex: 0 0 auto;
}

.jr-tx-list__loading {
  margin: 0.75rem 0;
  color: var(--color-jr-muted);
  font-size: 0.875rem;
}

.jr-tx-list__rows {
  list-style: none;
  margin: 0;
  padding: 0;
}

.jr-tx-list__rows[aria-busy="true"] {
  opacity: 0.55;
}

.jr-tx-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--color-jr-border);
}

.jr-tx-row__main {
  min-width: 0;
  flex: 1 1 auto;
}

.jr-tx-row__name {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-jr-text);
}

a.jr-tx-row__name--link {
  color: var(--color-jr-primary);
  text-decoration: none;
}

a.jr-tx-row__name--link:hover {
  color: var(--color-jr-primary-hover);
  text-decoration: underline;
}

.jr-tx-row__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0.2rem 0 0;
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}

.jr-tx-row__amount {
  font-variant-numeric: tabular-nums;
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-tx-row__aside {
  flex-shrink: 0;
}

.jr-tx-list__pager {
  margin-top: 0.25rem;
  border-top: 1px solid var(--color-jr-border);
}

.jr-tx-list__pager :deep(.p-paginator),
.jr-tx-list__pager :deep(.p-paginator-content) {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 0.5rem;
  padding: 0.35rem 0;
}

.jr-tx-list__table :deep(.p-datatable) {
  --p-datatable-row-striped-background: var(--color-jr-surface-muted);
  --p-datatable-body-cell-padding: 0.3rem 0.5rem;
  --p-datatable-header-cell-padding: 0.3rem 0.5rem;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface);
}

.jr-tx-list__table :deep(.p-datatable-tbody > tr > td),
.jr-tx-list__table :deep(.p-datatable-thead > tr > th) {
  font-size: 0.875rem;
  padding: 0.3rem 0.5rem;
  vertical-align: middle;
}

.jr-tx-list__table :deep(th.jr-col-num),
.jr-tx-list__table :deep(td.jr-col-num) {
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.jr-tx-list__table :deep(th.jr-col-actions),
.jr-tx-list__table :deep(td.jr-col-actions) {
  width: 18rem;
  text-align: center;
  white-space: nowrap;
}

.jr-tx-list__table :deep(th.jr-col-actions--compact),
.jr-tx-list__table :deep(td.jr-col-actions--compact) {
  width: 3.5rem;
}

.jr-tx-list__table[aria-busy="true"] {
  opacity: 0.7;
}
</style>
