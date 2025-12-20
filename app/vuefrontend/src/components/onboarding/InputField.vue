<template>
  <div class="form-floating mb-3">
    <input
      :id="id"
      :type="type"
      :class="['form-control', { 'is-invalid': error, 'has-value': hasValue }]"
      :placeholder="placeholder || ' '"
      :value="modelValue"
      :required="required"
      :maxlength="maxlength"
      :disabled="disabled"
      @input="$emit('update:modelValue', $event.target.value)"
      @blur="$emit('blur')"
      @focus="$emit('focus')"
      :aria-label="ariaLabel || label"
      :aria-describedby="error ? `${id}-error` : undefined"
    />
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
import { computed } from 'vue'

const props = defineProps({
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
  type: {
    type: String,
    default: 'text'
  },
  placeholder: {
    type: String,
    default: ''
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
  maxlength: {
    type: Number,
    default: null
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

const hasValue = computed(() => {
  return props.modelValue !== null && props.modelValue !== undefined && props.modelValue !== ''
})

defineEmits(['update:modelValue', 'blur', 'focus'])
</script>

<style scoped>
.form-floating {
  position: relative;
}

.form-floating > label {
  padding: 0.75rem 1rem;
  font-weight: 500;
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  pointer-events: none;
  border: 1px solid transparent;
  transform-origin: 0 0;
  transition: opacity 0.1s ease-in-out, transform 0.1s ease-in-out;
}

.form-control {
  padding: 0.75rem 1rem;
  min-height: calc(3.5rem + 2px);
  line-height: 1.5;
}

/* Cuando el input está vacío, la label está dentro */
.form-control:not(:focus):not(.has-value):placeholder-shown {
  padding-top: 0.75rem;
  padding-bottom: 0.75rem;
}

/* Cuando el input tiene valor o está en focus, mover la label arriba y dar más espacio al texto */
.form-control:focus,
.form-control.has-value,
.form-control:not(:placeholder-shown) {
  padding-top: 2rem !important;
  padding-bottom: 0.75rem !important;
}

.form-control:focus ~ label,
.form-control.has-value ~ label,
.form-control:not(:placeholder-shown) ~ label {
  opacity: 0.65;
  transform: scale(0.85) translateY(-0.25rem) translateX(0.15rem);
  padding-top: 0.5rem;
}

.form-control:focus {
  border-color: var(--bs-primary);
  box-shadow: 0 0 0 0.2rem rgba(var(--bs-primary-rgb), 0.25);
}
</style>

