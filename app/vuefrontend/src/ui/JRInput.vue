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
    :inputProps="numberInputProps"
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
    v-bind="textInputAttrs"
    :aria-describedby="ariaDescribedby || undefined"
    :aria-invalid="invalid ? 'true' : undefined"
    :aria-required="required ? 'true' : undefined"
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
    ariaDescribedby: {
      type: String,
      default: '',
    },
    required: {
      type: Boolean,
      default: false,
    },
    autocomplete: {
      type: String,
      default: undefined,
    },
    spellcheck: {
      type: [Boolean, String],
      default: undefined,
    },
    autocapitalize: {
      type: String,
      default: undefined,
    },
    enterkeyhint: {
      type: String,
      default: undefined,
    },
    autocorrect: {
      type: String,
      default: undefined,
    },
    inputmode: {
      type: String,
      default: undefined,
    },
  },
  emits: ['update:modelValue'],
  computed: {
    textInputAttrs() {
      const attrs = {};
      if (this.autocomplete) attrs.autocomplete = this.autocomplete;
      if (this.spellcheck !== undefined) attrs.spellcheck = this.spellcheck;
      if (this.autocapitalize) attrs.autocapitalize = this.autocapitalize;
      if (this.enterkeyhint) attrs.enterkeyhint = this.enterkeyhint;
      if (this.autocorrect) attrs.autocorrect = this.autocorrect;
      if (this.inputmode) attrs.inputmode = this.inputmode;
      return attrs;
    },
    numberInputProps() {
      const props = {};
      if (this.ariaDescribedby) props['aria-describedby'] = this.ariaDescribedby;
      if (this.invalid) props['aria-invalid'] = 'true';
      if (this.required) props['aria-required'] = 'true';
      return Object.keys(props).length ? props : undefined;
    },
  },
};
</script>
