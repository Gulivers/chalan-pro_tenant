<template>
  <div class="assistant-text-block">
    <div v-if="block.title" class="assistant-block-title text-muted small mb-1">
      {{ block.title }}
    </div>
    <p class="mb-0 assistant-text-body">{{ displayText }}</p>
  </div>
</template>

<script>
export default {
  name: 'TextBlock',
  props: {
    block: {
      type: Object,
      required: true,
    },
  },
  computed: {
    displayText() {
      const text = this.block?.text;
      return typeof text === 'string' ? text : '';
    },
  },
};
</script>

<style scoped>
.assistant-text-body {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.925rem;
  line-height: 1.45;
  text-align: left;
}
.assistant-block-title {
  text-align: left;
  font-weight: 600;
}
</style>
