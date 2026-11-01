<template>
  <InputNumber
    v-if="type === 'number'"
    class="jr-control"
    :class="{ 'jr-control--stepper': showButtons }"
    :modelValue="modelValue"
    :disabled="disabled"
    :invalid="invalid"
    :placeholder="placeholder"
    :inputId="inputId"
    :min="min"
    :max="max"
    :mode="mode"
    :currency="currency"
    :locale="locale"
    :prefix="prefix"
    :suffix="suffix"
    :minFractionDigits="resolvedMinFractionDigits"
    :maxFractionDigits="resolvedMaxFractionDigits"
    :showButtons="showButtons"
    :buttonLayout="buttonLayout"
    :useGrouping="resolvedUseGrouping"
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
    /** PrimeVue InputNumber mode: decimal | currency */
    mode: {
      type: String,
      default: 'decimal',
    },
    currency: {
      type: String,
      default: 'USD',
    },
    locale: {
      type: String,
      default: 'en-US',
    },
    prefix: {
      type: String,
      default: undefined,
    },
    suffix: {
      type: String,
      default: undefined,
    },
    showButtons: {
      type: Boolean,
      default: false,
    },
    buttonLayout: {
      type: String,
      default: 'stacked',
    },
    minFractionDigits: {
      type: Number,
      default: undefined,
    },
    maxFractionDigits: {
      type: Number,
      default: undefined,
    },
    useGrouping: {
      type: Boolean,
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
    resolvedMinFractionDigits() {
      if (this.minFractionDigits !== undefined) return this.minFractionDigits;
      if (this.mode === 'currency') return 2;
      return undefined;
    },
    resolvedMaxFractionDigits() {
      if (this.maxFractionDigits !== undefined) return this.maxFractionDigits;
      if (this.mode === 'currency') return 2;
      return undefined;
    },
    resolvedUseGrouping() {
      if (this.useGrouping !== undefined) return this.useGrouping;
      // Currency typically shows grouping; plain decimal fields in grids stay quiet.
      return this.mode === 'currency';
    },
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
