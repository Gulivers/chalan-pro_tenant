<template>
  <MultiSelect
    v-if="multiple"
    class="jr-control"
    :modelValue="modelValue"
    :options="options"
    :optionLabel="optionLabel"
    :optionValue="optionValue"
    :placeholder="placeholder"
    :disabled="disabled"
    :invalid="invalid"
    :filter="filter"
    :showClear="showClear"
    :inputId="inputId"
    display="chip"
    fluid
    @update:modelValue="$emit('update:modelValue', $event)"
    @show="$emit('show')"
  />
  <Select
    v-else
    class="jr-control"
    :modelValue="modelValue"
    :options="options"
    :optionLabel="optionLabel"
    :optionValue="optionValue"
    :placeholder="placeholder"
    :disabled="disabled"
    :invalid="invalid"
    :filter="filter"
    :showClear="showClear"
    :inputId="inputId"
    fluid
    @update:modelValue="$emit('update:modelValue', $event)"
    @show="$emit('show')"
  />
</template>

<script>
import MultiSelect from 'primevue/multiselect';
import Select from 'primevue/select';

export default {
  name: 'JRSelect',
  components: { MultiSelect, Select },
  props: {
    modelValue: {
      default: null,
    },
    options: {
      type: Array,
      default: () => [],
    },
    optionLabel: {
      type: String,
      default: 'label',
    },
    optionValue: {
      type: String,
      default: 'value',
    },
    multiple: {
      type: Boolean,
      default: false,
    },
    filter: {
      type: Boolean,
      default: false,
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
    showClear: {
      type: Boolean,
      default: false,
    },
    inputId: {
      type: String,
      default: undefined,
    },
  },
  emits: ['update:modelValue', 'show'],
};
</script>
