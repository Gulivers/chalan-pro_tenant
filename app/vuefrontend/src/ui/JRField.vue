<template>
  <div class="jr-field">
    <label v-if="label" class="jr-field__label" :for="resolvedInputId">
      {{ label }}
      <span v-if="required" class="jr-field__required" aria-hidden="true">*</span>
    </label>
    <p v-if="hint" class="jr-field__hint">{{ hint }}</p>
    <slot />
    <p v-if="error" class="jr-field__error" :id="errorId" role="alert">
      {{ error }}
    </p>
  </div>
</template>

<script>
let fieldSeq = 0;

export default {
  name: 'JRField',
  props: {
    label: {
      type: String,
      default: '',
    },
    hint: {
      type: String,
      default: '',
    },
    error: {
      type: String,
      default: '',
    },
    required: {
      type: Boolean,
      default: false,
    },
    inputId: {
      type: String,
      default: '',
    },
  },
  data() {
    return {
      uid: `jr-field-${++fieldSeq}`,
    };
  },
  computed: {
    resolvedInputId() {
      return this.inputId || this.uid;
    },
    errorId() {
      return `${this.resolvedInputId}-error`;
    },
  },
};
</script>
