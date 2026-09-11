<template>
  <JRPage>
    <JRPageHeader title="Work Prices per Builder" />

    <JRSection title="Builder">
      <div class="jr-wp-builder__builder">
        <JRField
          v-slot="{ describedby }"
          label="Select builder"
          inputId="wp-builder-select">
          <JRSelect
            inputId="wp-builder-select"
            v-model="selectedBuilderId"
            :options="builders"
            optionLabel="name"
            optionValue="id"
            placeholder="Search builder"
            filter
            showClear
            :disabled="buildersLoading"
            :ariaDescribedby="describedby"
            @update:modelValue="onBuilderChange" />
        </JRField>
      </div>
      <p v-if="buildersLoading" class="jr-wp-builder__status" role="status">
        Loading builders…
      </p>
    </JRSection>

    <JRSection v-if="selectedBuilderId" title="Assigned piece work prices">
      <p
        v-if="selectionError"
        id="wp-prices-selection-error"
        class="jr-wp-builder__selection-error"
        role="alert">
        {{ selectionError }}
      </p>
      <div class="jr-wp-builder__toolbar">
        <div class="jr-wp-builder__search">
          <label class="jr-sr-only" for="wp-builder-filter">
            Filter work prices
          </label>
          <JRInput
            inputId="wp-builder-filter"
            v-model="nameFilter"
            type="search"
            placeholder="Filter by description..."
            autocomplete="off"
            :disabled="loading" />
        </div>
        <div class="jr-wp-builder__bulk">
          <JRButton
            type="button"
            variant="ghost"
            size="sm"
            :disabled="loading || !filteredWorkPrices.length"
            @click="selectAll">
            Select All
          </JRButton>
          <JRButton
            type="button"
            variant="ghost"
            size="sm"
            :disabled="loading || !selectedIds.length"
            @click="clearAll">
            Clear
          </JRButton>
        </div>
      </div>

      <p v-if="loading" class="jr-wp-builder__status" role="status">
        Loading work prices…
      </p>

      <div
        v-else-if="filteredWorkPrices.length"
        class="jr-assign-grid"
        :class="{ 'jr-assign-grid--invalid': !!selectionError }"
        role="group"
        aria-label="Piece work prices"
        :aria-describedby="selectionError ? 'wp-prices-selection-error' : undefined">
        <div
          v-for="wp in filteredWorkPrices"
          :key="wp.id"
          class="jr-assign-grid__card">
          <JRCheckbox
            :inputId="`wp-price-${wp.id}`"
            :modelValue="isSelected(wp.id)"
            @update:modelValue="(checked) => togglePrice(wp.id, checked)">
            <span class="jr-assign-grid__text">
              <span class="jr-assign-grid__name">{{ wp.name }}</span>
              <span class="jr-assign-grid__meta">
                Trim {{ formatMoney(wp.trim) }} · Rough {{ formatMoney(wp.rough) }}
                <template v-if="wp.unit_price"> · {{ wp.unit_price }}</template>
              </span>
            </span>
          </JRCheckbox>
        </div>
      </div>

      <JREmptyState
        v-else
        :title="pricesEmptyTitle"
        :description="pricesEmptyDescription" />

      <div class="jr-wp-builder__actions">
        <JRButton
          type="button"
          variant="primary"
          :disabled="loading || saving || !selectedBuilderId"
          @click="updateWorkPriceAssignments">
          {{ saving ? "Saving..." : "Save" }}
        </JRButton>
      </div>
    </JRSection>

    <JREmptyState
      v-else-if="!buildersLoading"
      title="Select a builder"
      description="Choose a builder to assign piece work prices." />

    <p v-if="errorMessage" class="jr-wp-builder__error" role="alert">
      {{ errorMessage }}
    </p>
  </JRPage>
</template>

<script>
import axios from "axios";
import {
  JRPage,
  JRPageHeader,
  JRSection,
  JRField,
  JRSelect,
  JRInput,
  JRButton,
  JRCheckbox,
  JREmptyState,
} from "@ui";

export default {
  name: "WorkPricesBuilderComponent",
  components: {
    JRPage,
    JRPageHeader,
    JRSection,
    JRField,
    JRSelect,
    JRInput,
    JRButton,
    JRCheckbox,
    JREmptyState,
  },
  data() {
    return {
      builders: [],
      selectedBuilderId: null,
      workPrices: [],
      selectedIds: [],
      nameFilter: "",
      loading: false,
      saving: false,
      buildersLoading: true,
      errorMessage: "",
      selectionError: "",
    };
  },
  computed: {
    filteredWorkPrices() {
      const q = this.nameFilter.trim().toLowerCase();
      if (!q) return this.workPrices;
      return this.workPrices.filter((wp) =>
        (wp.name || "").toLowerCase().includes(q)
      );
    },
    pricesEmptyTitle() {
      if (this.nameFilter.trim() && this.workPrices.length) {
        return "No matching prices";
      }
      return "No piece work prices";
    },
    pricesEmptyDescription() {
      if (this.nameFilter.trim() && this.workPrices.length) {
        return `No prices match “${this.nameFilter.trim()}”.`;
      }
      return "Create piece work prices first, then assign them here.";
    },
  },
  mounted() {
    this.fetchBuilders();
  },
  methods: {
    formatMoney(value) {
      const n = Number(value);
      if (!Number.isFinite(n)) return "$0.00";
      return n.toLocaleString("en-US", {
        style: "currency",
        currency: "USD",
      });
    },
    clearSelectionError() {
      this.selectionError = "";
    },
    isSelected(id) {
      return this.selectedIds.includes(id);
    },
    togglePrice(id, checked) {
      if (checked) {
        if (!this.selectedIds.includes(id)) {
          this.selectedIds = [...this.selectedIds, id];
        }
        this.clearSelectionError();
        return;
      }
      this.selectedIds = this.selectedIds.filter((x) => x !== id);
    },
    async fetchBuilders() {
      this.buildersLoading = true;
      this.errorMessage = "";
      try {
        const response = await axios.get("/api/builder/");
        this.builders = Array.isArray(response.data)
          ? response.data
          : response.data?.results || [];

        const urlParams = new URLSearchParams(window.location.search);
        const builderId = urlParams.get("builder");
        if (builderId) {
          const id = parseInt(builderId, 10);
          if (this.builders.some((b) => b.id === id)) {
            this.selectedBuilderId = id;
            await this.fetchWorkPrices();
          }
        }
      } catch (error) {
        this.errorMessage = "Failed to load builders.";
        console.error("Error fetching builders:", error);
      } finally {
        this.buildersLoading = false;
      }
    },
    onBuilderChange() {
      this.selectedIds = [];
      this.nameFilter = "";
      this.clearSelectionError();
      this.fetchWorkPrices();
    },
    async fetchWorkPrices() {
      if (!this.selectedBuilderId) return;
      this.loading = true;
      this.errorMessage = "";
      this.clearSelectionError();
      try {
        const response = await axios.get(`/api/workprice/`);
        this.workPrices = Array.isArray(response.data)
          ? response.data
          : response.data?.results || [];

        const assignedResponse = await axios.get(
          `/api/builder/${this.selectedBuilderId}/workprices/`
        );
        const assigned = Array.isArray(assignedResponse.data)
          ? assignedResponse.data
          : assignedResponse.data?.results || [];
        this.selectedIds = assigned.map((wp) => wp.id).filter((id) => id != null);
      } catch (error) {
        this.errorMessage = "Error loading work prices.";
        console.error("Error fetching work prices:", error);
      } finally {
        this.loading = false;
      }
    },
    async updateWorkPriceAssignments() {
      if (!this.selectedBuilderId) return;
      if (!this.selectedIds.length) {
        this.selectionError = "Select at least one piece work price.";
        this.notifyError?.(this.selectionError);
        this.$nextTick(() => {
          document.getElementById("wp-builder-filter")?.focus();
        });
        return;
      }
      this.clearSelectionError();
      this.saving = true;
      this.errorMessage = "";
      try {
        await axios.post(
          `/api/builder/${this.selectedBuilderId}/assign-workprices/`,
          { work_price_ids: [...this.selectedIds] }
        );
        this.notifyToastSuccess?.("Assignments updated successfully.");
      } catch (error) {
        this.errorMessage = "Error updating assignments.";
        console.error("Error updating assignments:", error);
        this.notifyError?.("Error updating assignments.");
      } finally {
        this.saving = false;
      }
    },
    selectAll() {
      const ids = new Set(this.selectedIds);
      this.filteredWorkPrices.forEach((wp) => ids.add(wp.id));
      this.selectedIds = Array.from(ids);
      this.clearSelectionError();
    },
    clearAll() {
      if (!this.nameFilter.trim()) {
        this.selectedIds = [];
        return;
      }
      const filteredIds = new Set(this.filteredWorkPrices.map((wp) => wp.id));
      this.selectedIds = this.selectedIds.filter((id) => !filteredIds.has(id));
    },
  },
};
</script>

<style scoped>
.jr-wp-builder__builder {
  max-width: 28rem;
}

.jr-wp-builder__toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.jr-wp-builder__search {
  flex: 1 1 14rem;
  min-width: 0;
  max-width: 24rem;
}

.jr-wp-builder__bulk {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.jr-wp-builder__status {
  margin: 0.5rem 0;
  color: var(--color-jr-muted);
  font-size: 0.875rem;
}

.jr-wp-builder__selection-error {
  margin: 0 0 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-jr-danger-text);
}

.jr-assign-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 0.25rem 1rem;
  max-height: min(28rem, 55vh);
  overflow: auto;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface);
}

.jr-assign-grid--invalid {
  border-color: var(--color-jr-danger);
}

@media (min-width: 640px) {
  .jr-assign-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 900px) {
  .jr-assign-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (min-width: 1200px) {
  .jr-assign-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

.jr-assign-grid__card {
  min-width: 0;
}

/* Unlayered scoped rules beat Bootstrap `label { display }` over DS @layer. */
.jr-assign-grid :deep(.jr-checkbox) {
  display: inline-flex;
  align-items: flex-start;
  column-gap: 0.85rem;
  width: 100%;
  min-height: 2.25rem;
  text-align: left;
}

.jr-assign-grid :deep(.jr-checkbox .p-checkbox) {
  flex: 0 0 auto;
  margin-top: 0.15rem;
}

.jr-assign-grid :deep(.jr-checkbox__label) {
  margin-inline-start: 0.15rem;
}

.jr-assign-grid__text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  min-width: 0;
}

.jr-assign-grid__name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-jr-text);
  overflow-wrap: anywhere;
  line-height: 1.3;
}

.jr-assign-grid__meta {
  font-size: 0.75rem;
  color: var(--color-jr-muted);
  font-variant-numeric: tabular-nums;
  line-height: 1.3;
}

.jr-wp-builder__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  position: sticky;
  bottom: 0;
  z-index: 2;
  padding: 0.75rem 0 0.25rem;
  margin-top: 0.5rem;
  background: var(--color-jr-page);
  border-top: 1px solid var(--color-jr-border);
}

.jr-wp-builder__error {
  margin-top: 0.75rem;
  color: var(--color-jr-danger-text);
  font-size: 0.875rem;
}
</style>
