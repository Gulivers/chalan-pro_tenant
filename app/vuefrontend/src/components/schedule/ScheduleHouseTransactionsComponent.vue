<template>
  <div class="jr-pilot jr-house-transactions">
    <div class="jr-house-transactions__header">
      <h3 class="jr-house-transactions__title">Transactions</h3>
      <JRButton
        v-if="canAdd"
        type="button"
        size="sm"
        @click="() => goToTransactionForm()">
        + New Transaction
      </JRButton>
    </div>

    <JRToolbar>
      <template #start>
        <div class="jr-house-transactions__search">
          <label class="jr-sr-only" for="house-transactions-search">
            Search transactions
          </label>
          <span class="jr-house-transactions__search-icon" aria-hidden="true">
            <SearchIcon />
          </span>
          <JRInput
            inputId="house-transactions-search"
            v-model="search"
            type="search"
            placeholder="Search by type, notes, ID…"
            autocomplete="off"
            :spellcheck="false"
            enterkeyhint="search" />
        </div>
      </template>

      <template #stats>
        <div class="jr-house-transactions__summary" aria-live="polite">
          <JRBadge
            :value="`${filteredTransactions.length} Total`"
            severity="secondary" />
          <JRBadge
            :value="`${activeCount} Active`"
            :severity="activeCount > 0 ? 'success' : 'secondary'" />
          <JRBadge
            :value="`${voidedCount} Voided`"
            severity="secondary" />
        </div>
      </template>

      <template #actions>
        <JRButton
          type="button"
          variant="ghost"
          size="sm"
          class="jr-house-transactions__refresh"
          @click="refreshTable">
          <RefreshIcon />
          Refresh
        </JRButton>
      </template>
    </JRToolbar>

    <JRScrollArea
      class="jr-house-transactions__scroll"
      height="var(--jr-wov-body-height, 22rem)">
      <div
        class="jr-house-transactions__table"
        :aria-busy="loading ? 'true' : 'false'">
        <JRDataTable
          :value="filteredTransactions"
          :loading="loading"
          dataKey="id"
          :paginator="filteredTransactions.length > perPage"
          :rows="perPage"
          :first="tableFirst"
          sortField="id"
          :sortOrder="-1"
          paginatorTemplate="PrevPageLink CurrentPageReport NextPageLink"
          currentPageReportTemplate="{first}–{last} of {totalRecords}"
          scrollable
          stripedRows
          tableStyle="min-width: 40rem"
          :emptyTitle="loading ? '' : emptyTitle"
          :emptyDescription="loading ? '' : emptyDescription"
          @page="onTablePage">
          <template #empty>
            <JREmptyState
              v-if="!loading"
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
                v-else-if="search.trim()"
                type="button"
                variant="ghost"
                size="sm"
                @click="search = ''">
                Clear search
              </JRButton>
              <JRButton
                v-else-if="canAdd"
                type="button"
                size="sm"
                @click="() => goToTransactionForm()">
                + New Transaction
              </JRButton>
            </JREmptyState>
          </template>

          <Column field="id" header="ID" sortable style="width: 4rem">
            <template #body="{ data }">
              {{ data.id }}
            </template>
          </Column>

          <Column
            field="document_type"
            header="Type"
          sortable
          style="width: 7rem">
          <template #body="{ data }">
            <span
              v-tt
              :data-title="
                documentTypeDescriptionsMap[data.document_type] || ''
              ">
              <JRBadge
                :value="documentTypeNamesMap[data.document_type] || '—'"
                severity="info" />
            </span>
          </template>
        </Column>

        <Column field="date" header="Date" sortable style="width: 8rem">
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
            <strong>{{ currency(data.total_amount) }}</strong>
          </template>
        </Column>

        <Column field="notes" header="Notes">
          <template #body="{ data }">
            <span
              class="jr-house-transactions__notes"
              :title="data.notes || undefined">
              {{ data.notes || "—" }}
            </span>
          </template>
        </Column>

        <Column
          field="is_active"
          header="Status"
          sortable
          style="width: 6rem">
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
          headerClass="jr-col-actions"
          bodyClass="jr-col-actions">
          <template #body="{ data }">
            <JRRowActions
              :actions="getRowActions(data)"
              :entity-label="`Transaction ${data.id}`" />
          </template>
        </Column>
      </JRDataTable>
      </div>
    </JRScrollArea>
  </div>
</template>

<script>
import { getAccessToken } from '@/auth/tokenHelpers';
import axios from "axios";
import Swal from "sweetalert2";
import dayjs from "dayjs";
import Column from "primevue/column";
import EyeIcon from "@primevue/icons/eye";
import PencilIcon from "@primevue/icons/pencil";
import RefreshIcon from "@primevue/icons/refresh";
import SearchIcon from "@primevue/icons/search";
import {
  JRBadge,
  JRButton,
  JRDataTable,
  JREmptyState,
  JRInput,
  JRRowActions,
  JRScrollArea,
  JRToolbar,
} from "@ui";

export default {
  name: "ScheduleHouseTransactionsComponent",
  components: {
    Column,
    EyeIcon,
    PencilIcon,
    RefreshIcon,
    SearchIcon,
    JRBadge,
    JRButton,
    JRDataTable,
    JREmptyState,
    JRInput,
    JRRowActions,
    JRScrollArea,
    JRToolbar,
  },
  props: {
    eventId: {
      type: Number,
      default: null,
    },
    workAccountId: {
      type: Number,
      default: null,
    },
  },
  data() {
    return {
      transactions: [],
      documentTypesMap: {},
      documentTypeNamesMap: {},
      documentTypeDescriptionsMap: {},
      loading: false,
      loadError: false,
      search: "",
      perPage: 10,
      tableFirst: 0,
      resolvedWorkAccountId: null,
    };
  },
  computed: {
    canAdd() {
      return this.hasPermission("apptransactions.add_document");
    },
    canView() {
      return this.hasPermission("apptransactions.view_document");
    },
    canChange() {
      return this.hasPermission("apptransactions.change_document");
    },
    hasRowActions() {
      return this.canView || this.canChange;
    },
    filteredTransactions() {
      if (!this.search) return this.transactions;
      const q = this.search.toLowerCase();
      return this.transactions.filter((item) => {
        const typeCode = this.documentTypesMap[item.document_type] || "";
        const typeName = this.documentTypeNamesMap[item.document_type] || "";
        const notes = item.notes || "";
        return (
          typeCode.toLowerCase().includes(q) ||
          typeName.toLowerCase().includes(q) ||
          notes.toLowerCase().includes(q) ||
          item.id.toString().includes(q)
        );
      });
    },
    activeCount() {
      return this.filteredTransactions.filter((t) => t.is_active).length;
    },
    voidedCount() {
      return this.filteredTransactions.filter((t) => !t.is_active).length;
    },
    emptyTitle() {
      if (this.loadError) return "Could not load transactions";
      if (this.search.trim()) return "No matching transactions";
      return "No transactions yet";
    },
    emptyDescription() {
      if (this.loadError) return "Check your connection and try Refresh.";
      if (this.search.trim()) return "Try a different search term.";
      return "No transactions found for this work account.";
    },
  },
  watch: {
    eventId: {
      immediate: true,
      handler() {
        this.initializeData();
      },
    },
    workAccountId: {
      immediate: true,
      handler() {
        this.initializeData();
      },
    },
    search() {
      this.tableFirst = 0;
    },
  },
  methods: {
    hasPermission(permission) {
      try {
        const userPermissions = JSON.parse(
          localStorage.getItem("userPermissions")
        );
        return (
          !!userPermissions &&
          Array.isArray(userPermissions.permissions) &&
          userPermissions.permissions.includes(permission)
        );
      } catch {
        return false;
      }
    },
    getRowActions(item) {
      const actions = [];
      if (this.canView) {
        actions.push({
          key: "view",
          label: "View",
          severity: "success",
          icon: EyeIcon,
          command: () => this.goToTransactionForm(item.id, "view"),
        });
        actions.push({
          key: "print",
          label: "Print",
          severity: "secondary",
          command: () => this.printTransaction(item.id),
        });
      }
      if (this.canChange) {
        actions.push({
          key: "edit",
          label: "Edit",
          severity: "primary",
          icon: PencilIcon,
          command: () => this.goToTransactionForm(item.id),
        });
      }
      return actions;
    },
    onTablePage(event) {
      this.tableFirst = event.first ?? 0;
      if (event.rows) this.perPage = event.rows;
    },
    refreshTable() {
      this.initializeData();
    },
    async initializeData() {
      this.tableFirst = 0;
      if (this.workAccountId) {
        this.resolvedWorkAccountId = this.workAccountId;
        await Promise.all([
          this.fetchTransactions(),
          this.fetchDocumentTypes(),
        ]);
        return;
      }

      if (!this.eventId) {
        this.resolvedWorkAccountId = null;
        this.transactions = [];
        this.loading = false;
        this.loadError = false;
        return;
      }

      await this.loadWorkAccountId();
      if (this.resolvedWorkAccountId) {
        await Promise.all([
          this.fetchTransactions(),
          this.fetchDocumentTypes(),
        ]);
      } else {
        this.transactions = [];
        this.loading = false;
        this.loadError = false;
      }
    },
    async loadWorkAccountId() {
      try {
        const { data } = await axios.get(`/api/event/${this.eventId}/`);
        if (data && data.work_account) {
          if (typeof data.work_account === "number") {
            this.resolvedWorkAccountId = data.work_account;
          } else if (
            typeof data.work_account === "object" &&
            data.work_account !== null &&
            data.work_account.id
          ) {
            this.resolvedWorkAccountId = data.work_account.id;
          } else {
            this.resolvedWorkAccountId = data.work_account;
          }
        } else {
          this.resolvedWorkAccountId = null;
        }
      } catch (e) {
        console.error("Error fetching event data:", e);
        this.resolvedWorkAccountId = null;
      }
    },
    async fetchTransactions() {
      if (!this.resolvedWorkAccountId) {
        this.transactions = [];
        this.loading = false;
        this.loadError = false;
        return;
      }

      this.loading = true;
      this.loadError = false;
      try {
        const url = `/api/documents/?work_account=${this.resolvedWorkAccountId}&ordering=-id`;
        const response = await axios.get(url);
        const normalizeList = (data) =>
          Array.isArray(data) ? data : data?.results ?? [];
        this.transactions = normalizeList(response.data);
      } catch (error) {
        console.error("Error fetching transactions:", error);
        this.notifyError?.("Error loading transactions.");
        this.transactions = [];
        this.loadError = true;
      } finally {
        this.loading = false;
      }
    },
    async fetchDocumentTypes() {
      try {
        const response = await axios.get(
          "/api/document-types/?ordering=type_code"
        );
        const normalizeList = (data) =>
          Array.isArray(data) ? data : data?.results ?? [];
        const arr = normalizeList(response.data);
        this.documentTypesMap = Object.fromEntries(
          arr.map((dt) => [dt.id, dt.type_code])
        );
        this.documentTypeNamesMap = Object.fromEntries(
          arr.map((dt) => [dt.id, dt.name || dt.type_code])
        );
        this.documentTypeDescriptionsMap = Object.fromEntries(
          arr.map((dt) => [dt.id, dt.description || ""])
        );
      } catch (error) {
        console.error("Error fetching document types:", error);
      }
    },
    formatDate(dateString) {
      if (!dateString) return "—";
      return dayjs(dateString).format("MMM DD, YYYY");
    },
    currency(amount) {
      const num = Number(amount || 0);
      return num.toLocaleString("en-US", {
        style: "currency",
        currency: "USD",
      });
    },
    async goToTransactionForm(transactionId = null, mode = null) {
      if (transactionId !== null && transactionId !== undefined) {
        if (typeof transactionId === "object" || isNaN(Number(transactionId))) {
          transactionId = null;
          mode = null;
        } else {
          transactionId = Number(transactionId);
        }
      }

      if (!this.resolvedWorkAccountId && this.eventId) {
        await this.loadWorkAccountId();
      }

      try {
        const modalEl = document.querySelector(".modal.show");
        if (modalEl) {
          const inst = window.bootstrap?.Modal?.getInstance?.(modalEl);
          inst?.hide?.();
        }
        document
          .querySelectorAll(".modal-backdrop")
          .forEach((el) => el.remove());
        document.body.classList.remove("modal-open");
        document.body.style.removeProperty("padding-right");
      } catch (e) {
        // no-op
      }

      const queryParams = new URLSearchParams();

      if (this.eventId) {
        queryParams.append("event_id", String(this.eventId));
      }

      if (
        transactionId !== null &&
        transactionId !== undefined &&
        !isNaN(transactionId)
      ) {
        queryParams.append("id", String(transactionId));
        if (mode) {
          queryParams.append("mode", String(mode));
        }
      }

      if (
        this.resolvedWorkAccountId !== null &&
        this.resolvedWorkAccountId !== undefined
      ) {
        const workAccountIdStr = String(this.resolvedWorkAccountId);
        if (
          workAccountIdStr &&
          workAccountIdStr !== "null" &&
          workAccountIdStr !== "undefined"
        ) {
          queryParams.append("work_account_id", workAccountIdStr);
        }
      }

      const queryString = queryParams.toString();
      const url = `/transactions/form${queryString ? `?${queryString}` : ""}`;

      this.$nextTick(() => {
        window.location.href = url;
      });
    },
    async printTransaction(documentId) {
      try {
        const response = await axios.get(`/api/documents/${documentId}/pdf/`, {
          headers: {
            Authorization: `Bearer ${getAccessToken()}`,
          },
          responseType: "json",
        });

        if (!response.data || !response.data.file) {
          throw new Error("No PDF file received");
        }

        const byteCharacters = atob(response.data.file);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
          byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: "application/pdf" });
        const url = window.URL.createObjectURL(blob);

        const isMobile =
          /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
            navigator.userAgent
          ) || window.innerWidth <= 768;

        if (isMobile) {
          const link = document.createElement("a");
          link.href = url;
          link.download =
            response.data.filename || `transaction_${documentId}.pdf`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          this.notifyToastSuccess?.("PDF downloaded successfully.");
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
            this.notifyToastSuccess?.("PDF downloaded successfully.");
          } else {
            this.notifyToastSuccess?.("PDF opened in new window.");
          }
        }

        setTimeout(() => {
          window.URL.revokeObjectURL(url);
        }, 1000);
      } catch (error) {
        console.error("Error downloading PDF:", error);
        await Swal.fire({
          icon: "error",
          title: "Error",
          text: "Could not generate the PDF document. Please try again.",
          confirmButtonText: "OK",
        });
      }
    },
  },
};
</script>

<style scoped>
.jr-house-transactions {
  display: flex;
  flex-direction: column;
  gap: 0;
  min-height: 0;
  height: 100%;
}

.jr-house-transactions__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  flex: 0 0 auto;
}

.jr-house-transactions__scroll {
  flex: 1 1 auto;
  min-height: 0;
}

.jr-house-transactions__title {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text, #111827);
  text-align: left;
}

.jr-house-transactions__search {
  position: relative;
  min-width: 0;
  width: 100%;
  max-width: 22rem;
}

.jr-house-transactions__search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  z-index: 1;
  display: flex;
  color: var(--color-jr-muted, #4b5563);
  pointer-events: none;
  transform: translateY(-50%);
}

.jr-house-transactions__search-icon :deep(svg) {
  width: 1rem;
  height: 1rem;
}

.jr-house-transactions__search :deep(.p-inputtext) {
  padding-left: 2.25rem;
}

.jr-house-transactions__summary {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  pointer-events: none;
}

.jr-house-transactions__notes {
  display: inline-block;
  max-width: 12rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--color-jr-muted, #4b5563);
  font-size: 0.75rem;
}

.jr-house-transactions__table :deep(th.jr-col-num),
.jr-house-transactions__table :deep(td.jr-col-num) {
  text-align: right;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

.jr-house-transactions__table :deep(th.jr-col-num .p-datatable-column-header-content) {
  justify-content: flex-end;
}

.jr-house-transactions__table :deep(.jr-empty-state) {
  padding: 2.5rem 1rem;
}

.jr-house-transactions__table :deep(th.jr-col-actions),
.jr-house-transactions__table :deep(td.jr-col-actions) {
  width: 14rem;
  text-align: center;
  white-space: nowrap;
}

.jr-house-transactions__table
  :deep(th.jr-col-actions .p-datatable-column-header-content) {
  display: flex;
  justify-content: center;
  width: 100%;
}

.jr-house-transactions__table :deep(td.jr-col-actions .jr-row-actions) {
  justify-content: center;
  width: 100%;
}

@media (max-width: 767.98px) {
  .jr-house-transactions__search {
    max-width: none;
  }

  .jr-house-transactions__summary {
    display: none;
  }

  .jr-house-transactions__table :deep(th.jr-col-actions),
  .jr-house-transactions__table :deep(td.jr-col-actions) {
    width: 3.25rem;
  }
}
</style>
