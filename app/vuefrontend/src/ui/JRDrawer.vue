<template>
  <Drawer
    class="jr-pilot"
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
    <slot />
    <template v-if="$slots.footer" #footer>
      <slot name="footer" />
    </template>
  </Drawer>
</template>

<script>
import Drawer from 'primevue/drawer';

export default {
  name: 'JRDrawer',
  components: { Drawer },
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
