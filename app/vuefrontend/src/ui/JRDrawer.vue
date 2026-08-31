<template>
  <Drawer
    class="jr-pilot jr-drawer"
    :visible="visible"
    :header="header"
    :position="position"
    :modal="modal"
    :dismissable="dismissable"
    :blockScroll="blockScroll"
    @update:visible="$emit('update:visible', $event)"
  >
    <template v-if="$slots.header" #header>
      <slot name="header" />
    </template>
    <template #closebutton="{ closeCallback }">
      <Button
        type="button"
        class="jr-drawer__close"
        severity="secondary"
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
    <slot />
    <template v-if="$slots.footer" #footer>
      <slot name="footer" />
    </template>
  </Drawer>
</template>

<script>
import Button from 'primevue/button';
import Drawer from 'primevue/drawer';

export default {
  name: 'JRDrawer',
  components: { Button, Drawer },
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
    header: {
      type: String,
      default: '',
    },
    position: {
      type: String,
      default: 'right',
    },
    modal: {
      type: Boolean,
      default: true,
    },
    dismissable: {
      type: Boolean,
      default: true,
    },
    blockScroll: {
      type: Boolean,
      default: true,
    },
  },
  emits: ['update:visible'],
};
</script>
