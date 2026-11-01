<template>
  <section v-if="show" class="jr-wa-progress" aria-label="Project progress">
    <button
      type="button"
      class="jr-wa-progress__toggle"
      :aria-expanded="expanded ? 'true' : 'false'"
      aria-controls="jr-wa-progress-body"
      @click="expanded = !expanded">
      <span class="jr-wa-progress__label">Project progress</span>
      <span class="jr-wa-progress__toggle-side">
        <JRBadge
          v-if="summary"
          :value="overallLabel"
          :severity="overallSeverity" />
        <svg
          class="jr-wa-progress__chevron"
          :class="{ 'jr-wa-progress__chevron--open': expanded }"
          width="14"
          height="14"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          stroke-width="1.75"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true">
          <path d="M4 6l4 4 4-4" />
        </svg>
      </span>
    </button>

    <div v-if="expanded" id="jr-wa-progress-body" class="jr-wa-progress__body">
      <p v-if="loading" class="jr-wa-progress__muted" role="status">
        Loading project progress…
      </p>
      <p v-else-if="error" class="jr-wa-progress__muted" role="status">
        {{ error }}
      </p>

      <template v-else-if="summary">
        <p class="jr-wa-progress__meta">
          {{ summary.expected_phases_completed }} of
          {{ summary.expected_phases_total }} expected phases completed
        </p>
        <ul v-if="summary.phases?.length" class="jr-wa-progress__phases">
          <li v-for="phase in summary.phases" :key="phase.template_id || phase.category_id">
            <span class="jr-wa-progress__phase-name">{{ phase.category_name || phase.template_name }}</span>
            <JRBadge
              :value="stateLabel(phase.state)"
              :severity="stateSeverity(phase.state)" />
          </li>
        </ul>
        <p v-if="summary.overall_state !== 'completed' && hasMissingPhase" class="jr-wa-progress__muted">
          This project is not complete yet — some expected phases have not finished.
        </p>
      </template>
    </div>
  </section>
</template>

<script>
import axios from 'axios';
import { JRBadge } from '@/ui';
import {
  workAccountStateLabel,
  workAccountStateSeverity,
} from '@/utils/workOrderStatus';

export default {
  name: 'WorkAccountProgressSummary',
  components: { JRBadge },
  props: {
    workAccountId: {
      type: [Number, String],
      default: null,
    },
    /** Increment to force a reload (e.g. after a status change). */
    refreshKey: {
      type: Number,
      default: 0,
    },
  },
  data() {
    return {
      summary: null,
      loading: false,
      error: '',
      hidden: false,
      expanded: false,
      alive: true,
    };
  },
  computed: {
    show() {
      return !!this.workAccountId && !this.hidden;
    },
    overallLabel() {
      return workAccountStateLabel(this.summary?.overall_state);
    },
    overallSeverity() {
      return workAccountStateSeverity(this.summary?.overall_state);
    },
    hasMissingPhase() {
      return (this.summary?.phases || []).some((phase) => phase.state !== 'completed');
    },
  },
  watch: {
    workAccountId: {
      immediate: true,
      handler() {
        this.expanded = false;
        this.load();
      },
    },
    refreshKey() {
      this.load();
    },
  },
  beforeUnmount() {
    this.alive = false;
  },
  methods: {
    stateLabel: workAccountStateLabel,
    stateSeverity: workAccountStateSeverity,
    async load() {
      if (!this.workAccountId) {
        this.summary = null;
        return;
      }
      const workAccountId = this.workAccountId;
      this.loading = true;
      this.error = '';
      this.hidden = false;
      try {
        const { data } = await axios.get(
          `/api/work-accounts/${workAccountId}/work-order-progress/`,
        );
        if (!this.alive || workAccountId !== this.workAccountId) return;
        this.summary = data;
      } catch (err) {
        if (!this.alive || workAccountId !== this.workAccountId) return;
        if (err?.response?.status === 404 || err?.response?.status === 403) {
          this.hidden = true;
          this.summary = null;
        } else {
          this.error = 'Project progress could not be loaded.';
        }
      } finally {
        if (this.alive && workAccountId === this.workAccountId) this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.jr-wa-progress {
  display: grid;
  gap: 0;
  padding: 0.75rem 1rem;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-control, 0);
  background: var(--color-jr-surface);
}

.jr-wa-progress__toggle {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  width: 100%;
  margin: 0;
  padding: 0;
  border: 0;
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.jr-wa-progress__toggle:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
}

.jr-wa-progress__toggle-side {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
}

.jr-wa-progress__chevron {
  flex-shrink: 0;
  color: var(--color-jr-muted);
  transition: transform 0.15s ease;
}

.jr-wa-progress__chevron--open {
  transform: rotate(180deg);
}

.jr-wa-progress__body {
  display: grid;
  gap: 0.5rem;
  margin-top: 0.6rem;
}

.jr-wa-progress__label {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-jr-muted);
}

.jr-wa-progress__meta,
.jr-wa-progress__muted {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.45;
  color: var(--color-jr-muted);
}

.jr-wa-progress__phases {
  display: grid;
  gap: 0.35rem;
  margin: 0;
  padding: 0;
  list-style: none;
}

.jr-wa-progress__phases li {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.35rem 0.5rem;
}

.jr-wa-progress__phase-name {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-jr-text);
  overflow-wrap: anywhere;
}
</style>
