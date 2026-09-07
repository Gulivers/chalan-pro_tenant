<template>
  <button
    v-if="text"
    type="button"
    class="jr-tooltip-trigger"
    :aria-label="ariaLabel"
    v-tooltip.top="tooltipBinding">
    <svg
      width="16"
      height="16"
      viewBox="0 0 16 16"
      aria-hidden="true"
      fill="none"
      stroke="currentColor"
      stroke-width="1.6"
      stroke-linecap="round"
      stroke-linejoin="round">
      <circle cx="8" cy="8" r="6.2" />
      <path d="M8 7.2V11" />
      <circle cx="8" cy="5.1" r="0.7" fill="currentColor" stroke="none" />
    </svg>
  </button>
</template>

<script>
import Tooltip from 'primevue/tooltip';

export default {
  name: 'JRTooltip',
  directives: {
    tooltip: Tooltip,
  },
  props: {
    text: {
      type: String,
      default: '',
    },
    ariaLabel: {
      type: String,
      default: 'More information',
    },
    showDelay: {
      type: Number,
      default: 150,
    },
  },
  computed: {
    tooltipBinding() {
      return {
        value: this.text,
        showDelay: this.showDelay,
        escape: true,
        class: 'jr-tooltip',
      };
    },
  },
};
</script>
