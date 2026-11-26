<template>
  <aside
    class="jr-wov-sidebar"
    :aria-label="$t('workOrderViewer.sidebarAria')">
    <!-- Header -->
    <div class="jr-wov-sidebar__header">
      <div class="jr-wov-sidebar__header-text">
        <span class="jr-wov-sidebar__eyebrow">
          {{
            workAccountFilterActive
              ? $t("workOrderViewer.thisWorkAccount")
              : $t("workOrderViewer.operations")
          }}
        </span>
        <h2 class="jr-wov-sidebar__title" :title="headerTitle">
          {{ headerTitle }}
        </h2>
      </div>
      <span v-if="eventsCountLabel" class="jr-wov-sidebar__count-badge">
        {{ eventsCountLabel }}
      </span>
    </div>

    <!-- Active work-account filter (from /work-accounts/:id/view) -->
    <div
      v-if="workAccountFilterActive"
      class="jr-wov-sidebar__filter"
      role="status">
      <span class="jr-wov-sidebar__filter-text">
        {{
          workAccount?.title
            ? $t("workOrderViewer.filteredByWaNamed", {
                title: workAccount.title,
              })
            : $t("workOrderViewer.filteredByWa")
        }}
      </span>
      <button
        type="button"
        class="jr-wov-sidebar__filter-clear"
        @click="$emit('clear-work-account-filter')">
        {{ $t("workOrderViewer.showAllOperations") }}
      </button>
    </div>

    <!-- Operations scope chips -->
    <div
      v-if="showOpsScopes"
      class="jr-wov-sidebar__scopes"
      role="group"
      :aria-label="$t('workOrderViewer.opsScopeAria')">
      <button
        v-for="chip in scopeChips"
        :key="chip.id"
        type="button"
        class="jr-wov-sidebar__scope"
        :class="{ 'jr-wov-sidebar__scope--on': opsScope === chip.id }"
        :aria-pressed="opsScope === chip.id ? 'true' : 'false'"
        @click="onScope(chip.id)">
        {{ chip.label }}
      </button>
    </div>

    <!-- Search bar: Enter submits same as lupa -->
    <form class="jr-wov-sidebar__search" @submit.prevent="triggerSearch">
      <div class="jr-wov-sidebar__search-wrap">
        <input
          v-model="searchInput"
          type="search"
          enterkeyhint="search"
          class="jr-wov-sidebar__search-input"
          :placeholder="$t('workOrderViewer.searchPlaceholder')"
          :aria-label="$t('workOrderViewer.searchAria')"
          @keydown.enter.prevent="triggerSearch" />
        <button
          v-if="searchInput"
          type="button"
          class="jr-wov-sidebar__search-clear"
          :aria-label="$t('common.clearSearch')"
          @click="clearSearch">
          ✕
        </button>
        <button
          type="submit"
          class="jr-wov-sidebar__search-submit"
          :aria-label="$t('workOrderViewer.submitSearch')">
          <svg
            class="jr-wov-sidebar__icon-search"
            viewBox="0 0 20 20"
            fill="currentColor"
            aria-hidden="true">
            <path
              fill-rule="evenodd"
              d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z"
              clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </form>

    <!-- Loading State -->
    <div v-if="loading && !events.length" class="jr-wov-sidebar__state">
      <span class="jr-wov-sidebar__spinner" aria-hidden="true"></span>
      <span>{{ $t("workOrderViewer.loadingOrders") }}</span>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="!events.length"
      class="jr-wov-sidebar__state jr-wov-sidebar__empty">
      <p class="jr-wov-sidebar__empty-title">
        {{ $t("workOrderViewer.noWorkOrders") }}
      </p>
      <p class="jr-wov-sidebar__empty-desc">
        {{
          searchInput || searchQuery
            ? $t("workOrderViewer.emptySearchDesc")
            : $t("workOrderViewer.emptyNoneDesc")
        }}
      </p>
    </div>

    <!-- Event List — hierarchy: phase → crew → date → status -->
    <div
      v-else
      class="jr-wov-sidebar__list"
      role="listbox"
      :aria-label="$t('workOrderViewer.ordersListAria')">
      <button
        v-for="event in events"
        :key="event.id"
        type="button"
        role="option"
        :aria-selected="selectedEventId === event.id ? 'true' : 'false'"
        class="jr-wov-card"
        :class="{ 'jr-wov-card--selected': selectedEventId === event.id }"
        @click="onSelectEvent(event)">
        <div class="jr-wov-card__phase">
          <span
            class="jr-wov-card__phase-name"
            :class="getCategoryClass(event.crew_category || event.phase)">
            {{ formatCategory(event.crew_category || event.phase) }}
          </span>
          <span class="jr-wov-card__id">
            {{ $t("workOrderViewer.orderChip", { id: event.id }) }}
          </span>
        </div>

        <div
          v-if="isGeneralMode && event.title"
          class="jr-wov-card__wa"
          :title="event.title">
          {{ event.title }}
          <span
            v-if="unreadCount(event.id) > 0"
            class="jr-wov-card__unread-chip">
            {{ unreadCount(event.id) }}
          </span>
        </div>

        <div class="jr-wov-card__meta">
          <span>
            <strong>{{
              event.crew_title || $t("workOrderViewer.unassigned")
            }}</strong>
          </span>
          <span>{{ formatDate(event.date) }}</span>
          <span
            v-if="!isGeneralMode && unreadCount(event.id) > 0"
            class="jr-wov-card__unread-dot"
            :title="
              $t('workOrderViewer.unreadTitle', {
                count: unreadCount(event.id),
              })
            ">
            {{ unreadCount(event.id) }}
          </span>
        </div>

        <div
          v-if="statusLabel(event)"
          class="jr-wov-card__status">
          <JRBadge
            :value="statusLabel(event)"
            :severity="statusSeverity(event)" />
        </div>
      </button>
    </div>

    <!-- Pagination -->
    <div v-if="hasPagination" class="jr-wov-sidebar__pagination">
      <button
        type="button"
        class="jr-wov-sidebar__page-btn"
        :disabled="!hasPrevious || loading"
        @click="$emit('prev-page')">
        {{ $t("workOrderViewer.previous") }}
      </button>
      <span class="jr-wov-sidebar__page-info">
        {{ $t("workOrderViewer.page", { page: currentPage }) }}
      </span>
      <button
        type="button"
        class="jr-wov-sidebar__page-btn"
        :disabled="!hasNext || loading"
        @click="$emit('next-page')">
        {{ $t("common.next") }}
      </button>
    </div>
  </aside>
</template>

<script>
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import dayjs from "dayjs";
import { useChatStore } from "@/stores/chatStore";
import { JRBadge } from "@/ui";
import { tStatus } from "@/utils/statusI18n";
import { workOrderStatusSeverity } from "@/utils/workOrderStatus";

export default {
  name: "WorkOrderSidebar",
  components: { JRBadge },
  props: {
    workAccount: {
      type: Object,
      default: null,
    },
    events: {
      type: Array,
      default: () => [],
    },
    selectedEventId: {
      type: Number,
      default: null,
    },
    totalCount: {
      type: Number,
      default: 0,
    },
    loading: {
      type: Boolean,
      default: false,
    },
    hasPrevious: {
      type: Boolean,
      default: false,
    },
    hasNext: {
      type: Boolean,
      default: false,
    },
    currentPage: {
      type: Number,
      default: 1,
    },
    isGeneralMode: {
      type: Boolean,
      default: false,
    },
    workAccountFilterActive: {
      type: Boolean,
      default: false,
    },
    opsScope: {
      type: String,
      default: "active",
    },
    unreadMap: {
      type: Object,
      default: () => ({}),
    },
    /** Applied search term owned by the parent (survives remount). */
    searchQuery: {
      type: String,
      default: "",
    },
  },
  emits: [
    "select-event",
    "search",
    "prev-page",
    "next-page",
    "clear-work-account-filter",
    "update:ops-scope",
  ],
  setup(props, { emit }) {
    const { t } = useI18n({ useScope: "global" });
    const chatStore = useChatStore();
    const searchInput = ref(props.searchQuery || "");

    watch(
      () => props.searchQuery,
      (value) => {
        const next = value || "";
        if (searchInput.value !== next) {
          searchInput.value = next;
        }
      }
    );

    const headerTitle = computed(() => {
      if (props.workAccountFilterActive) {
        return t("workOrderViewer.ordersForAccount");
      }
      return t("workOrderViewer.workOrders");
    });

    const showOpsScopes = computed(
      () => props.isGeneralMode && !props.workAccountFilterActive
    );

    const scopeChips = computed(() => [
      { id: "active", label: t("workOrderViewer.opsScopeActive") },
      { id: "leaves", label: t("workOrderViewer.opsScopeLeaves") },
      { id: "all", label: t("workOrderViewer.opsScopeAll") },
    ]);

    const eventsCountLabel = computed(() => {
      if (props.isGeneralMode && props.totalCount > 0) {
        return t("workOrderViewer.ordersCount", {
          count: props.totalCount,
        });
      }
      if (props.events.length > 0) {
        const count = props.events.length;
        return count === 1
          ? t("workOrderViewer.orderCountOne", { count })
          : t("workOrderViewer.orderCountMany", { count });
      }
      return "";
    });

    const hasPagination = computed(() => props.hasPrevious || props.hasNext);

    const formatCategory = (cat) => {
      if (!cat) return String(t("workOrderViewer.generalCategory")).toUpperCase();
      const cleaned = String(cat)
        .replace(/^[\p{Emoji}\s\d]+/u, "")
        .trim();
      if (!cleaned) return String(cat).toUpperCase();
      return cleaned.toUpperCase();
    };

    const getCategoryClass = (cat) => {
      if (!cat) return "jr-wov-card__phase-name--default";
      const lower = String(cat).toLowerCase();
      if (lower.includes("trim")) return "jr-wov-card__phase-name--trim";
      if (lower.includes("rough") || lower.includes("routh")) {
        return "jr-wov-card__phase-name--rough";
      }
      if (lower.includes("repair") || lower.includes("punch")) {
        return "jr-wov-card__phase-name--repair";
      }
      return "jr-wov-card__phase-name--default";
    };

    const formatDate = (dateStr) => {
      if (!dateStr) return "—";
      const d = dayjs(dateStr);
      return d.isValid() ? d.format("MM/DD") : dateStr;
    };

    const unreadCount = (eventId) => {
      if (!eventId) return 0;
      if (props.unreadMap && props.unreadMap[eventId] !== undefined) {
        return props.unreadMap[eventId];
      }
      const item = chatStore.unreadEvents?.find((e) => e.id === eventId);
      return item ? item.unread_messages : 0;
    };

    const statusLabel = (event) => {
      const code = event?.status_code || event?.work_order_status_code;
      const name = event?.work_order_status_name;
      if (!code && !name) return "";
      return tStatus(code, name);
    };

    const statusSeverity = (event) =>
      workOrderStatusSeverity({
        status_code: event?.status_code || event?.work_order_status_code,
        is_terminal: !!event?.work_order_status_is_terminal,
      });

    const triggerSearch = () => {
      emit("search", searchInput.value.trim());
    };

    const clearSearch = () => {
      searchInput.value = "";
      emit("search", "");
    };

    const onSelectEvent = (event) => {
      emit("select-event", event);
    };

    const onScope = (id) => {
      if (id === props.opsScope) return;
      emit("update:ops-scope", id);
    };

    return {
      searchInput,
      headerTitle,
      showOpsScopes,
      scopeChips,
      eventsCountLabel,
      hasPagination,
      formatCategory,
      getCategoryClass,
      formatDate,
      unreadCount,
      statusLabel,
      statusSeverity,
      triggerSearch,
      clearSearch,
      onSelectEvent,
      onScope,
    };
  },
};
</script>

<style scoped>
.jr-wov-sidebar {
  display: flex;
  flex-direction: column;
  background: var(--color-jr-surface, #ffffff);
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-panel, 0.75rem);
  overflow: hidden;
}

.jr-wov-sidebar__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: var(--color-jr-surface-muted, #f9fafb);
  border-bottom: 1px solid var(--color-jr-border, #e5e7eb);
}

.jr-wov-sidebar__filter {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.45rem 0.75rem;
  border-bottom: 1px solid var(--color-jr-border, #e5e7eb);
  background: color-mix(
    in srgb,
    var(--color-jr-primary, #2563eb) 8%,
    var(--color-jr-surface, #ffffff)
  );
}

.jr-wov-sidebar__filter-text {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-jr-text, #111827);
  line-height: 1.3;
}

.jr-wov-sidebar__filter-clear {
  flex-shrink: 0;
  border: 0;
  padding: 0.2rem 0.45rem;
  background: transparent;
  color: var(--color-jr-primary, #2563eb);
  font: inherit;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.jr-wov-sidebar__filter-clear:hover {
  color: var(--color-jr-primary-hover, #1d4ed8);
}

.jr-wov-sidebar__filter-clear:focus-visible {
  outline: 2px solid var(--color-jr-primary, #2563eb);
  outline-offset: 2px;
}

.jr-wov-sidebar__scopes {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  padding: 0.55rem 0.75rem;
  border-bottom: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface, #ffffff);
}

.jr-wov-sidebar__scope {
  border: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface, #ffffff);
  color: var(--color-jr-muted, #4b5563);
  font: inherit;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.3rem 0.55rem;
  border-radius: var(--radius-jr-control, 0);
  cursor: pointer;
}

.jr-wov-sidebar__scope:hover {
  border-color: var(--color-jr-hover-border, #d1d5db);
  color: var(--color-jr-text, #111827);
}

.jr-wov-sidebar__scope--on {
  border-color: var(--color-jr-primary, #2563eb);
  background: color-mix(
    in srgb,
    var(--color-jr-primary, #2563eb) 10%,
    var(--color-jr-surface, #ffffff)
  );
  color: var(--color-jr-primary, #2563eb);
}

.jr-wov-sidebar__scope:focus-visible {
  outline: 2px solid var(--color-jr-primary, #2563eb);
  outline-offset: 2px;
}

.jr-wov-sidebar__header-text {
  min-width: 0;
  flex: 1;
}

.jr-wov-sidebar__eyebrow {
  display: block;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-jr-muted, #4b5563);
}

.jr-wov-sidebar__title {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-jr-text, #111827);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.jr-wov-sidebar__count-badge {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-jr-primary, #2563eb);
  background: color-mix(
    in srgb,
    var(--color-jr-primary, #2563eb) 10%,
    var(--color-jr-surface, #fff)
  );
  border-radius: var(--radius-jr-control, 0);
}

.jr-wov-sidebar__search {
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface, #ffffff);
}

.jr-wov-sidebar__search-wrap {
  display: flex;
  align-items: center;
  position: relative;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-control, 0);
  background: var(--color-jr-surface, #ffffff);
  transition: border-color 0.15s ease;
}

.jr-wov-sidebar__search-wrap:focus-within {
  border-color: var(--color-jr-primary, #2563eb);
}

.jr-wov-sidebar__search-input {
  flex: 1;
  min-width: 0;
  padding: 0.4rem 0.625rem;
  font-size: 0.8125rem;
  border: none;
  background: transparent;
  color: var(--color-jr-text, #111827);
  outline: none;
}

.jr-wov-sidebar__search-input::-webkit-search-cancel-button {
  display: none;
}

.jr-wov-sidebar__search-input::placeholder {
  color: var(--color-jr-muted, #4b5563);
}

.jr-wov-sidebar__search-clear {
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
  color: var(--color-jr-muted, #4b5563);
  background: transparent;
  border: none;
  cursor: pointer;
}

.jr-wov-sidebar__search-clear:hover {
  color: var(--color-jr-text, #111827);
}

.jr-wov-sidebar__search-submit {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem 0.625rem;
  background: transparent;
  border: none;
  color: var(--color-jr-muted, #4b5563);
  cursor: pointer;
  border-left: 1px solid var(--color-jr-border, #e5e7eb);
}

.jr-wov-sidebar__search-submit:hover {
  color: var(--color-jr-primary, #2563eb);
  background: var(--color-jr-surface-muted, #f9fafb);
}

.jr-wov-sidebar__icon-search {
  width: 0.9375rem;
  height: 0.9375rem;
}

.jr-wov-sidebar__state {
  padding: 2.5rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.625rem;
  color: var(--color-jr-muted, #4b5563);
  font-size: 0.8125rem;
  text-align: center;
}

.jr-wov-sidebar__empty-title {
  margin: 0;
  font-weight: 600;
  font-size: 0.875rem;
  color: var(--color-jr-text, #111827);
}

.jr-wov-sidebar__empty-desc {
  margin: 0;
  font-size: 0.75rem;
  color: var(--color-jr-muted, #4b5563);
}

.jr-wov-sidebar__spinner {
  width: 1.25rem;
  height: 1.25rem;
  border: 2px solid var(--color-jr-border, #e5e7eb);
  border-top-color: var(--color-jr-primary, #2563eb);
  border-radius: 50%;
  animation: jr-spin 0.7s linear infinite;
}

@keyframes jr-spin {
  to {
    transform: rotate(360deg);
  }
}

.jr-wov-sidebar__list {
  flex: 1;
  overflow-y: auto;
  max-height: calc(100vh - 21rem);
  min-height: 18rem;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  padding: 0.5rem;
}

.jr-wov-card {
  display: block;
  width: 100%;
  text-align: left;
  padding: 0.65rem 0.7rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-control, 0);
  cursor: pointer;
  background: var(--color-jr-surface, #ffffff);
  font: inherit;
  color: inherit;
  transition: background-color 0.15s ease, border-color 0.15s ease;
}

.jr-wov-card:hover {
  border-color: var(--color-jr-hover-border, #d1d5db);
  background: var(--color-jr-surface-muted, #f9fafb);
}

.jr-wov-card--selected {
  border-color: var(--color-jr-primary, #2563eb);
  background: color-mix(
    in srgb,
    var(--color-jr-primary, #2563eb) 8%,
    var(--color-jr-surface, #ffffff)
  );
  box-shadow: inset 3px 0 0 var(--color-jr-primary, #2563eb);
}

.jr-wov-card:focus-visible {
  outline: 2px solid var(--color-jr-primary, #2563eb);
  outline-offset: 2px;
}

.jr-wov-card__phase {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.3rem;
}

.jr-wov-card__phase-name {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text, #111827);
  letter-spacing: -0.01em;
}

.jr-wov-card__phase-name--rough {
  color: var(--color-jr-warning-text, #92400e);
}

.jr-wov-card__phase-name--trim {
  color: var(--color-jr-info-text, #1e40af);
}

.jr-wov-card__phase-name--repair,
.jr-wov-card__phase-name--default {
  color: var(--color-jr-text, #111827);
}

.jr-wov-card__id {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-jr-muted, #4b5563);
  font-variant-numeric: tabular-nums;
}

.jr-wov-card__wa {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.3rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-jr-text, #111827);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.jr-wov-card__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem 0.75rem;
  font-size: 0.8125rem;
  color: var(--color-jr-muted, #4b5563);
}

.jr-wov-card__meta strong {
  font-weight: 500;
  color: var(--color-jr-text, #111827);
}

.jr-wov-card__status {
  margin-top: 0.45rem;
}

.jr-wov-card__unread-chip,
.jr-wov-card__unread-dot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1rem;
  height: 1rem;
  padding: 0 0.25rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-jr-warning-text, #92400e);
  background: var(--color-jr-warning-subtle, #fef3c7);
  border-radius: var(--radius-jr-control, 0);
  flex-shrink: 0;
}

.jr-wov-sidebar__pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.625rem 0.75rem;
  background: var(--color-jr-surface, #ffffff);
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
  margin-top: auto;
}

.jr-wov-sidebar__page-btn {
  padding: 0.25rem 0.625rem;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface, #ffffff);
  color: var(--color-jr-text, #111827);
  border-radius: var(--radius-jr-control, 0);
  cursor: pointer;
}

.jr-wov-sidebar__page-btn:hover:not(:disabled) {
  background: var(--color-jr-surface-muted, #f3f4f6);
  border-color: var(--color-jr-hover-border, #d1d5db);
}

.jr-wov-sidebar__page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.jr-wov-sidebar__page-info {
  font-size: 0.75rem;
  color: var(--color-jr-muted, #4b5563);
}
</style>
