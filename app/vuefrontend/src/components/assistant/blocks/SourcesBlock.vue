<template>
  <div v-if="normalizedSources.length" class="assistant-sources-block">
    <ul class="list-unstyled mb-0">
      <li
        v-for="(source, index) in normalizedSources"
        :key="source.key || index"
        class="small text-muted text-start">
        {{ source.display }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'SourcesBlock',
  props: {
    /** Single source block or array of root-level sources */
    block: {
      type: Object,
      default: null,
    },
    sources: {
      type: Array,
      default: null,
    },
  },
  computed: {
    normalizedSources() {
      if (Array.isArray(this.sources)) {
        return this.sources.map((s, i) => this.normalize(s, i)).filter(Boolean);
      }
      if (this.block && typeof this.block === 'object') {
        if (Array.isArray(this.block.items)) {
          return this.block.items.map((s, i) => this.normalize(s, i)).filter(Boolean);
        }
        const one = this.normalize(this.block, 0);
        return one ? [one] : [];
      }
      return [];
    },
  },
  methods: {
    normalize(source, index) {
      if (!source || typeof source !== 'object') return null;

      const rowCount =
        typeof source.row_count === 'number'
          ? source.row_count
          : typeof source.rowCount === 'number'
            ? source.rowCount
            : null;

      // Prefer operational label from backend: "Source: 3 purchase invoices"
      let display = null;
      if (typeof source.display === 'string' && source.display.trim()) {
        display = source.display.trim();
      } else if (typeof source.label === 'string' && source.label.trim()) {
        const label = source.label.trim();
        display = label.toLowerCase().startsWith('source:')
          ? label
          : `Source: ${label}`;
      } else if (rowCount != null) {
        const unit = rowCount === 1 ? 'purchase invoice' : 'purchase invoices';
        display = `Source: ${rowCount} ${unit}`;
      } else {
        return null;
      }

      return {
        key: source.id || `src-${index}`,
        display,
      };
    },
  },
};
</script>

<style scoped>
.assistant-sources-block {
  text-align: left;
  padding-top: 0.25rem;
  border-top: 1px dashed rgba(0, 0, 0, 0.08);
  margin-top: 0.35rem;
}
</style>
