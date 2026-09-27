<template>
  <div v-if="visible" class="active-filters" role="region" aria-label="Active parameters">
    <div class="active-filters__header">
      <span class="active-filters__title">Parameters</span>
      <button
        v-if="showClearAll"
        type="button"
        class="active-filters__clear"
        :disabled="disabled"
        @click="$emit('clear-all')">
        Clear
      </button>
    </div>
    <div class="active-filters__chips">
      <span
        v-for="(chip, index) in chips"
        :key="chipKey(chip, index)"
        class="filter-chip"
        :class="{
          'filter-chip--fixed': !isRemovable(chip),
          'filter-chip--removable': isRemovable(chip),
        }">
        <span class="filter-chip__label">{{ chip.label }}</span>
        <button
          v-if="isRemovable(chip)"
          type="button"
          class="filter-chip__remove"
          :disabled="disabled"
          :aria-label="`Remove ${chip.label}`"
          @click="$emit('remove', chip)">
          ×
        </button>
      </span>
    </div>
  </div>
</template>

<script>
const REMOVABLE_KEYS = new Set(['vendor', 'min_amount', 'comparison_period']);

export default {
  name: 'ActiveFilterChips',
  props: {
    activeFilters: {
      type: Object,
      default: null,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['remove', 'clear-all'],
  computed: {
    chips() {
      const list = this.activeFilters?.chips;
      return Array.isArray(list) ? list : [];
    },
    visible() {
      return this.chips.length > 0 && !!this.activeFilters?.inherited;
    },
    showClearAll() {
      return this.chips.some(
        (chip) => this.isRemovable(chip) || chip.key === 'period' || chip.key === 'tool',
      );
    },
  },
  methods: {
    isRemovable(chip) {
      if (!chip || typeof chip !== 'object') return false;
      if (typeof chip.removable === 'boolean') return chip.removable;
      return REMOVABLE_KEYS.has(chip.key);
    },
    chipKey(chip, index) {
      const value = chip?.value;
      const valuePart =
        value && typeof value === 'object'
          ? JSON.stringify(value)
          : String(value ?? '');
      return `${chip?.key || 'chip'}-${valuePart}-${index}`;
    },
  },
};
</script>

<style scoped>
.active-filters {
  border-top: 1px solid var(--color-jr-border);
  padding: 0.55rem 0.75rem 0.45rem;
  background: var(--color-jr-surface-muted);
  text-align: left;
}

.active-filters__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.35rem;
}

.active-filters__title {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
  color: var(--color-jr-muted);
}

.active-filters__clear {
  border: none;
  background: transparent;
  color: var(--color-jr-primary);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0;
  cursor: pointer;
}

.active-filters__clear:hover:not(:disabled) {
  text-decoration: underline;
}

.active-filters__clear:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.active-filters__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.2rem;
  max-width: 100%;
  border: 1px solid var(--color-jr-border);
  background: var(--color-jr-surface);
  color: var(--color-jr-text);
  border-radius: var(--radius-jr-control);
  padding: 0.2rem 0.55rem;
  font-size: 0.75rem;
  line-height: 1.3;
}

.filter-chip--fixed {
  background: var(--color-jr-surface-muted);
  border-color: transparent;
  color: var(--color-jr-muted);
}

.filter-chip--removable {
  padding-right: 0.25rem;
}

.filter-chip__label {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 14rem;
}

.filter-chip__remove {
  border: none;
  background: transparent;
  color: var(--color-jr-muted);
  font-size: 0.9375rem;
  line-height: 1;
  width: 1.15rem;
  height: 1.15rem;
  border-radius: var(--radius-jr-control);
  padding: 0;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.filter-chip__remove:hover:not(:disabled) {
  background: var(--color-jr-page);
  color: var(--color-jr-text);
}

.filter-chip__remove:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
