<template>
  <TxCard class="shadow-sm mt-0">
    <template #header>
      <div
        class="d-flex flex-wrap justify-content-between align-items-center w-100 gap-2">
        <h5 class="text-primary mb-0 fw-semibold listview-title">
          Piece Work List
        </h5>
        <div>
          <button
            v-if="hasPermission('ctrctsapp.add_workprice')"
            class="btn btn-success btn-sm"
            @click="createPrice">
            + New Price Work
          </button>
        </div>
      </div>
    </template>

    <div class="card-body">
      <!-- Toolbar: stats + refresh -->
      <div
        class="listview-toolbar d-flex flex-wrap align-items-center gap-2 mb-3">
        <span class="badge bg-primary stats-badge">
          {{ filteredPrices.length }} Total
        </span>
        <span
          class="listview-toolbar-divider d-none d-sm-inline"
          aria-hidden="true"></span>
        <button
          type="button"
          class="btn btn-outline-success btn-sm listview-refresh-btn"
          @click="fetchPrices">
          Refresh List
        </button>
      </div>

      <!-- Filters: entries per page + search -->
      <div class="listview-filters row g-2 g-md-3 mb-3 align-items-end">
        <div class="col-12 col-sm-6 col-lg-4 col-xl-3">
          <div class="listview-filter-group">
            <label for="workprice-per-page" class="form-label small mb-1">
              Entries per page:
            </label>
            <select
              id="workprice-per-page"
              v-model="perPage"
              class="form-select form-select-sm">
              <option v-for="n in [5, 10, 25, 50]" :key="n" :value="n">
                {{ n }}
              </option>
            </select>
          </div>
        </div>
        <div class="col-12 col-sm-6 col-lg-5 col-xl-4 ms-lg-auto">
          <div class="listview-filter-group">
            <label for="workprice-search" class="form-label small mb-1">
              Search:
            </label>
            <input
              id="workprice-search"
              v-model="search"
              type="search"
              class="form-control form-control-sm"
              placeholder="Search by description, unit price..."
              autocomplete="off" />
          </div>
        </div>
      </div>

      <BOverlay :show="loading" rounded="sm" opacity="0.85" variant="light">
        <template #overlay>
          <div class="text-center">
            <BSpinner class="mb-3" />
            <div class="h5 text-primary">Loading Pieces...</div>
          </div>
        </template>

        <b-table
          :items="filteredPrices"
          :fields="fields"
          :per-page="perPage"
          :current-page="currentPage"
          bordered
          hover
          responsive
          striped>
          <template #cell(id)="data">
            {{ data.item.id }}
          </template>
          <template #cell(name)="data">
            {{ data.item.name }}
          </template>
          <template #cell(trim)="data">$ {{ data.item.trim }}</template>
          <template #cell(rough)="data">$ {{ data.item.rough }}</template>
          <template #cell(unit_price)="data">
            {{ data.item.unit_price }}
          </template>
          <template #cell(actions)="data">
            <div class="btn-group btn-group-sm" role="group">
              <button
                v-if="hasPermission('ctrctsapp.view_workprice')"
                type="button"
                class="btn btn-outline-success me-1"
                @click="viewPrice(data.item.id)">
                View
              </button>
              <button
                v-if="hasPermission('ctrctsapp.change_workprice')"
                type="button"
                class="btn btn-outline-primary me-1"
                @click="editPrice(data.item.id)">
                Edit
              </button>
            </div>
          </template>
        </b-table>
      </BOverlay>

      <div class="d-flex justify-content-end mt-3">
        <b-pagination
          v-model="currentPage"
          :total-rows="filteredPrices.length"
          :per-page="perPage" />
      </div>
    </div>
  </TxCard>
</template>

<script>
import TxCard from "@/components/layout/TxCard.vue";
import { BOverlay, BSpinner } from "bootstrap-vue-next";
import axios from "axios";

export default {
  name: "WorkPricesView",
  components: { TxCard, BOverlay, BSpinner },
  data() {
    return {
      loading: false,
      prices: [],
      search: "",
      perPage: 25,
      currentPage: 1,
    };
  },
  computed: {
    filteredPrices() {
      if (!this.search.trim()) return this.prices;
      const q = this.search.toLowerCase().trim();
      return this.prices.filter(
        (p) =>
          (p.name || "").toLowerCase().includes(q) ||
          (p.unit_price || "").toString().toLowerCase().includes(q)
      );
    },
    fields() {
      return [
        {
          key: "id",
          label: "ID",
          sortable: true,
          thClass: "text-center",
          tdClass: "text-center",
        },
        {
          key: "name",
          label: "Description",
          sortable: true,
          thClass: "text-start",
          tdClass: "text-start",
        },
        {
          key: "trim",
          label: "USD$ Trim",
          thClass: "text-center",
          tdClass: "text-center",
        },
        {
          key: "rough",
          label: "USD$ Rough",
          thClass: "text-center",
          tdClass: "text-center",
        },
        {
          key: "unit_price",
          label: "Unit Price Type",
          sortable: true,
          thClass: "text-start",
          tdClass: "text-start",
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
    },
  },
  mounted() {
    this.fetchPrices();
  },
  methods: {
    fetchPrices() {
      this.loading = true;
      axios
        .get("/api/workprice/")
        .then((response) => {
          this.prices = response.data;
          this.currentPage = 1;
        })
        .catch((error) => {
          console.error("Error fetching work prices:", error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    createPrice() {
      this.$router.push({ name: "work-prices-form" });
    },
    editPrice(id) {
      this.$router.push({ name: "work-prices-edit", params: { id } });
    },
    viewPrice(id) {
      this.$router.push({ name: "work-prices-view", params: { id } });
    },
  },
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
.listview-filters .listview-filter-group label {
  font-size: 0.8rem;
  color: var(--bs-secondary-color);
}
.form-select-sm,
.form-control-sm {
  font-size: 0.8rem;
}
</style>
