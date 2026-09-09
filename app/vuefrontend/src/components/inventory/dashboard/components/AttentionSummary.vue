<template>
  <div
    class="jr-attention"
    :class="{ 'is-clear': !hasAttention }"
    :aria-busy="loading ? 'true' : 'false'"
    aria-live="polite">
    <div class="jr-attention__lead">
      <p class="jr-attention__kicker">Today</p>
      <p class="jr-attention__title">
        {{ headline }}
      </p>
      <p class="jr-attention__sub">{{ subcopy }}</p>
    </div>

    <ul class="jr-attention__counts" aria-label="Stock attention counts">
      <li v-if="counts.critical > 0">
        <JRBadge :value="`${counts.critical} Critical`" severity="danger" />
      </li>
      <li v-if="counts.out > 0">
        <JRBadge :value="`${counts.out} Out of stock`" severity="danger" />
      </li>
      <li v-if="counts.low > 0">
        <JRBadge :value="`${counts.low} Low stock`" severity="warn" />
      </li>
      <li v-if="!hasAttention && !loading">
        <JRBadge value="All clear" severity="success" />
      </li>
    </ul>
  </div>
</template>

<script>
import { JRBadge } from '@ui';
import { summarizeStockAttention } from './stockStatus';

export default {
  name: 'AttentionSummary',
  components: { JRBadge },
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
  computed: {
    counts() {
      return summarizeStockAttention(this.products);
    },
    attentionTotal() {
      return this.counts.critical + this.counts.out + this.counts.low;
    },
    hasAttention() {
      return this.attentionTotal > 0;
    },
    headline() {
      if (this.loading) return 'Checking inventory…';
      if (!this.hasAttention) return 'No stock exceptions right now';
      if (this.counts.critical > 0) {
        return `${this.counts.critical} product${this.counts.critical === 1 ? '' : 's'} with negative stock`;
      }
      if (this.counts.out > 0) {
        return `${this.counts.out} product${this.counts.out === 1 ? '' : 's'} out of stock`;
      }
      return `${this.counts.low} product${this.counts.low === 1 ? '' : 's'} below reorder`;
    },
    subcopy() {
      if (this.loading) return 'Loading low-stock signals.';
      if (!this.hasAttention) {
        return 'Critical, out-of-stock, and below-reorder items will appear here.';
      }
      return `${this.attentionTotal} item${this.attentionTotal === 1 ? '' : 's'} need review below.`;
    },
  },
};
</script>

<style scoped>
.jr-attention {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.85rem 1.25rem;
  margin-bottom: 1.25rem;
  padding: 0.95rem 1.1rem;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel);
  background: var(--color-jr-danger-subtle);
}

.jr-attention.is-clear {
  background: var(--color-jr-success-subtle);
}

.jr-attention__kicker {
  margin: 0 0 0.2rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-jr-muted);
}

.jr-attention__title {
  margin: 0;
  font-size: 1.3125rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-jr-text);
}

.jr-attention__sub {
  margin: 0.25rem 0 0;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-attention__counts {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  list-style: none;
  margin: 0;
  padding: 0;
}

@media (max-width: 575.98px) {
  .jr-attention {
    padding: 0.85rem 0.9rem;
  }
}
</style>
