<template>
  <JRPage class="jr-mr-field">
    <JRPageHeader :title="headerTitle">
      <template #actions>
        <JRButton type="button" variant="ghost" size="sm" @click="goBack">
          Back
        </JRButton>
      </template>
    </JRPageHeader>
    <p class="jr-mr-field__context">{{ contextLine }}</p>

    <JRToolbar>
      <template #start>
        <label class="jr-sr-only" for="mr-search">Search material</label>
        <JRInput
          inputId="mr-search"
          v-model="search"
          type="search"
          placeholder="Search material..."
          autocomplete="off" />
      </template>
      <template #actions>
        <JRSelect
          inputId="mr-category"
          ariaLabel="Category"
          v-model="categoryId"
          :options="categoryOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Category" />
        <JRSelect
          inputId="mr-brand"
          ariaLabel="Brand"
          v-model="brandId"
          :options="brandOptions"
          optionLabel="label"
          optionValue="value"
          placeholder="Brand" />
      </template>
    </JRToolbar>

    <div class="jr-mr-catalog" :aria-busy="loading ? 'true' : 'false'">
      <DataView :value="viewItems" :layout="layout" dataKey="id">
        <template #header>
          <div class="jr-mr-layout">
            <SelectButton
              v-model="layout"
              :options="layoutOptions"
              :allowEmpty="false"
              aria-label="Layout">
              <template #option="{ option }">
                <Bars v-if="option === 'list'" aria-hidden="true" />
                <Table v-else aria-hidden="true" />
                <span class="jr-sr-only">{{ option === 'list' ? 'List' : 'Grid' }}</span>
              </template>
            </SelectButton>
          </div>
        </template>

        <template #list="{ items }">
          <div class="jr-mr-list">
            <article
              v-for="item in items"
              :key="item.id"
              class="jr-mr-row"
              :class="{ 'jr-mr-row--added': !loading && selection[item.id] }">
              <template v-if="loading">
                <Skeleton class="jr-mr-media" width="8.75rem" height="6.5rem" borderRadius="var(--radius-jr-panel)" />
                <div class="jr-mr-row__body">
                  <div class="jr-mr-row__identity">
                    <Skeleton width="6rem" height="0.8rem" />
                    <Skeleton width="12rem" height="1.25rem" />
                    <Skeleton width="4.5rem" height="1.6rem" borderRadius="var(--radius-jr-panel)" />
                  </div>
                  <div class="jr-mr-row__aside">
                    <Skeleton width="3rem" height="1.75rem" />
                    <Skeleton width="9rem" height="2.25rem" />
                  </div>
                </div>
              </template>
              <template v-else>
                <div class="jr-mr-media">
                  <img
                    v-if="productImage(item)"
                    :src="productImage(item)"
                    :alt="item.name"
                    class="jr-mr-media__img"
                    width="140"
                    height="104"
                    loading="lazy"
                    decoding="async"
                    @error="onImageError(item)" />
                  <span v-else class="jr-mr-media__ph" aria-hidden="true" />
                  <span class="jr-mr-tag" :data-tone="stockTone(item).tone">{{ stockTone(item).label }}</span>
                </div>
                <div class="jr-mr-row__body">
                  <div class="jr-mr-row__identity">
                    <p v-if="item.category_name" class="jr-mr-category">{{ item.category_name }}</p>
                    <h2 class="jr-mr-name">{{ item.name }}</h2>
                    <p class="jr-mr-sku">{{ item.sku || 'No SKU' }}</p>
                  </div>
                  <div class="jr-mr-row__aside">
                    <p class="jr-mr-stock">
                      <span class="jr-mr-stock__value">{{ stockLabel(item) }}</span>
                      <span class="jr-mr-stock__caption">available</span>
                    </p>
                    <div class="jr-mr-actions">
                      <div class="jr-mr-qty">
                        <button type="button" aria-label="Decrease quantity" @click="step(item, -1)">−</button>
                        <span>{{ displayQty(item) }}</span>
                        <button type="button" aria-label="Increase quantity" @click="step(item, 1)">+</button>
                      </div>
                      <JRButton
                        v-if="!selection[item.id]"
                        type="button"
                        size="sm"
                        @click="add(item)">
                        Add
                      </JRButton>
                      <p v-else class="jr-mr-added">In request</p>
                    </div>
                  </div>
                </div>
              </template>
            </article>
          </div>
        </template>

        <template #grid="{ items }">
          <div class="jr-mr-grid">
            <article v-for="item in items" :key="item.id" class="jr-mr-card">
              <template v-if="loading">
                <Skeleton width="100%" height="9rem" borderRadius="var(--radius-jr-panel)" />
                <Skeleton width="5rem" height="0.8rem" />
                <Skeleton width="80%" height="1.25rem" />
                <Skeleton width="4rem" height="1.75rem" />
                <Skeleton width="100%" height="2.25rem" />
              </template>
              <template v-else>
                <div class="jr-mr-media">
                  <img
                    v-if="productImage(item)"
                    :src="productImage(item)"
                    :alt="item.name"
                    class="jr-mr-media__img"
                    width="240"
                    height="144"
                    loading="lazy"
                    decoding="async"
                    @error="onImageError(item)" />
                  <span v-else class="jr-mr-media__ph" aria-hidden="true" />
                  <span class="jr-mr-tag" :data-tone="stockTone(item).tone">{{ stockTone(item).label }}</span>
                </div>
                <p v-if="item.category_name" class="jr-mr-category">{{ item.category_name }}</p>
                <h2 class="jr-mr-name">{{ item.name }}</h2>
                <p class="jr-mr-stock">
                  <span class="jr-mr-stock__value">{{ stockLabel(item) }}</span>
                  <span class="jr-mr-stock__caption">available</span>
                </p>
                <p class="jr-mr-sku">{{ item.sku || 'No SKU' }}</p>
                <div class="jr-mr-actions">
                  <div class="jr-mr-qty">
                    <button type="button" aria-label="Decrease quantity" @click="step(item, -1)">−</button>
                    <span>{{ displayQty(item) }}</span>
                    <button type="button" aria-label="Increase quantity" @click="step(item, 1)">+</button>
                  </div>
                  <JRButton
                    v-if="!selection[item.id]"
                    type="button"
                    size="sm"
                    @click="add(item)">
                    Add
                  </JRButton>
                  <p v-else class="jr-mr-added">In request</p>
                </div>
              </template>
            </article>
          </div>
        </template>

        <template #empty>
          <JREmptyState
            title="No materials"
            description="Try another search, category, or brand." />
        </template>
      </DataView>
    </div>

    <div class="jr-mr-field__pager">
      <JRButton type="button" variant="ghost" size="sm" :disabled="page <= 1" @click="page -= 1">
        Previous
      </JRButton>
      <span>Page {{ page }}</span>
      <JRButton type="button" variant="ghost" size="sm" :disabled="!hasMore" @click="page += 1">
        Next
      </JRButton>
    </div>

    <div v-if="itemCount" class="jr-mr-dock">
      <button
        type="button"
        class="jr-mr-float"
        @click="summaryOpen = true">
        Request ({{ itemCount }} {{ itemCount === 1 ? 'item' : 'items' }})
      </button>
    </div>

    <JRDialog
      :visible="summaryOpen"
      header="Material Request"
      size="wide"
      :confirm-label="submitting ? 'Submitting...' : 'Submit Material Request'"
      :confirm-disabled="submitting || !selectedLines.length"
      cancel-label="Cancel"
      @update:visible="summaryOpen = $event"
      @confirm="submit">
      <p class="jr-mr-summary__meta">
        {{ workAccountTitle }}<br />
        {{ phase }}<br />
        {{ requestedBy }}
      </p>
      <table class="jr-mr-summary__table">
        <thead>
          <tr>
            <th>Material</th>
            <th>Qty</th>
            <th><span class="jr-sr-only">Remove</span></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="line in selectedLines" :key="line.id">
            <td>{{ line.name }}</td>
            <td>
              <div class="jr-mr-summary__qty">
                <button type="button" aria-label="Decrease quantity" @click="adjustLine(line, -1)">−</button>
                <input
                  type="number"
                  min="1"
                  :aria-label="`Quantity for ${line.name}`"
                  :value="line.quantity"
                  @change="setLineQty(line, $event.target.value)" />
                <button type="button" aria-label="Increase quantity" @click="adjustLine(line, 1)">+</button>
              </div>
            </td>
            <td>
              <JRButton type="button" variant="ghost" size="sm" @click="removeLine(line)">
                Remove
              </JRButton>
            </td>
          </tr>
          <tr v-if="!selectedLines.length">
            <td colspan="3">No materials in this request.</td>
          </tr>
        </tbody>
      </table>
      <JRField label="Notes" inputId="mr-notes">
        <JRTextarea
          inputId="mr-notes"
          v-model="notes"
          rows="3"
          placeholder="Need material to finish master bedroom." />
      </JRField>
      <p v-if="error" class="jr-mr-summary__error" role="alert">{{ error }}</p>
    </JRDialog>
  </JRPage>
</template>

<script>
import axios from 'axios';
import DataView from 'primevue/dataview';
import SelectButton from 'primevue/selectbutton';
import Skeleton from 'primevue/skeleton';
import Bars from '@primeicons/vue/bars';
import Table from '@primeicons/vue/table';
import {
  JRPage,
  JRPageHeader,
  JRToolbar,
  JRButton,
  JRInput,
  JRSelect,
  JREmptyState,
  JRDialog,
  JRField,
  JRTextarea,
} from '@/ui';

export default {
  name: 'MissingMaterialView',
  components: {
    DataView,
    SelectButton,
    Skeleton,
    Bars,
    Table,
    JRPage,
    JRPageHeader,
    JRToolbar,
    JRButton,
    JRInput,
    JRSelect,
    JREmptyState,
    JRDialog,
    JRField,
    JRTextarea,
  },
  data() {
    return {
      search: '',
      categoryId: null,
      brandId: null,
      categories: [],
      brands: [],
      products: [],
      page: 1,
      perPage: 24,
      totalRows: 0,
      loading: false,
      selection: {},
      draft: {},
      brokenImages: {},
      notes: '',
      summaryOpen: false,
      submitting: false,
      error: '',
      layout: 'list',
      layoutOptions: ['list', 'grid'],
      workAccountTitle: '',
      phase: '',
      requestedBy: '',
      searchTimer: null,
    };
  },
  computed: {
    headerTitle() {
      return this.workAccountTitle
        ? `Missing Material — ${this.workAccountTitle}`
        : 'Missing Material';
    },
    contextLine() {
      return [this.phase, this.requestedBy].filter(Boolean).join(' · ');
    },
    categoryOptions() {
      return [{ label: 'All categories', value: null }, ...this.categories];
    },
    brandOptions() {
      return [{ label: 'All brands', value: null }, ...this.brands];
    },
    selectedLines() {
      return Object.values(this.selection);
    },
    itemCount() {
      return this.selectedLines.reduce((sum, line) => sum + Number(line.quantity || 0), 0);
    },
    hasMore() {
      return this.page * this.perPage < this.totalRows;
    },
    viewItems() {
      if (!this.loading) return this.products;
      return Array.from({ length: 6 }, (_, index) => ({ id: `skeleton-${index}` }));
    },
  },
  watch: {
    search() {
      clearTimeout(this.searchTimer);
      this.searchTimer = setTimeout(() => {
        this.page = 1;
        this.loadProducts();
      }, 300);
    },
    categoryId() {
      this.page = 1;
      this.loadProducts();
    },
    brandId() {
      this.page = 1;
      this.loadProducts();
    },
    page() {
      this.loadProducts();
    },
  },
  mounted() {
    this.loadContext();
    this.loadFilters();
    this.loadProducts();
  },
  methods: {
    stockLabel(item) {
      if (item.total_stock === null || item.total_stock === undefined) return '—';
      return item.total_stock;
    },
    stockTone(item) {
      const stock = Number(item.total_stock);
      if (!Number.isFinite(stock)) return { label: 'Unknown', tone: 'muted' };
      const reorder = Number(item.reorder_level);
      if (stock <= 0) return { label: 'Out', tone: 'danger' };
      if (Number.isFinite(reorder) && reorder > 0 && stock <= reorder) {
        return { label: 'Low', tone: 'warning' };
      }
      return { label: 'In stock', tone: 'success' };
    },
    productImage(item) {
      if (!item?.id || this.brokenImages[item.id]) return '';
      return item.image || '';
    },
    onImageError(item) {
      if (!item?.id) return;
      this.brokenImages = { ...this.brokenImages, [item.id]: true };
    },
    displayQty(item) {
      if (this.selection[item.id]) return this.selection[item.id].quantity;
      return this.draft[item.id] || 1;
    },
    step(item, delta) {
      if (this.selection[item.id]) {
        const next = Number(this.selection[item.id].quantity) + delta;
        if (next <= 0) {
          const nextSelection = { ...this.selection };
          delete nextSelection[item.id];
          this.selection = nextSelection;
          return;
        }
        this.selection = {
          ...this.selection,
          [item.id]: { ...this.selection[item.id], quantity: next },
        };
        return;
      }
      const current = this.draft[item.id] || 1;
      this.draft = { ...this.draft, [item.id]: Math.max(1, current + delta) };
    },
    add(item) {
      const quantity = this.draft[item.id] || 1;
      this.selection = {
        ...this.selection,
        [item.id]: {
          id: item.id,
          name: item.name,
          sku: item.sku,
          quantity,
        },
      };
    },
    adjustLine(line, delta) {
      this.setLineQty(line, Number(line.quantity) + delta);
    },
    setLineQty(line, value) {
      const quantity = Math.floor(Number(value));
      if (!Number.isFinite(quantity) || quantity <= 0) {
        this.removeLine(line);
        return;
      }
      this.selection = {
        ...this.selection,
        [line.id]: { ...this.selection[line.id], quantity },
      };
    },
    removeLine(line) {
      const nextSelection = { ...this.selection };
      delete nextSelection[line.id];
      this.selection = nextSelection;
    },
    async loadContext() {
      const eventId = this.$route.params.eventId;
      const workAccountId = this.$route.params.workAccountId;
      try {
        const { data } = await axios.get(`/api/work-accounts/${workAccountId}/`);
        this.workAccountTitle = data.title || '';
      } catch {
        this.workAccountTitle = '';
      }
      try {
        const { data } = await axios.get(`/api/schedule/${eventId}/`);
        this.phase = data.crew_category || '';
        if (!this.phase && data.crew) {
          const crew = await axios.get(`/api/crews/${data.crew}/`);
          this.phase = crew.data.category_name || '';
        }
        if (!this.workAccountTitle) {
          this.workAccountTitle = data.work_account_title || data.title || '';
        }
      } catch {
        this.phase = '';
      }
      try {
        const { data } = await axios.get('/api/auth/me/');
        this.requestedBy = data.username || '';
      } catch {
        this.requestedBy = '';
      }
    },
    unwrapList(data) {
      if (Array.isArray(data)) return data;
      if (Array.isArray(data?.items)) return data.items;
      if (Array.isArray(data?.results)) return data.results;
      return [];
    },
    async loadFilters() {
      try {
        const [categories, brands] = await Promise.all([
          axios.get('/api/productcategory-provider/', { params: { page: 1, per_page: 200 } }),
          axios.get('/api/productbrand/', { params: { page_size: 200 } }),
        ]);
        this.categories = this.unwrapList(categories.data).map((row) => ({
          label: row.name,
          value: row.id,
        }));
        this.brands = this.unwrapList(brands.data).map((row) => ({
          label: row.name,
          value: row.id,
        }));
      } catch {
        this.categories = [];
        this.brands = [];
      }
    },
    async loadProducts() {
      this.loading = true;
      this.brokenImages = {};
      try {
        const params = {
          page: this.page,
          per_page: this.perPage,
          is_active: 'true',
          search: this.search.trim(),
        };
        if (this.categoryId) params.category = this.categoryId;
        if (this.brandId) params.brand = this.brandId;
        const { data } = await axios.get('/api/products-provider/', { params });
        this.products = data.items || [];
        this.totalRows = data.totalRows || 0;
      } catch {
        this.products = [];
        this.totalRows = 0;
      } finally {
        this.loading = false;
      }
    },
    async submit() {
      this.submitting = true;
      this.error = '';
      try {
        await axios.post('/api/material-requests/', {
          work_account: Number(this.$route.params.workAccountId),
          work_order: Number(this.$route.params.eventId),
          notes: this.notes,
          lines: this.selectedLines.map((line) => ({
            product: line.id,
            quantity: line.quantity,
          })),
        });
        this.summaryOpen = false;
        this.selection = {};
        this.notes = '';
        this.notifyToastSuccess('Material request submitted.');
        this.goBack();
      } catch (err) {
        const detail = err?.response?.data;
        this.error = detail?.lines || detail?.work_order || detail?.document_type || detail?.detail || 'Could not submit the material request.';
        if (Array.isArray(this.error)) this.error = this.error.join(' ');
        if (typeof this.error === 'object') this.error = 'Could not submit the material request.';
      } finally {
        this.submitting = false;
      }
    },
    goBack() {
      this.$router.push({
        name: 'work-order-viewer',
        params: { id: this.$route.params.workAccountId },
        query: { tab: 'materials' },
      });
    },
  },
};
</script>

<style scoped>
.jr-mr-field__context {
  margin: 0 0 1rem;
  color: var(--color-jr-muted, #4b5563);
}
.jr-mr-catalog :deep(.p-dataview) {
  overflow: hidden;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface, #fff);
}
.jr-mr-catalog :deep(.p-dataview-header) {
  padding: 0.85rem 1.25rem;
  border-bottom: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface, #fff);
}
.jr-mr-catalog :deep(.p-dataview-content) {
  background: var(--color-jr-surface, #fff);
}
.jr-mr-layout {
  display: flex;
  justify-content: flex-end;
}
.jr-mr-layout :deep(svg) {
  width: 1rem;
  height: 1rem;
}
.jr-mr-list {
  display: flex;
  flex-direction: column;
}
.jr-mr-row {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.25rem 1.5rem;
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
}
.jr-mr-row:first-child {
  border-top: 0;
}
.jr-mr-row--added {
  background: var(--color-jr-success-subtle);
}
.jr-mr-row__body {
  display: flex;
  flex: 1 1 auto;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  min-width: 0;
}
.jr-mr-row__identity {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.35rem;
  min-width: 0;
}
.jr-mr-row__aside {
  display: flex;
  flex-shrink: 0;
  flex-direction: column;
  align-items: flex-end;
  gap: 1rem;
}
.jr-mr-media {
  position: relative;
  flex: 0 0 8.75rem;
  width: 8.75rem;
  height: 6.5rem;
}
.jr-mr-media__img,
.jr-mr-media__ph {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface-muted, #f9fafb);
}
.jr-mr-media__ph {
  border: 1px dashed var(--color-jr-hover-border, #d1d5db);
}
.jr-mr-tag {
  position: absolute;
  top: 0.35rem;
  left: 0.35rem;
  padding: 0.12rem 0.4rem;
  border-radius: var(--radius-jr-control);
  background: var(--color-jr-surface-muted, #f9fafb);
  color: var(--color-jr-muted, #4b5563);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  line-height: 1.3;
  text-transform: uppercase;
}
.jr-mr-tag[data-tone="success"] {
  background: var(--color-jr-success-subtle);
  color: var(--color-jr-success-text, #166534);
}
.jr-mr-tag[data-tone="warning"] {
  background: var(--color-jr-warning-subtle);
  color: var(--color-jr-warning-text, #92400e);
}
.jr-mr-tag[data-tone="danger"] {
  background: var(--color-jr-danger-subtle);
  color: var(--color-jr-danger-text, #991b1b);
}
.jr-mr-category {
  margin: 0;
  color: var(--color-jr-muted, #4b5563);
  font-size: 0.8125rem;
}
.jr-mr-name {
  margin: 0;
  color: var(--color-jr-text, #111827);
  font-size: 1.3125rem;
  font-weight: 600;
  line-height: 1.25;
  overflow-wrap: anywhere;
}
.jr-mr-sku {
  margin: 0;
  padding: 0.2rem 0.65rem;
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface, #fff);
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.08);
  color: var(--color-jr-text, #111827);
  font-size: 0.8125rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
.jr-mr-stock {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  margin: 0;
}
.jr-mr-stock__value {
  color: var(--color-jr-text, #111827);
  font-size: 1.3125rem;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  letter-spacing: -0.02em;
  line-height: 1.1;
}
.jr-mr-stock__caption {
  color: var(--color-jr-muted, #4b5563);
  font-size: 0.75rem;
}
.jr-mr-actions {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}
.jr-mr-added {
  margin: 0;
  color: var(--color-jr-success-text, #166534);
  font-size: 0.875rem;
  font-weight: 600;
}
.jr-mr-qty {
  display: flex;
  align-items: center;
  gap: 0.65rem;
}
.jr-mr-qty span {
  min-width: 1.25rem;
  font-variant-numeric: tabular-nums;
  font-weight: 600;
  text-align: center;
}
.jr-mr-qty button {
  width: 2.25rem;
  height: 2.25rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-control);
  background: var(--color-jr-surface, #fff);
  color: var(--color-jr-text, #111827);
  cursor: pointer;
}
.jr-mr-qty button:focus-visible {
  outline: 2px solid var(--color-jr-primary, #2563eb);
  outline-offset: 2px;
}
.jr-mr-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(16rem, 1fr));
  gap: 1rem;
  padding: 1rem;
}
.jr-mr-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.4rem;
  padding: 1rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-surface, #fff);
}
.jr-mr-card .jr-mr-media {
  flex: none;
  width: 100%;
  height: 9rem;
}
.jr-mr-card .jr-mr-stock {
  align-items: flex-start;
}
.jr-mr-card .jr-mr-actions {
  width: 100%;
  margin-top: auto;
  padding-top: 0.65rem;
}
@media (max-width: 767.98px) {
  .jr-mr-row {
    flex-direction: column;
    align-items: stretch;
  }
  .jr-mr-media {
    width: 100%;
    height: 10rem;
  }
  .jr-mr-row__body {
    flex-direction: column;
    align-items: stretch;
  }
  .jr-mr-row__aside {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
  .jr-mr-dock {
    left: 0;
  }
}
.jr-mr-field__pager {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin: 1rem 0 0;
  padding-bottom: 4.5rem;
}
.jr-mr-dock {
  position: fixed;
  z-index: 20;
  right: 0;
  bottom: 0;
  left: var(--jr-sidebar-rail, 3.25rem);
  display: flex;
  justify-content: flex-end;
  padding: 0.75rem 1.25rem calc(0.75rem + env(safe-area-inset-bottom));
  background: var(--color-jr-surface, #fff);
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
  box-shadow: 0 -8px 24px rgba(15, 23, 42, 0.08);
}
.jr-mr-float {
  border: 0;
  border-radius: var(--radius-jr-control);
  background: var(--color-jr-primary, #2563eb);
  color: #fff;
  font-weight: 600;
  padding: 0.85rem 1.1rem;
  cursor: pointer;
}
.jr-mr-float:focus-visible {
  outline: 2px solid var(--color-jr-primary-950, #172554);
  outline-offset: 2px;
}
.jr-mr-summary__meta {
  margin: 0 0 1rem;
}
.jr-mr-summary__table {
  width: 100%;
  margin-bottom: 1rem;
  border-collapse: collapse;
}
.jr-mr-summary__table th,
.jr-mr-summary__table td {
  text-align: left;
  padding: 0.4rem 0;
  border-bottom: 1px solid var(--color-jr-border, #e5e7eb);
  vertical-align: middle;
}
.jr-mr-summary__qty {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.jr-mr-summary__qty button {
  width: 2.25rem;
  height: 2.25rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  background: #fff;
  cursor: pointer;
}
.jr-mr-summary__qty input {
  width: 4.5rem;
  height: 2.25rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  text-align: center;
}
.jr-mr-summary__error {
  color: var(--color-jr-danger, #dc2626);
}
</style>
