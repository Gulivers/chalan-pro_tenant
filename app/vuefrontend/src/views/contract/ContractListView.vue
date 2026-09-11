<template>
  <JRPage>
    <JRPageHeader title="Contracts">
      <template #actions>
        <JRButton
          v-if="hasPermission('ctrctsapp.add_contract')"
          type="button"
          @click="goToCreateForm">
          + New Contract
        </JRButton>
      </template>
    </JRPageHeader>

    <JRToolbar>
      <template #start>
        <div class="jr-contract-list__search">
          <label class="jr-sr-only" for="contract-filter-input">
            Search contracts
          </label>
          <span class="jr-contract-list__search-icon" aria-hidden="true">
            <SearchIcon />
          </span>
          <JRInput
            inputId="contract-filter-input"
            v-model="filter"
            type="search"
            placeholder="Search contracts..."
            autocomplete="off"
            :spellcheck="false"
            autocapitalize="none"
            autocorrect="off"
            enterkeyhint="search" />
        </div>
      </template>

      <template v-if="!isMobile" #stats>
        <div class="jr-contract-list__summary" aria-live="polite">
          <JRBadge :value="`${stats.total} Total`" severity="secondary" />
          <JRBadge
            :value="`${stats.active} Active`"
            :severity="stats.active > 0 ? 'success' : 'secondary'" />
          <JRBadge
            :value="`${stats.inactive} Inactive`"
            severity="secondary" />
        </div>
      </template>

      <template #actions>
        <template v-if="!isMobile">
          <JRSelect
            class="jr-contract-list__entries"
            inputId="contract-per-page"
            ariaLabel="Entries per page"
            v-model="perPage"
            :options="pageOptions"
            optionLabel="label"
            optionValue="value" />
          <JRButton
            type="button"
            variant="ghost"
            size="sm"
            class="jr-contract-list__refresh"
            @click="refreshTable">
            <RefreshIcon />
            Refresh
          </JRButton>
        </template>
        <template v-else>
          <button
            id="contract-list-tools-trigger"
            type="button"
            class="jr-icon-btn"
            aria-label="List tools"
            aria-haspopup="menu"
            :aria-expanded="toolsMenuOpen ? 'true' : 'false'"
            aria-controls="contract-list-tools-menu"
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
            id="contract-list-tools-menu"
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

    <div v-if="isMobile" class="jr-contract-list__mobile">
      <JREmptyState
        v-if="!contracts.length && !isLoading"
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
      <p v-if="isLoading && !contracts.length" class="jr-contract-list__loading">
        Loading contracts…
      </p>
      <p
        v-else-if="isLoading && contracts.length"
        class="jr-contract-list__loading"
        aria-live="polite">
        Updating…
      </p>
      <ul
        v-if="contracts.length"
        class="jr-contract-list__rows"
        :aria-busy="isLoading ? 'true' : 'false'">
        <li v-for="item in contracts" :key="item.id" class="jr-contract-row">
          <div class="jr-contract-row__main">
            <router-link
              v-if="canView"
              class="jr-contract-row__name jr-contract-row__name--link"
              :to="contractViewTo(item.id)"
              :aria-label="`View contract ${item.id}`">
              #{{ item.id }} · {{ item.builder?.name || "—" }}
            </router-link>
            <span v-else class="jr-contract-row__name">
              #{{ item.id }} · {{ item.builder?.name || "—" }}
            </span>
            <p class="jr-contract-row__meta">
              <span>{{ item.job?.name || "—" }}</span>
              <span aria-hidden="true"> · </span>
              <span>{{ item.house_model?.name || "—" }}</span>
              <span aria-hidden="true"> · </span>
              <span>{{ formatDate(item.date_created) }}</span>
            </p>
            <p class="jr-contract-row__meta">
              <JRBadge
                :value="item.needs_reprint ? 'Yes' : 'No'"
                :severity="item.needs_reprint ? 'danger' : 'success'" />
              <span v-if="item.lot">Lot {{ item.lot }}</span>
              <span v-else-if="item.address">{{ item.address }}</span>
            </p>
          </div>
          <div class="jr-contract-row__aside">
            <JRRowActions
              v-if="hasRowActions"
              :actions="getRowActions(item)"
              :compact="true"
              :entity-label="`Contract ${item.id}`" />
          </div>
        </li>
      </ul>
      <Paginator
        v-if="totalRows > 0"
        class="jr-contract-list__pager"
        :rows="perPage"
        :totalRecords="totalRows"
        :first="tableFirst"
        template="PrevPageLink CurrentPageReport NextPageLink"
        currentPageReportTemplate="{first}–{last} of {totalRecords}"
        @page="onTablePage" />
    </div>

    <div
      v-else
      class="jr-contract-list__table"
      :aria-busy="isLoading ? 'true' : 'false'">
      <JRDataTable
        :value="contracts"
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
        <Column field="id" header="ID" sortable>
          <template #body="{ data }">
            <router-link
              v-if="canView"
              class="jr-contract-row__name jr-contract-row__name--link"
              :to="contractViewTo(data.id)"
              :aria-label="`View contract ${data.id}`">
              {{ data.id }}
            </router-link>
            <strong v-else>{{ data.id }}</strong>
          </template>
        </Column>
        <Column v-if="!isTablet" field="doc_type" header="Doc" sortable>
          <template #body="{ data }">
            {{ data.doc_type || "—" }}
          </template>
        </Column>
        <Column field="type" header="Type" sortable>
          <template #body="{ data }">
            {{ data.type || "—" }}
          </template>
        </Column>
        <Column field="date_created" header="Date" sortable>
          <template #body="{ data }">
            {{ formatDate(data.date_created) }}
          </template>
        </Column>
        <Column field="builder" header="Builder">
          <template #body="{ data }">
            {{ data.builder?.name || "—" }}
          </template>
        </Column>
        <Column field="job" header="Job">
          <template #body="{ data }">
            {{ data.job?.name || "—" }}
          </template>
        </Column>
        <Column v-if="!isTablet" field="house_model" header="Model">
          <template #body="{ data }">
            {{ data.house_model?.name || "—" }}
          </template>
        </Column>
        <Column field="lot" header="Lot" sortable>
          <template #body="{ data }">
            {{ data.lot || "—" }}
          </template>
        </Column>
        <Column
          v-if="!isTablet"
          field="address"
          header="Address"
          sortable
          headerClass="jr-col-address"
          bodyClass="jr-col-address">
          <template #body="{ data }">
            {{ data.address || "—" }}
          </template>
        </Column>
        <Column
          v-if="!isTablet"
          field="sqft"
          header="SqFt"
          sortable
          headerClass="jr-col-num"
          bodyClass="jr-col-num">
          <template #body="{ data }">
            {{ data.sqft ?? "—" }}
          </template>
        </Column>
        <Column
          v-if="!isTablet"
          field="total"
          header="Total"
          sortable
          headerClass="jr-col-num"
          bodyClass="jr-col-num">
          <template #body="{ data }">
            {{ formatMoney(data.total) }}
          </template>
        </Column>
        <Column field="needs_reprint" header="Need Print" sortable>
          <template #body="{ data }">
            <JRBadge
              :value="data.needs_reprint ? 'Yes' : 'No'"
              :severity="data.needs_reprint ? 'danger' : 'success'" />
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
              :entity-label="`Contract ${data.id}`" />
          </template>
        </Column>
      </JRDataTable>
    </div>
  </JRPage>
</template>

<script>
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

const ENDPOINT = "/api/contract/contracts-provider/";
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
  name: "ContractListView",
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

    const contracts = ref([]);
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
      isTablet.value ? "min-width: 40rem" : "min-width: 64rem"
    );
    const hasSearch = computed(() =>
      Boolean(filter.value && filter.value.trim())
    );
    const emptyTitle = computed(() => {
      if (loadError.value) return "Could not load contracts";
      if (hasSearch.value) return "No matching contracts";
      return "No contracts";
    });
    const emptyDescription = computed(() => {
      if (loadError.value) return "Try Refresh.";
      const query = filter.value.trim();
      if (query) return `No contracts match “${query}”.`;
      return "No contracts yet.";
    });

    const canView = computed(() =>
      !!proxy?.hasPermission?.("ctrctsapp.view_contract")
    );
    const hasRowActions = computed(
      () =>
        canView.value ||
        !!proxy?.hasPermission?.("ctrctsapp.change_contract") ||
        !!proxy?.hasPermission?.("ctrctsapp.delete_contract")
    );

    const clearSearch = () => {
      filter.value = "";
      if (typeof document !== "undefined") {
        document.getElementById("contract-filter-input")?.focus();
      }
    };

    const formatDate = (iso) => {
      if (!iso) return "—";
      const d = new Date(iso);
      return d.toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "2-digit",
      });
    };

    const formatMoney = (value) => {
      if (value === null || value === undefined || value === "") return "—";
      const n = Number(value);
      if (!Number.isFinite(n)) return "—";
      return n.toLocaleString("en-US", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
    };

    const getOrderingFromSortBy = ({ sortField: field, sortOrder: order }) => {
      if (!field) return "-id";
      const fieldMap = {
        id: "id",
        doc_type: "doc_type",
        type: "type",
        date_created: "date_created",
        lot: "lot",
        address: "address",
        sqft: "sqft",
        total: "total",
        needs_reprint: "needs_reprint",
      };
      const djangoField = fieldMap[field];
      if (!djangoField) return "-id";
      return order === -1 ? `-${djangoField}` : djangoField;
    };

    const loadContracts = async () => {
      if (!isLoading.value) isLoading.value = true;
      try {
        const params = new URLSearchParams({
          page: currentPage.value,
          per_page: perPage.value,
          search: filter.value || "",
          ordering: getOrderingFromSortBy({
            sortField: sortField.value,
            sortOrder: sortOrder.value,
          }),
        });
        const { data } = await axios.get(`${ENDPOINT}?${params}`);
        contracts.value = data.items || [];
        totalRows.value = data.totalRows || 0;
        if (data.stats) stats.value = data.stats;
        loadError.value = false;
      } catch (e) {
        console.error("contracts provider error:", e);
        loadError.value = true;
        contracts.value = [];
        totalRows.value = 0;
        proxy?.notifyError?.("Error loading contracts.");
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
      loadContracts();
    };

    const goToCreateForm = () => router.push({ name: "contract-form" });
    const contractViewTo = (id) => ({
      name: "contract-view",
      params: { id },
    });
    const viewItem = (id) => router.push(contractViewTo(id));
    const editItem = (id) => {
      const url = router.resolve({ name: "contract-edit", params: { id } });
      window.open(url.href, "_blank");
    };

    const printItem = async (id) => {
      try {
        const response = await axios.get(`/api/contract-pdf/${id}/`, {
          headers: {
            Authorization: `Token ${localStorage.getItem("authToken")}`,
          },
          responseType: "json",
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
        const pdfUrl = window.URL.createObjectURL(blob);

        const win = window.open(pdfUrl, "_blank");
        if (!win) {
          const link = document.createElement("a");
          link.href = pdfUrl;
          link.download = response.data.filename || `contract_${id}.pdf`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        }

        setTimeout(() => window.URL.revokeObjectURL(pdfUrl), 10000);
      } catch (error) {
        console.error("Error generating contract PDF:", error);
        proxy?.notifyError?.("Could not generate contract PDF.");
      }
    };

    const deleteItem = (id) => {
      proxy?.confirmDelete?.(
        "Are you sure?",
        `Delete contract #${id}? This action cannot be undone.`,
        async () => {
          try {
            await axios.delete(`/api/contract/${id}/`);
            proxy?.notifyToastSuccess?.("The contract has been deleted.");
            refreshTable();
          } catch (error) {
            console.error("Error deleting contract:", error);
            const status = error?.response?.status;
            const data = error?.response?.data;
            if (status === 403) {
              proxy?.notifyError?.(
                "You do not have permission for this action."
              );
            } else if (status === 409) {
              const detail =
                data?.detail ||
                "Cannot delete this contract because it is being used elsewhere.";
              proxy?.notifyError?.(detail);
            } else {
              const detail = data?.detail || "Error deleting the contract.";
              proxy?.notifyError?.(detail);
            }
          }
        }
      );
    };

    const getRowActions = (item) => {
      const actions = [];
      if (proxy?.hasPermission?.("ctrctsapp.view_contract")) {
        actions.push({
          key: "view",
          label: "View",
          severity: "success",
          icon: EyeIcon,
          command: () => viewItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("ctrctsapp.change_contract")) {
        actions.push({
          key: "edit",
          label: "Edit",
          severity: "primary",
          icon: PencilIcon,
          command: () => editItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("ctrctsapp.view_contract")) {
        actions.push({
          key: "print",
          label: "Print",
          severity: "secondary",
          buttonClass: "jr-row-actions__btn--print",
          icon: UploadIcon,
          command: () => printItem(item.id),
        });
      }
      if (proxy?.hasPermission?.("ctrctsapp.delete_contract")) {
        actions.push({
          key: "delete",
          label: "Delete",
          severity: "danger",
          icon: TrashIcon,
          command: () => deleteItem(item.id),
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
      loadContracts();
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
      // Reset to page 1 when page size changes without double-fetching.
      if (prev && next[1] !== prev[1] && next[0] !== 1) {
        currentPage.value = 1;
        return;
      }
      loadContracts();
    });

    watch(filter, () => {
      if (searchTimer) clearTimeout(searchTimer);
      searchTimer = setTimeout(() => {
        if (currentPage.value !== 1) {
          currentPage.value = 1;
        } else {
          loadContracts();
        }
      }, 300);
    });

    return {
      contracts,
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
      contractViewTo,
      formatDate,
      formatMoney,
      toolsMenu,
      toolsMenuOpen,
      toolsMenuModel,
      toggleToolsMenu,
    };
  },
};
</script>

<style scoped>
.jr-contract-list__search {
  position: relative;
  min-width: 0;
  width: 100%;
}

.jr-contract-list__search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  z-index: 1;
  display: flex;
  color: var(--color-jr-muted);
  pointer-events: none;
  transform: translateY(-50%);
}

.jr-contract-list__search-icon :deep(svg) {
  width: 1rem;
  height: 1rem;
}

.jr-contract-list__search :deep(.p-inputtext) {
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

.jr-contract-list__summary {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
  pointer-events: none;
}

:deep(.jr-toolbar__actions .jr-contract-list__entries.p-select),
:deep(.jr-toolbar__actions .jr-contract-list__entries.jr-control) {
  width: 4.75rem;
  flex: 0 0 auto;
}

.jr-contract-list__loading {
  margin: 0.75rem 0;
  color: var(--color-jr-muted);
  font-size: 0.875rem;
}

.jr-contract-list__rows {
  list-style: none;
  margin: 0;
  padding: 0;
}

.jr-contract-list__rows[aria-busy="true"] {
  opacity: 0.55;
}

.jr-contract-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.75rem 0;
  border-bottom: 1px solid var(--color-jr-border);
}

.jr-contract-row__main {
  min-width: 0;
  flex: 1 1 auto;
}

.jr-contract-row__name {
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-jr-text);
}

a.jr-contract-row__name--link {
  color: var(--color-jr-primary);
  text-decoration: none;
}

a.jr-contract-row__name--link:hover {
  color: var(--color-jr-primary-hover);
  text-decoration: underline;
}

.jr-contract-row__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0.2rem 0 0;
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}

.jr-contract-row__aside {
  flex-shrink: 0;
}

.jr-contract-list__pager {
  margin-top: 0.25rem;
  border-top: 1px solid var(--color-jr-border);
}

.jr-contract-list__pager :deep(.p-paginator),
.jr-contract-list__pager :deep(.p-paginator-content) {
  display: flex;
  flex-wrap: nowrap;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 0.5rem;
  padding: 0.35rem 0;
}

.jr-contract-list__table :deep(.p-datatable) {
  --p-datatable-row-striped-background: var(--color-jr-surface-muted);
  --p-datatable-body-cell-padding: 0.3rem 0.5rem;
  --p-datatable-header-cell-padding: 0.3rem 0.5rem;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface);
}

.jr-contract-list__table :deep(.p-datatable-tbody > tr > td),
.jr-contract-list__table :deep(.p-datatable-thead > tr > th) {
  font-size: 0.875rem;
  padding: 0.3rem 0.5rem;
  vertical-align: middle;
}

.jr-contract-list__table :deep(th.jr-col-address),
.jr-contract-list__table :deep(td.jr-col-address) {
  min-width: 14rem;
  width: 18%;
  white-space: normal;
  overflow-wrap: anywhere;
}

.jr-contract-list__table :deep(th.jr-col-num),
.jr-contract-list__table :deep(td.jr-col-num) {
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.jr-contract-list__table :deep(th.jr-col-actions),
.jr-contract-list__table :deep(td.jr-col-actions) {
  width: 18rem;
  text-align: center;
  white-space: nowrap;
}

.jr-contract-list__table :deep(th.jr-col-actions.jr-col-actions--compact),
.jr-contract-list__table :deep(td.jr-col-actions.jr-col-actions--compact) {
  width: 3.25rem;
}

.jr-contract-list__table
  :deep(th.jr-col-actions .p-datatable-column-header-content),
.jr-contract-list__table :deep(td.jr-col-actions .jr-row-actions) {
  justify-content: center;
  width: 100%;
}

.jr-contract-list__table :deep(.jr-row-actions__btn--print.p-button-text),
.jr-contract-list__table
  :deep(.jr-row-actions__btn--print.p-button-text .p-button-label),
.jr-contract-list__table
  :deep(.jr-row-actions__btn--print.p-button-text .p-button-icon),
.jr-contract-list__table :deep(.jr-row-actions__btn--print.p-button-text svg) {
  --p-button-text-secondary-color: var(--color-jr-text);
  --p-button-text-secondary-hover-color: var(--color-jr-text);
  color: var(--color-jr-text);
}

.jr-contract-list__table
  :deep(.jr-row-actions__btn--print.p-button-text:hover:not(:disabled)) {
  background: var(--color-jr-surface-muted);
}
</style>
