<template>
  <ol
    v-if="statuses.length"
    class="jr-doc-status-progress"
    :class="{ 'jr-doc-status-progress--stacked': stacked }"
    aria-label="Document status progress">
    <li
      v-for="(step, index) in statuses"
      :key="step.id || step.code || index"
      class="jr-doc-status-progress__step"
      :data-state="stepState(step)">
      <span class="jr-doc-status-progress__dot" aria-hidden="true" />
      <span class="jr-doc-status-progress__label">{{ step.name }}</span>
      <span
        v-if="index < statuses.length - 1"
        class="jr-doc-status-progress__connector"
        aria-hidden="true" />
    </li>
  </ol>
</template>

<script>
export default {
  name: 'DocumentStatusProgress',
  props: {
    statuses: {
      type: Array,
      default: () => [],
    },
    currentSequence: {
      type: Number,
      default: null,
    },
    /** Force the mobile/stacked layout (e.g. inside a right drawer). */
    stacked: {
      type: Boolean,
      default: false,
    },
  },
  methods: {
    stepState(step) {
      const current = Number(this.currentSequence);
      const sequence = Number(step.sequence);
      if (!Number.isFinite(current) || !Number.isFinite(sequence)) return 'pending';
      if (sequence < current) return 'done';
      if (sequence === current) return 'current';
      return 'pending';
    },
  },
};
</script>

<style scoped>
.jr-doc-status-progress {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 0.35rem 0;
  margin: 0;
  padding: 0;
  list-style: none;
}

.jr-doc-status-progress__step {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  grid-template-rows: auto auto;
  align-items: center;
  column-gap: 0.4rem;
  min-width: 5.5rem;
  flex: 1 1 5.5rem;
  max-width: 100%;
}

.jr-doc-status-progress__dot {
  width: 0.65rem;
  height: 0.65rem;
  border-radius: 50%;
  border: 1px solid var(--color-jr-border);
  background: var(--color-jr-surface);
}

.jr-doc-status-progress__label {
  font-size: 0.75rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-jr-muted);
  overflow-wrap: anywhere;
}

.jr-doc-status-progress__connector {
  grid-column: 1 / -1;
  height: 1px;
  margin: 0.35rem 0 0.15rem;
  background: var(--color-jr-border);
}

.jr-doc-status-progress__step:last-child .jr-doc-status-progress__connector {
  display: none;
}

.jr-doc-status-progress__step[data-state='done'] .jr-doc-status-progress__dot {
  background: var(--color-jr-primary);
  border-color: var(--color-jr-primary);
}

.jr-doc-status-progress__step[data-state='done'] .jr-doc-status-progress__label {
  color: var(--color-jr-text);
}

.jr-doc-status-progress__step[data-state='current'] .jr-doc-status-progress__dot {
  background: var(--color-jr-primary);
  border-color: var(--color-jr-primary);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-jr-primary) 18%, transparent);
  animation: jr-doc-status-dot-pulse 1.35s ease-in-out infinite;
}

.jr-doc-status-progress__step[data-state='current'] .jr-doc-status-progress__label {
  color: var(--color-jr-text);
  font-weight: 700;
}

@keyframes jr-doc-status-dot-pulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-jr-primary) 22%, transparent);
  }
  50% {
    opacity: 0.4;
    transform: scale(0.92);
    box-shadow: 0 0 0 6px color-mix(in srgb, var(--color-jr-primary) 10%, transparent);
  }
}

@media (prefers-reduced-motion: reduce) {
  .jr-doc-status-progress__step[data-state='current'] .jr-doc-status-progress__dot {
    animation: none;
    opacity: 1;
    transform: none;
  }
}

@media (min-width: 768px) {
  .jr-doc-status-progress:not(.jr-doc-status-progress--stacked) {
    flex-wrap: nowrap;
    align-items: center;
  }

  .jr-doc-status-progress:not(.jr-doc-status-progress--stacked)
    .jr-doc-status-progress__step {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    min-width: 0;
    flex: 1 1 0;
  }

  .jr-doc-status-progress:not(.jr-doc-status-progress--stacked)
    .jr-doc-status-progress__connector {
    display: block;
    flex: 1 1 auto;
    min-width: 1.25rem;
    height: 1px;
    margin: 0;
    order: 3;
  }

  .jr-doc-status-progress:not(.jr-doc-status-progress--stacked)
    .jr-doc-status-progress__label {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.jr-doc-status-progress--stacked {
  flex-direction: column;
  flex-wrap: nowrap;
  align-items: stretch;
  gap: 0;
}

.jr-doc-status-progress--stacked .jr-doc-status-progress__step {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  flex: none;
  min-width: 0;
  max-width: none;
  width: 100%;
}

.jr-doc-status-progress--stacked .jr-doc-status-progress__connector {
  display: block;
  grid-column: 1 / -1;
  height: 1px;
  margin: 0.35rem 0 0.15rem;
  order: unset;
  min-width: 0;
  flex: none;
}
</style>
