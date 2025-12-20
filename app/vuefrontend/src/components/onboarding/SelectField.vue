<template>
  <div class="form-floating mb-3">
    <select
      :id="id"
      :class="['form-select', { 'is-invalid': error }]"
      :value="modelValue"
      :required="required"
      :disabled="disabled"
      @change="$emit('update:modelValue', $event.target.value)"
      @blur="$emit('blur')"
      :aria-label="ariaLabel || label"
      :aria-describedby="error ? `${id}-error` : undefined"
    >
      <option value="" disabled>{{ placeholder || 'Select an option' }}</option>
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>
    <label :for="id">
      {{ label }}
      <span v-if="required" class="text-danger">*</span>
    </label>
    <div v-if="error" :id="`${id}-error`" class="invalid-feedback d-block mt-1">
      {{ error }}
    </div>
    <div v-if="hint && !error" class="form-text text-muted small mt-1">
      {{ hint }}
    </div>
  </div>
</template>

<script setup>
defineProps({
  id: {
    type: String,
    required: true
  },
  label: {
    type: String,
    required: true
  },
  modelValue: {
    type: [String, Number],
    default: ''
  },
  options: {
    type: Array,
    required: true,
    validator: (options) => {
      return options.every(opt => opt.value !== undefined && opt.label !== undefined)
    }
  },
  placeholder: {
    type: String,
    default: 'Select an option'
  },
  error: {
    type: String,
    default: ''
  },
  hint: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  ariaLabel: {
    type: String,
    default: ''
  }
})

defineEmits(['update:modelValue', 'blur'])
</script>

<style scoped>
.form-floating > label {
  padding: 0.75rem 1rem;
  font-weight: 500;
  z-index: 1;
}

.form-select {
  position: relative;
  z-index: 2;
}

.form-select:focus {
  border-color: var(--bs-primary);
  box-shadow: 0 0 0 0.2rem rgba(var(--bs-primary-rgb), 0.25);
  z-index: 3;
}
</style>

