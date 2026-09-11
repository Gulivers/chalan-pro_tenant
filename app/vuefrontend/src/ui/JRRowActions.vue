<template>
  <div
    v-if="visibleActions.length"
    class="jr-row-actions"
    :class="{ 'jr-row-actions--solid': useSolid }">
    <template v-if="!useCompact">
      <Button
        v-for="action in visibleActions"
        :key="action.key"
        type="button"
        class="jr-row-actions__btn"
        :class="[
          action.buttonClass,
          {
            'jr-button': useSolid || isOutlinedAction(action),
            'jr-row-actions__btn--outlined': isOutlinedAction(action) && !useSolid,
          },
        ]"
        :severity="primeSeverity(action)"
        :label="action.label"
        :text="!useSolid && !isOutlinedAction(action)"
        :outlined="useSolid ? isOutlined(action) : isOutlinedAction(action)"
        size="small"
        :aria-label="actionAriaLabel(action)"
        @click="action.command">
        <template v-if="!useSolid && action.icon" #icon="{ class: iconClass }">
          <component
            v-if="isIconComponent(action.icon)"
            :is="action.icon"
            :class="iconClass"
            aria-hidden="true" />
          <span
            v-else
            :class="[iconClass, action.icon]"
            aria-hidden="true" />
        </template>
      </Button>
    </template>
    <template v-else>
      <button
        :id="menuTriggerId"
        type="button"
        class="jr-icon-btn jr-row-actions__more"
        :aria-label="menuAriaLabel"
        aria-haspopup="menu"
        :aria-expanded="menuOpen ? 'true' : 'false'"
        :aria-controls="menuId"
        @click="toggleMenu">
        <svg
          width="16"
          height="16"
          viewBox="0 0 16 16"
          aria-hidden="true"
          fill="currentColor">
          <circle cx="8" cy="3" r="1.4" />
          <circle cx="8" cy="8" r="1.4" />
          <circle cx="8" cy="13" r="1.4" />
        </svg>
      </button>
      <Menu
        :id="menuId"
        ref="menu"
        class="jr-overlay jr-row-menu"
        :model="menuModel"
        :popup="true"
        :ariaLabel="menuAriaLabel"
        :ariaLabelledby="menuTriggerId"
        @show="menuOpen = true"
        @hide="menuOpen = false">
        <template #itemicon="{ item, class: iconClass }">
          <component
            v-if="item.iconComponent"
            :is="item.iconComponent"
            :class="iconClass"
            aria-hidden="true" />
          <span
            v-else-if="item.icon"
            :class="[iconClass, item.icon]"
            aria-hidden="true" />
        </template>
      </Menu>
    </template>
  </div>
</template>

<script>
import Button from 'primevue/button';
import Menu from 'primevue/menu';

let rowActionSeq = 0;
const COMPACT_MQ = '(max-width: 767.98px)';

export default {
  name: 'JRRowActions',
  components: { Button, Menu },
  props: {
    actions: {
      type: Array,
      default: () => [],
    },
    compact: {
      type: Boolean,
      default: undefined,
    },
    solid: {
      type: Boolean,
      default: undefined,
    },
    entityLabel: {
      type: String,
      default: '',
    },
  },
  data() {
    const uid = ++rowActionSeq;
    return {
      menuId: `jr-row-actions-menu-${uid}`,
      menuTriggerId: `jr-row-actions-trigger-${uid}`,
      menuOpen: false,
      detectedCompact: false,
      detectedDrawer: false,
    };
  },
  computed: {
    useSolid() {
      return this.solid === undefined ? this.detectedDrawer : this.solid;
    },
    visibleActions() {
      return (this.actions || []).filter(
        (action) => action && action.visible !== false && typeof action.command === 'function'
      );
    },
    useCompact() {
      return this.compact === undefined ? this.detectedCompact : this.compact;
    },
    menuAriaLabel() {
      return this.entityLabel
        ? `More actions for ${this.entityLabel}`
        : 'More actions';
    },
    menuModel() {
      return this.visibleActions.map((action) => {
        const iconIsComponent = this.isIconComponent(action.icon);
        return {
          label: action.label,
          icon: iconIsComponent ? undefined : action.icon,
          iconComponent: iconIsComponent ? action.icon : undefined,
          class: `jr-row-actions__item--${action.severity || 'primary'}`,
          command: action.command,
        };
      });
    },
  },
  mounted() {
    this.detectedDrawer = !!(this.$el && this.$el.closest?.('.p-drawer'));
    if (this.compact !== undefined) return;
    if (typeof window === 'undefined' || !window.matchMedia) return;
    this.mediaQuery = window.matchMedia(COMPACT_MQ);
    this.detectedCompact = this.mediaQuery.matches;
    this.onMedia = (event) => {
      this.detectedCompact = event.matches;
    };
    if (this.mediaQuery.addEventListener) {
      this.mediaQuery.addEventListener('change', this.onMedia);
    } else {
      this.mediaQuery.addListener(this.onMedia);
    }
  },
  beforeUnmount() {
    if (this.mediaQuery && this.onMedia) {
      if (this.mediaQuery.removeEventListener) {
        this.mediaQuery.removeEventListener('change', this.onMedia);
      } else {
        this.mediaQuery.removeListener(this.onMedia);
      }
    }
  },
  methods: {
    isIconComponent(icon) {
      return !!(icon && typeof icon !== 'string');
    },
    primeSeverity(action) {
      if (!action?.severity || action.severity === 'primary') return undefined;
      return action.severity;
    },
    isOutlined(action) {
      return action?.severity === 'secondary' || action?.severity === 'info';
    },
    /** List-row outlined secondary (e.g. Print) for clearer hover on desktop. */
    isOutlinedAction(action) {
      return !!(action?.outlined || action?.appearance === 'outlined');
    },
    actionAriaLabel(action) {
      return this.entityLabel ? `${action.label} ${this.entityLabel}` : action.label;
    },
    toggleMenu(event) {
      this.$refs.menu?.toggle(event);
    },
  },
};
</script>
