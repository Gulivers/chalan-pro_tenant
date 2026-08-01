<template>
  <div class="assistant-entity-link text-start">
    <a
      v-if="canNavigate"
      class="btn btn-link btn-sm p-0 text-decoration-none"
      :href="href"
      target="_blank"
      rel="noopener noreferrer"
      @click="onClick">
      {{ label }}
    </a>
    <span v-else class="text-muted small">{{ label }}</span>
  </div>
</template>

<script>
import { resolveEntityLinkLocation } from '../entityNavigation';

export default {
  name: 'EntityLinkBlock',
  props: {
    block: {
      type: Object,
      required: true,
    },
  },
  emits: ['navigate'],
  computed: {
    location() {
      return resolveEntityLinkLocation(this.block);
    },
    canNavigate() {
      return !!this.location;
    },
    href() {
      if (!this.location) return '#';
      try {
        return this.$router.resolve(this.location).href;
      } catch {
        return '#';
      }
    },
    label() {
      if (typeof this.block?.label === 'string' && this.block.label.trim()) {
        return this.block.label;
      }
      const type = this.block?.entity_type || 'entity';
      const id = this.block?.entity_id;
      return id != null ? `${type} #${id}` : String(type);
    },
  },
  methods: {
    onClick() {
      // Browser opens a new tab via target="_blank"; notify parent for analytics/UX.
      if (this.location) {
        this.$emit('navigate', this.location);
      }
    },
  },
};
</script>
