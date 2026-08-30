<template>
  <InputNumber
    v-if="type === 'number'"
    class="jr-control"
    :modelValue="modelValue"
    :disabled="disabled"
    :invalid="invalid"
    :placeholder="placeholder"
    :inputId="inputId"
    :min="min"
    :max="max"
    :minFractionDigits="minFractionDigits"
    :maxFractionDigits="maxFractionDigits"
    :useGrouping="false"
    fluid
    @update:modelValue="$emit('update:modelValue', $event)"
  />
  <InputText
    v-else
    class="jr-control"
    :type="type"
    :modelValue="modelValue"
    :disabled="disabled"
    :invalid="invalid"
    :placeholder="placeholder"
    :id="inputId"
    fluid
    @update:modelValue="$emit('update:modelValue', $event)"
  />
</template>

<script>
import InputNumber from 'primevue/inputnumber';
import InputText from 'primevue/inputtext';

export default {
  name: 'JRInput',
  components: { InputNumber, InputText },
  props: {
    modelValue: {
      type: [String, Number],
      default: null,
    },
    type: {
      type: String,
      default: 'text',
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
    min: {
      type: Number,
      default: undefined,
    },
    max: {
      type: Number,
      default: undefined,
    },
    minFractionDigits: {
      type: Number,
      default: undefined,
    },
    maxFractionDigits: {
      type: Number,
      default: undefined,
    },
  },
  emits: ['update:modelValue'],
};
</script>
