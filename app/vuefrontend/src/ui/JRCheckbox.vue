<template>
  <label class="jr-checkbox">
    <Checkbox
      :modelValue="modelValue"
      :inputId="inputId"
      :disabled="disabled"
      :invalid="invalid"
      :aria-label="ariaLabel"
      binary
      @update:modelValue="$emit('update:modelValue', $event)"
    />
    <span v-if="label || $slots.default" class="jr-checkbox__label">
      <slot>{{ label }}</slot>
    </span>
  </label>
</template>

<script>
import Checkbox from 'primevue/checkbox';

export default {
  name: 'JRCheckbox',
  components: { Checkbox },
  props: {
    modelValue: {
      type: [Boolean, Array],
      default: false,
    },
    label: {
      type: String,
      default: '',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    invalid: {
      type: Boolean,
      default: false,
    },
    inputId: {
      type: String,
      default: undefined,
    },
    ariaLabel: {
      type: String,
      default: '',
    },
  },
  emits: ['update:modelValue'],
};
</script>
