<template>
  <Dialog
    :class="dialogClass"
    :visible="visible"
    :header="header"
    modal
    :dismissableMask="true"
    @update:visible="$emit('update:visible', $event)"
  >
    <template #closebutton="{ closeCallback }">
      <Button
        type="button"
        class="jr-dialog__close"
        :class="{ 'jr-dialog__close--danger': isDanger }"
        text
        rounded
        aria-label="Close"
        @click="closeCallback">
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          aria-hidden="true"
          fill="none"
          stroke="currentColor"
          stroke-width="1.7"
          stroke-linecap="round">
          <path d="M4 4l8 8M12 4l-8 8" />
        </svg>
      </Button>
    </template>
    <p v-if="message" class="jr-dialog__message">{{ message }}</p>
    <slot />
    <template v-if="showFooter" #footer>
      <div class="jr-dialog__footer">
        <JRButton variant="secondary" @click="$emit('update:visible', false)">
          {{ cancelLabel }}
        </JRButton>
        <JRButton :variant="confirmVariant" @click="$emit('confirm')">
          {{ confirmLabel }}
        </JRButton>
      </div>
    </template>
  </Dialog>
</template>

<script>
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import JRButton from './JRButton.vue';

export default {
  name: 'JRDialog',
  components: { Button, Dialog, JRButton },
  computed: {
    isDanger() {
      return this.confirmVariant === 'danger';
    },
    dialogClass() {
      return [
        'jr-pilot',
        'jr-dialog',
        this.size === 'wide' ? 'jr-dialog--wide' : '',
        this.isDanger ? 'jr-dialog--danger' : '',
      ].filter(Boolean);
    },
  },
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
    header: {
      type: String,
      default: '',
    },
    message: {
      type: String,
      default: '',
    },
    cancelLabel: {
      type: String,
      default: 'Cancel',
    },
    confirmLabel: {
      type: String,
      default: 'Confirm',
    },
    confirmVariant: {
      type: String,
      default: 'primary',
    },
    showFooter: {
      type: Boolean,
      default: true,
    },
    size: {
      type: String,
      default: 'default',
      validator: (value) => ['default', 'wide'].includes(value),
    },
  },
  emits: ['update:visible', 'confirm'],
};
</script>
