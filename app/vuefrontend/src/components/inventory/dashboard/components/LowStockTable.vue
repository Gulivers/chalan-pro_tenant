<template>
  <div class="low-stock-table">
    <div v-if="loading" class="jr-dash-state" aria-live="polite">Loading…</div>

    <JREmptyState
      v-else-if="!products.length"
      title="No stock attention needed"
      description="No products are below reorder level right now."
    />

    <template v-else>
      <!-- Phone: scan list -->
      <ul v-if="isMobile" class="jr-stock-rows" :aria-busy="loading ? 'true' : 'false'">
        <li
          v-for="product in products"
          :key="product.id"
          class="jr-stock-row"
          :class="rowToneClass(product)">
          <div class="jr-stock-row__main">
            <p class="jr-stock-row__name">{{ product.name }}</p>
            <p class="jr-stock-row__meta">
              <span>{{ product.sku }}</span>
              <span v-if="product.category?.name" aria-hidden="true"> · </span>
              <span v-if="product.category?.name">{{ product.category.name }}</span>
            </p>
            <p class="jr-stock-row__nums">
              On hand
              <strong :class="stockTextClass(product)">{{ formatNumber(stockQty(product)) }}</strong>
              <span class="jr-dash-muted"> · Reorder {{ formatNumber(reorderLevel(product)) }}</span>
            </p>
          </div>
          <div class="jr-stock-row__aside">
            <JRBadge
              :value="statusLabel(product)"
              :severity="statusSeverity(product)" />
            <div class="jr-stock-row__actions">
              <JRButton
                v-if="canView"
                type="button"
                variant="ghost"
                size="sm"
                @click="viewProduct(product)">
                View
              </JRButton>
              <JRButton
                v-if="canEdit"
                type="button"
                variant="ghost"
                size="sm"
                @click="editProduct(product)">
                Edit
              </JRButton>
            </div>
          </div>
        </li>
      </ul>

      <!-- Tablet / desktop table -->
      <div v-else class="jr-dash-table-wrap">
        <table class="jr-dash-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>SKU</th>
              <th class="jr-col-num">On hand</th>
              <th class="jr-col-num">Reorder</th>
              <th>Status</th>
              <th class="jr-col-actions">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="product in products"
              :key="product.id"
              :class="rowToneClass(product)">
              <td>
                <strong>{{ product.name }}</strong>
                <br />
                <span class="jr-dash-muted">{{ product.category?.name || '—' }}</span>
              </td>
              <td><span class="jr-sku">{{ product.sku }}</span></td>
              <td class="jr-col-num">
                <span :class="stockTextClass(product)">
                  {{ formatNumber(stockQty(product)) }}
                </span>
              </td>
              <td class="jr-col-num jr-dash-muted">
                {{ formatNumber(reorderLevel(product)) }}
              </td>
              <td>
                <JRBadge
                  :value="statusLabel(product)"
                  :severity="statusSeverity(product)" />
              </td>
              <td class="jr-col-actions">
                <div class="jr-dash-actions">
                  <JRButton
                    v-if="canView"
                    type="button"
                    variant="secondary"
                    size="sm"
                    @click="viewProduct(product)">
                    View
                  </JRButton>
                  <JRButton
                    v-if="canEdit"
                    type="button"
                    variant="ghost"
                    size="sm"
                    @click="editProduct(product)">
                    Edit
                  </JRButton>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script>
import { JRButton, JRBadge, JREmptyState } from '@ui';
import {
  getStockQty,
  getReorderLevel,
  getStockStatus,
  stockStatusLabel,
  stockStatusSeverity,
} from './stockStatus';

const PHONE_MQ = '(max-width: 767.98px)';

export default {
  name: 'LowStockTable',
  components: {
    JRButton,
    JRBadge,
    JREmptyState,
  },
  props: {
    products: {
      type: Array,
      default: () => [],
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isMobile: false,
      phoneQuery: null,
    };
  },
  computed: {
    canView() {
      return !!this.hasPermission?.('appinventory.view_product');
    },
    canEdit() {
      return !!this.hasPermission?.('appinventory.change_product');
    },
  },
  mounted() {
    if (typeof window !== 'undefined' && window.matchMedia) {
      this.phoneQuery = window.matchMedia(PHONE_MQ);
      this.onViewport = () => {
        this.isMobile = this.phoneQuery.matches;
      };
      this.onViewport();
      if (this.phoneQuery.addEventListener) {
        this.phoneQuery.addEventListener('change', this.onViewport);
      } else {
        this.phoneQuery.addListener(this.onViewport);
      }
    }
  },
  beforeUnmount() {
    if (!this.phoneQuery || !this.onViewport) return;
    if (this.phoneQuery.removeEventListener) {
      this.phoneQuery.removeEventListener('change', this.onViewport);
    } else {
      this.phoneQuery.removeListener?.(this.onViewport);
    }
  },
  methods: {
    stockQty: getStockQty,
    reorderLevel: getReorderLevel,

    formatNumber(value) {
      const n = Number(value);
      if (!Number.isFinite(n)) return '0';
      return new Intl.NumberFormat('en-US', {
        maximumFractionDigits: 2,
        minimumFractionDigits: 0,
      }).format(n);
    },

    statusOf(product) {
      return getStockStatus(product);
    },

    statusLabel(product) {
      return stockStatusLabel(this.statusOf(product));
    },

    statusSeverity(product) {
      return stockStatusSeverity(this.statusOf(product));
    },

    rowToneClass(product) {
      const status = this.statusOf(product);
      if (status === 'critical' || status === 'out') return 'is-danger';
      if (status === 'low') return 'is-warning';
      return '';
    },

    stockTextClass(product) {
      const status = this.statusOf(product);
      if (status === 'critical' || status === 'out') return 'is-danger-text';
      if (status === 'low') return 'is-warning-text';
      return 'is-success-text';
    },

    viewProduct(product) {
      this.$router.push({
        name: 'product-form',
        query: { mode: 'view', id: product.id },
      });
    },

    editProduct(product) {
      this.$router.push({
        name: 'product-form',
        query: { mode: 'edit', id: product.id },
      });
    },
  },
};
</script>

<style scoped>
.low-stock-table {
  min-height: 0;
}

.jr-dash-state {
  padding: 0.75rem 0;
  font-size: 0.875rem;
  color: var(--color-jr-muted);
}

.jr-dash-muted {
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}

.jr-dash-table-wrap {
  max-height: 28rem;
  overflow: auto;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
}

.jr-dash-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
  margin: 0;
}

.jr-dash-table th,
.jr-dash-table td {
  padding: 0.55rem 0.75rem;
  border-bottom: 1px solid var(--color-jr-border);
  text-align: left;
  vertical-align: middle;
}

.jr-dash-table thead th {
  position: sticky;
  top: 0;
  z-index: 1;
  background: var(--color-jr-surface-muted);
  font-weight: 600;
  color: var(--color-jr-text);
}

.jr-dash-table tbody tr.is-danger {
  background: var(--color-jr-danger-subtle);
}

.jr-dash-table tbody tr.is-warning {
  background: var(--color-jr-warning-subtle);
}

.jr-col-num {
  text-align: right;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}

.jr-col-actions {
  text-align: center;
  white-space: nowrap;
}

.is-danger-text {
  color: var(--color-jr-danger-text);
  font-weight: 600;
}

.is-warning-text {
  color: var(--color-jr-warning-text);
  font-weight: 600;
}

.is-success-text {
  color: var(--color-jr-success-text);
  font-weight: 600;
}

.jr-dash-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  justify-content: center;
}

.jr-stock-rows {
  list-style: none;
  margin: 0;
  padding: 0;
  border-top: 1px solid var(--color-jr-border);
}

.jr-stock-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.65rem 0;
  border-bottom: 1px solid var(--color-jr-border);
}

.jr-stock-row.is-danger {
  background: var(--color-jr-danger-subtle);
  margin: 0 -0.25rem;
  padding-left: 0.25rem;
  padding-right: 0.25rem;
}

.jr-stock-row.is-warning {
  background: var(--color-jr-warning-subtle);
  margin: 0 -0.25rem;
  padding-left: 0.25rem;
  padding-right: 0.25rem;
}

.jr-stock-row__main {
  min-width: 0;
  flex: 1 1 auto;
}

.jr-stock-row__name {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-jr-text);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.jr-stock-row__meta,
.jr-stock-row__nums {
  margin: 0.2rem 0 0;
  font-size: 0.75rem;
  color: var(--color-jr-muted);
}

.jr-stock-row__aside {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.35rem;
  flex-shrink: 0;
}

.jr-stock-row__actions {
  display: flex;
  gap: 0.25rem;
}

.jr-sku {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-jr-text);
  letter-spacing: 0.02em;
}
</style>
