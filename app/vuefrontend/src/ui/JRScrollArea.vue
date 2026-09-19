<template>
  <ScrollArea
    class="jr-scroll-area"
    :class="rootClass"
    :variant="variant"
    :mask="mask"
    :style="areaStyle">
    <ScrollAreaViewport class="jr-scroll-area__viewport">
      <ScrollAreaContent class="jr-scroll-area__content">
        <slot />
      </ScrollAreaContent>
    </ScrollAreaViewport>
    <ScrollAreaScrollbar orientation="vertical" class="jr-scroll-area__scrollbar">
      <ScrollAreaHandle class="jr-scroll-area__handle" />
    </ScrollAreaScrollbar>
  </ScrollArea>
</template>

<script>
import ScrollArea from "primevue/scrollarea";
import ScrollAreaContent from "primevue/scrollareacontent";
import ScrollAreaHandle from "primevue/scrollareahandle";
import ScrollAreaScrollbar from "primevue/scrollareascrollbar";
import ScrollAreaViewport from "primevue/scrollareaviewport";

export default {
  name: "JRScrollArea",
  components: {
    ScrollArea,
    ScrollAreaViewport,
    ScrollAreaContent,
    ScrollAreaScrollbar,
    ScrollAreaHandle,
  },
  props: {
    /** Fixed height of the scroll viewport (CSS length). */
    height: {
      type: String,
      default: "var(--jr-wov-body-height, 22rem)",
    },
    variant: {
      type: String,
      default: "hover",
    },
    mask: {
      type: Boolean,
      default: false,
    },
    rootClass: {
      type: [String, Array, Object],
      default: undefined,
    },
  },
  computed: {
    areaStyle() {
      return {
        height: this.height,
        width: "100%",
      };
    },
  },
};
</script>

<style scoped>
.jr-scroll-area {
  display: block;
  min-height: 0;
  max-width: 100%;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface, #ffffff);
}

.jr-scroll-area__viewport {
  height: 100%;
  width: 100%;
  border-radius: inherit;
}

.jr-scroll-area__content {
  min-width: 100%;
}

.jr-scroll-area__scrollbar {
  background: var(--color-jr-surface-muted, #f9fafb);
}

.jr-scroll-area__handle {
  background: var(--color-jr-hover-border, #d1d5db);
}

.jr-scroll-area :deep(.p-scrollarea-scrollbar[data-orientation="vertical"]) {
  width: 0.625rem;
}

.jr-scroll-area :deep(.p-scrollarea-handle),
.jr-scroll-area :deep(.p-scrollarea-handle-y) {
  border-radius: 0;
  background: var(--color-jr-hover-border, #d1d5db);
}
</style>
