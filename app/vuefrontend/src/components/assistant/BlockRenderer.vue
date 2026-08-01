<template>
  <div class="assistant-block-renderer">
    <template v-for="(entry, index) in resolvedBlocks" :key="entry.key || index">
      <component
        v-if="entry.component"
        :is="entry.component"
        class="assistant-block-item mb-2"
        :block="entry.block"
        @navigate="onNavigate" />
      <div
        v-else-if="entry.devSkipped"
        class="small text-muted text-start mb-2"
        data-testid="unknown-block">
        Unsupported block type skipped.
      </div>
    </template>
    <div
      v-if="!resolvedBlocks.length && showEmpty"
      class="small text-muted text-start">
      No structured blocks in this response.
    </div>
  </div>
</template>

<script>
import { isValidBlockShape, resolveBlockComponent } from './blockRegistry';

export default {
  name: 'BlockRenderer',
  props: {
    blocks: {
      type: Array,
      default: () => [],
    },
    showEmpty: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['navigate'],
  computed: {
    isDev() {
      return process.env.NODE_ENV === 'development';
    },
    resolvedBlocks() {
      const list = Array.isArray(this.blocks) ? this.blocks : [];
      const out = [];

      list.forEach((block, index) => {
        if (!isValidBlockShape(block)) {
          if (this.isDev) {
            // eslint-disable-next-line no-console
            console.warn('[Assistant] Invalid block skipped at index', index);
          }
          return;
        }

        const component = resolveBlockComponent(block.type);
        if (!component) {
          if (this.isDev) {
            // eslint-disable-next-line no-console
            console.warn('[Assistant] Unknown block type skipped:', block.type);
            out.push({
              key: `skipped-${block.id || index}`,
              component: null,
              block,
              devSkipped: true,
            });
          }
          return;
        }

        out.push({
          key: block.id || `block-${index}`,
          component,
          block,
          devSkipped: false,
        });
      });

      return out;
    },
  },
  methods: {
    onNavigate(location) {
      this.$emit('navigate', location);
    },
  },
};
</script>

<style scoped>
.assistant-block-renderer {
  text-align: left;
}
</style>
