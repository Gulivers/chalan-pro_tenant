<template>
  <div class="jr-select-addon">
    <JRSelect
      class="jr-select-addon__select"
      :modelValue="modelValue"
      :options="options"
      :optionLabel="optionLabel"
      :optionValue="optionValue"
      :multiple="multiple"
      :filter="filter"
      :disabled="disabled"
      :invalid="invalid"
      :placeholder="placeholder"
      :showClear="showClear"
      :inputId="inputId"
      :ariaDescribedby="ariaDescribedby"
      :required="required"
      @update:modelValue="$emit('update:modelValue', $event)"
      @show="$emit('show')"
    />
    <div v-if="showAdd || showEdit" class="jr-select-addon__actions">
      <button
        v-if="showAdd"
        type="button"
        class="jr-icon-btn"
        :disabled="addDisabled"
        :aria-label="addLabel"
        @click="$emit('add')"
      >
        <slot name="add-icon">
          <svg width="20" height="20" viewBox="0 0 16 16" aria-hidden="true" fill="currentColor">
            <path d="M8 3a.75.75 0 0 1 .75.75v3.5h3.5a.75.75 0 0 1 0 1.5h-3.5v3.5a.75.75 0 0 1-1.5 0v-3.5h-3.5a.75.75 0 0 1 0-1.5h3.5v-3.5A.75.75 0 0 1 8 3Z" />
          </svg>
        </slot>
      </button>
      <button
        v-if="showEdit"
        type="button"
        class="jr-icon-btn"
        :disabled="editDisabled || !hasValue"
        :aria-label="editLabel"
        @click="$emit('edit')"
      >
        <slot name="edit-icon">
          <svg width="20" height="20" viewBox="0 0 16 16" aria-hidden="true" fill="currentColor">
            <path d="M11.013 2.513a1.75 1.75 0 0 1 2.475 2.474L6.28 12.196a2 2 0 0 1-.854.51l-2.37.692a.5.5 0 0 1-.62-.62l.692-2.37a2 2 0 0 1 .51-.854l7.375-7.441Z" />
          </svg>
        </slot>
      </button>
    </div>
  </div>
</template>

<script>
import JRSelect from './JRSelect.vue';

export default {
  name: 'JRSelectAddon',
  components: { JRSelect },
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
    showAdd: {
      type: Boolean,
      default: false,
    },
    showEdit: {
      type: Boolean,
      default: false,
    },
    addDisabled: {
      type: Boolean,
      default: false,
    },
    editDisabled: {
      type: Boolean,
      default: false,
    },
    addLabel: {
      type: String,
      default: 'Add',
    },
    editLabel: {
      type: String,
      default: 'Edit',
    },
    inputId: {
      type: String,
      default: undefined,
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
  emits: ['update:modelValue', 'show', 'add', 'edit'],
  computed: {
    hasValue() {
      if (Array.isArray(this.modelValue)) {
        return this.modelValue.length > 0;
      }
      return this.modelValue !== null && this.modelValue !== undefined && this.modelValue !== '';
    },
  },
};
</script>
