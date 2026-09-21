<template>
  <div class="jr-pilot jr-house-contracts">
    <div class="jr-house-contracts__header">
      <h3 class="jr-house-contracts__title">Contracts</h3>
      <JRButton
        v-if="canAdd"
        type="button"
        size="sm"
        @click="goToContractForm">
        + New Contract
      </JRButton>
    </div>

    <JRToolbar>
      <template #start>
        <div class="jr-house-contracts__search">
          <label class="jr-sr-only" for="house-contracts-search">
            Search contracts
          </label>
          <span class="jr-house-contracts__search-icon" aria-hidden="true">
            <SearchIcon />
          </span>
          <JRInput
            inputId="house-contracts-search"
            v-model="search"
            type="search"
            placeholder="Search by type, model, ID…"
            autocomplete="off"
            :spellcheck="false"
            enterkeyhint="search" />
        </div>
      </template>

      <template #stats>
        <JRBadge
          :value="`${filteredContracts.length} Total`"
          severity="secondary" />
      </template>

      <template #actions>
        <JRButton
          type="button"
          variant="ghost"
          size="sm"
          class="jr-house-contracts__refresh"
          @click="refreshTable">
          <RefreshIcon />
          Refresh
        </JRButton>
      </template>
    </JRToolbar>

    <JRScrollArea
      class="jr-house-contracts__scroll"
      height="var(--jr-wov-body-height, 22rem)">
      <div
        class="jr-house-contracts__table"
        :aria-busy="loading ? 'true' : 'false'">
        <JRDataTable
          :value="filteredContracts"
          :loading="loading"
          dataKey="id"
          :paginator="filteredContracts.length > perPage"
          :rows="perPage"
          :first="tableFirst"
          sortField="id"
          :sortOrder="-1"
          paginatorTemplate="PrevPageLink CurrentPageReport NextPageLink"
          currentPageReportTemplate="{first}–{last} of {totalRecords}"
          scrollable
          stripedRows
          tableStyle="min-width: 36rem"
          :emptyTitle="loading ? '' : emptyTitle"
          :emptyDescription="loading ? '' : emptyDescription"
          @page="onTablePage">
          <template #empty>
            <JREmptyState
              v-if="!loading"
              :title="emptyTitle"
              :description="emptyDescription">
              <JRButton
                v-if="canAdd && !search.trim()"
                type="button"
                size="sm"
                @click="goToContractForm">
                + New Contract
              </JRButton>
              <JRButton
                v-else-if="search.trim()"
                type="button"
                variant="ghost"
                size="sm"
                @click="search = ''">
                Clear search
              </JRButton>
            </JREmptyState>
          </template>

          <Column field="id" header="ID" sortable style="width: 4rem">
            <template #body="{ data }">
              {{ data.id }}
            </template>
          </Column>

          <Column field="type" header="Type" sortable style="width: 6rem">
            <template #body="{ data }">
              <JRBadge :value="data.type || '—'" severity="info" />
            </template>
          </Column>

          <Column field="date_created" header="Date" sortable style="width: 8rem">
            <template #body="{ data }">
              {{ formatDate(data.date_created) }}
            </template>
          </Column>

          <Column field="house_model" header="Model" sortable>
            <template #body="{ data }">
              {{ data.house_model?.name || "—" }}
            </template>
          </Column>

          <Column
          field="sqft"
          header="SqFt"
          sortable
          headerClass="jr-col-num"
          bodyClass="jr-col-num">
          <template #body="{ data }">
            {{ data.sqft ? data.sqft.toLocaleString() : "—" }}
          </template>
        </Column>

        <Column
          field="total"
          header="Total"
          sortable
          headerClass="jr-col-num"
          bodyClass="jr-col-num">
          <template #body="{ data }">
            <strong>{{ currency(data.total) }}</strong>
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
              :entity-label="`Contract ${data.id}`" />
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
import dayjs from "dayjs";
import Swal from "sweetalert2";
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
  name: "ScheduleHouseContractsComponent",
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
      contracts: [],
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
      return this.hasPermission("ctrctsapp.add_contract");
    },
    canView() {
      return this.hasPermission("ctrctsapp.view_contract");
    },
    canChange() {
      return this.hasPermission("ctrctsapp.change_contract");
    },
    hasRowActions() {
      return this.canView || this.canChange;
    },
    filteredContracts() {
      const q = this.search.trim().toLowerCase();
      if (!q) return this.contracts;
      return this.contracts.filter((item) => {
        const type = String(item.type || "").toLowerCase();
        const model = String(item.house_model?.name || "").toLowerCase();
        const id = String(item.id || "");
        return type.includes(q) || model.includes(q) || id.includes(q);
      });
    },
    emptyTitle() {
      if (this.loadError) return "Could not load contracts";
      if (this.search.trim()) return "No matching contracts";
      return "No contracts yet";
    },
    emptyDescription() {
      if (this.loadError) return "Check your connection and try Refresh.";
      if (this.search.trim()) return "Try a different search term.";
      return "No contracts found for this work account.";
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
    getRowActions(contract) {
      const actions = [];
      if (this.canView) {
        actions.push({
          key: "view",
          label: "View",
          severity: "success",
          icon: EyeIcon,
          command: () => this.viewContract(contract.id),
        });
        actions.push({
          key: "print",
          label: "Print",
          severity: "secondary",
          command: () => this.printContract(contract.id),
        });
      }
      if (this.canChange) {
        actions.push({
          key: "edit",
          label: "Edit",
          severity: "primary",
          icon: PencilIcon,
          command: () => this.editContract(contract.id),
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
        await this.getContracts();
        return;
      }

      if (!this.eventId) {
        this.resolvedWorkAccountId = null;
        this.contracts = [];
        this.loading = false;
        this.loadError = false;
        return;
      }

      await this.loadWorkAccountId();
      await this.getContracts();
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
        console.error("Error fetching event data for contracts:", e);
        this.resolvedWorkAccountId = null;
      }
    },
    async getContracts() {
      if (!this.resolvedWorkAccountId) {
        this.contracts = [];
        this.loading = false;
        this.loadError = false;
        return;
      }

      this.loading = true;
      this.loadError = false;
      try {
        const url = `/api/contract/?work_account=${this.resolvedWorkAccountId}&ordering=-id`;
        const response = await axios.get(url);
        const normalizeList = (data) =>
          Array.isArray(data) ? data : data?.results ?? [];
        this.contracts = normalizeList(response.data);
      } catch (error) {
        console.error("Error fetching contracts:", error);
        this.contracts = [];
        this.loadError = true;
      } finally {
        this.loading = false;
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
    viewContract(contractId) {
      this.$router.push({ name: "contract-view", params: { id: contractId } });
    },
    editContract(contractId) {
      const url = this.$router.resolve({
        name: "contract-edit",
        params: { id: contractId },
      });
      window.open(url.href, "_blank");
    },
    async printContract(contractId) {
      try {
        const response = await axios.get(`/api/contract-pdf/${contractId}/`, {
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
            response.data.filename || `contract_${contractId}.pdf`;
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
              response.data.filename || `contract_${contractId}.pdf`;
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
        console.error("Error downloading contract PDF:", error);
        await Swal.fire({
          icon: "error",
          title: "Error",
          text: "Could not generate the PDF document. Please try again.",
          confirmButtonText: "OK",
        });
      }
    },
    goToContractForm() {
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
      this.$nextTick(() => {
        try {
          const query = {};
          if (this.eventId) query.event_id = this.eventId;
          if (this.resolvedWorkAccountId) {
            query.work_account_id = this.resolvedWorkAccountId;
          }
          const resolved = this.$router.resolve({
            name: "contract-form",
            query,
          });
          const href =
            resolved?.href ||
            `/contract-form?${new URLSearchParams(query).toString()}`;
          window.location.href = href;
        } catch (_) {
          const queryString = new URLSearchParams({
            ...(this.eventId && { event_id: this.eventId }),
            ...(this.resolvedWorkAccountId && {
              work_account_id: this.resolvedWorkAccountId,
            }),
          }).toString();
          window.location.href = `/contract-form?${queryString}`;
        }
      });
    },
  },
};
</script>

<style scoped>
.jr-house-contracts {
  display: flex;
  flex-direction: column;
  min-height: 0;
  height: 100%;
}

.jr-house-contracts__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  flex: 0 0 auto;
}

.jr-house-contracts__scroll {
  flex: 1 1 auto;
  min-height: 0;
}

.jr-house-contracts__title {
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text, #111827);
  text-align: left;
}

.jr-house-contracts__search {
  position: relative;
  min-width: 0;
  width: 100%;
  max-width: 22rem;
}

.jr-house-contracts__search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  z-index: 1;
  display: flex;
  color: var(--color-jr-muted, #4b5563);
  pointer-events: none;
  transform: translateY(-50%);
}

.jr-house-contracts__search-icon :deep(svg) {
  width: 1rem;
  height: 1rem;
}

.jr-house-contracts__search :deep(.p-inputtext) {
  padding-left: 2.25rem;
}

.jr-house-contracts__table :deep(th.jr-col-num),
.jr-house-contracts__table :deep(td.jr-col-num) {
  text-align: right;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}

.jr-house-contracts__table :deep(th.jr-col-num .p-datatable-column-header-content) {
  justify-content: flex-end;
}

.jr-house-contracts__table :deep(.jr-empty-state) {
  padding: 2.5rem 1rem;
}

.jr-house-contracts__table :deep(th.jr-col-actions),
.jr-house-contracts__table :deep(td.jr-col-actions) {
  width: 14rem;
  text-align: center;
  white-space: nowrap;
}

.jr-house-contracts__table
  :deep(th.jr-col-actions .p-datatable-column-header-content) {
  display: flex;
  justify-content: center;
  width: 100%;
}

.jr-house-contracts__table :deep(td.jr-col-actions .jr-row-actions) {
  justify-content: center;
  width: 100%;
}

@media (max-width: 767.98px) {
  .jr-house-contracts__search {
    max-width: none;
  }

  .jr-house-contracts__table :deep(th.jr-col-actions),
  .jr-house-contracts__table :deep(td.jr-col-actions) {
    width: 3.25rem;
  }
}
</style>
