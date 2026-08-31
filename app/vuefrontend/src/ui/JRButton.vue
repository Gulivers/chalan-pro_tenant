<template>
  <Button
    class="jr-button"
    :type="type"
    :severity="primeSeverity"
    :text="variant === 'ghost'"
    :outlined="variant === 'secondary'"
    :size="primeSize"
    :disabled="disabled"
    :fluid="fluid"
    v-bind="$attrs"
  >
    <slot />
  </Button>
</template>

<script>
import Button from 'primevue/button';

const SEVERITY = {
  primary: null,
  secondary: 'secondary',
  danger: 'danger',
  ghost: 'secondary',
};

export default {
  name: 'JRButton',
  components: { Button },
  inheritAttrs: false,
  props: {
    variant: {
      type: String,
      default: 'primary',
      validator: (value) => ['primary', 'secondary', 'danger', 'ghost'].includes(value),
    },
    size: {
      type: String,
      default: 'md',
      validator: (value) => ['sm', 'md'].includes(value),
    },
    type: {
      type: String,
      default: 'button',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    fluid: {
      type: Boolean,
      default: false,
    },
  },
  computed: {
    primeSeverity() {
      return SEVERITY[this.variant];
    },
    primeSize() {
      return this.size === 'sm' ? 'small' : null;
    },
  },
};
</script>
