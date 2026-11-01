<template>
  <div class="jr-dual-pick">
    <PickList
      v-model="lists"
      :dataKey="dataKey"
      :breakpoint="breakpoint"
      :showSourceFilter="true"
      :showTargetFilter="true"
      :sourceFilterPlaceholder="filterPlaceholder"
      :targetFilterPlaceholder="filterPlaceholder"
      :filterBy="filterBy"
      :showSourceControls="false"
      :showTargetControls="false"
      :pt="pickListPt"
      class="jr-dual-pick__list">
      <template #sourceheader>{{ sourceHeader }}</template>
      <template #targetheader>{{ targetHeader }}</template>
      <template #option="{ option }">
        <span class="jr-dual-pick__option">{{ optionLabel(option) }}</span>
      </template>
    </PickList>
    <p v-if="hint" class="jr-dual-pick__hint">{{ hint }}</p>
  </div>
</template>

<script>
import PickList from 'primevue/picklist';

export default {
  name: 'DualListPick',
  components: { PickList },
  props: {
    modelValue: {
      type: Array,
      default: () => [[], []],
    },
    dataKey: {
      type: String,
      default: 'id',
    },
    labelKey: {
      type: String,
      default: 'label',
    },
    sourceHeader: {
      type: String,
      default: 'Available',
    },
    targetHeader: {
      type: String,
      default: 'Chosen',
    },
    filterPlaceholder: {
      type: String,
      default: 'Filter',
    },
    filterBy: {
      type: String,
      default: 'label,name',
    },
    hint: {
      type: String,
      default: '',
    },
    breakpoint: {
      type: String,
      default: '960px',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['update:modelValue'],
  computed: {
    lists: {
      get() {
        const value = this.modelValue;
        if (Array.isArray(value) && value.length === 2) {
          return value;
        }
        return [[], []];
      },
      set(next) {
        if (this.disabled) return;
        this.$emit('update:modelValue', next);
      },
    },
    pickListPt() {
      return {
        root: { class: this.disabled ? 'jr-dual-pick--disabled' : '' },
      };
    },
  },
  methods: {
    optionLabel(option) {
      if (!option) return '';
      if (typeof option === 'string') return option;
      return option[this.labelKey] || option.name || String(option.id ?? '');
    },
  },
};
</script>

<style scoped>
.jr-dual-pick {
  width: 100%;
}
.jr-dual-pick__list {
  width: 100%;
}
.jr-dual-pick__option {
  font-size: 0.875rem;
  line-height: 1.4;
  word-break: break-word;
}
.jr-dual-pick__hint {
  margin: 0.65rem 0 0;
  max-width: 62ch;
  font-size: 0.8125rem;
  line-height: 1.5;
  color: var(--color-jr-muted, #4b5563);
}
.jr-dual-pick--disabled {
  opacity: 0.65;
  pointer-events: none;
}
:deep(.p-picklist-list) {
  min-height: 14rem;
  max-height: 18rem;
}
:deep(.p-picklist-header) {
  font-size: 0.875rem;
  font-weight: 600;
  line-height: 1.35;
}
</style>
