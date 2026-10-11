<template>
  <DatePicker
    class="jr-control"
    :modelValue="modelValue"
    :disabled="disabled"
    :invalid="invalid"
    :placeholder="placeholder"
    :inputId="inputId"
    :dateFormat="dateFormat"
    :showIcon="showIcon"
    :showButtonBar="showButtonBar"
    :manualInput="manualInput"
    fluid
    @update:modelValue="$emit('update:modelValue', $event)"
  />
</template>

<script>
import DatePicker from 'primevue/datepicker';

export default {
  name: 'JRDatePicker',
  components: { DatePicker },
  props: {
    modelValue: {
      default: null,
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
    dateFormat: {
      type: String,
      default: 'yy-mm-dd',
    },
    showIcon: {
      type: Boolean,
      default: true,
    },
    showButtonBar: {
      type: Boolean,
      default: false,
    },
    manualInput: {
      type: Boolean,
      default: true,
    },
  },
  emits: ['update:modelValue'],
};
</script>
