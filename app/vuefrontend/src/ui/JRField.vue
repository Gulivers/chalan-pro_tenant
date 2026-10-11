<template>
  <div class="jr-field">
    <div v-if="label || $slots.help" class="jr-field__heading">
      <label v-if="label" class="jr-field__label" :for="resolvedInputId">
        <span class="jr-field__label-text">
          {{ label }}
          <span v-if="required" class="jr-field__required" aria-hidden="true">*</span>
        </span>
      </label>
      <slot name="help" />
    </div>
    <slot :errorId="errorId" :hintId="hintId" :invalid="!!error" :describedby="describedby" />
    <p v-if="hint" class="jr-field__hint" :id="hintId">{{ hint }}</p>
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
    hintId() {
      return `${this.resolvedInputId}-hint`;
    },
    describedby() {
      return [this.hint ? this.hintId : '', this.error ? this.errorId : '']
        .filter(Boolean)
        .join(' ');
    },
  },
};
</script>
