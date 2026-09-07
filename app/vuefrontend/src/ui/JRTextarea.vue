<template>
  <Textarea
    class="jr-control"
    :modelValue="modelValue"
    :disabled="disabled"
    :invalid="invalid"
    :placeholder="placeholder"
    :id="inputId"
    :rows="rows"
    :autoResize="autoResize"
    :aria-describedby="ariaDescribedby || undefined"
    :aria-invalid="invalid ? 'true' : undefined"
    :aria-required="required ? 'true' : undefined"
    fluid
    @update:modelValue="$emit('update:modelValue', $event)"
  />
</template>

<script>
import Textarea from 'primevue/textarea';

export default {
  name: 'JRTextarea',
  components: { Textarea },
  props: {
    modelValue: {
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
    placeholder: {
      type: String,
      default: '',
    },
    inputId: {
      type: String,
      default: undefined,
    },
    rows: {
      type: Number,
      default: 3,
    },
    autoResize: {
      type: Boolean,
      default: true,
    },
    ariaDescribedby: {
      type: String,
      default: '',
    },
    required: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['update:modelValue'],
};
</script>
