<template>
  <aside class="jr-wov-sidebar" aria-label="Work orders selection sidebar">
    <!-- Header -->
    <div class="jr-wov-sidebar__header">
      <div class="jr-wov-sidebar__header-text">
        <span class="jr-wov-sidebar__eyebrow">
          {{ workAccount ? 'Work Account' : 'Operations' }}
        </span>
        <h2 class="jr-wov-sidebar__title" :title="headerTitle">
          {{ headerTitle }}
        </h2>
      </div>
      <span v-if="eventsCountLabel" class="jr-wov-sidebar__count-badge">
        {{ eventsCountLabel }}
      </span>
    </div>

    <!-- Search bar -->
    <div class="jr-wov-sidebar__search">
      <div class="jr-wov-sidebar__search-wrap">
        <input
          v-model="searchQuery"
          type="text"
          class="jr-wov-sidebar__search-input"
          placeholder="Search work orders, crew…"
          aria-label="Search work orders"
          @keydown.enter="triggerSearch" />
        <button
          v-if="searchQuery"
          type="button"
          class="jr-wov-sidebar__search-clear"
          aria-label="Clear search"
          @click="clearSearch">
          ✕
        </button>
        <button
          type="button"
          class="jr-wov-sidebar__search-submit"
          aria-label="Submit search"
          @click="triggerSearch">
          <svg class="jr-wov-sidebar__icon-search" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading && !events.length" class="jr-wov-sidebar__state">
      <span class="jr-wov-sidebar__spinner" aria-hidden="true"></span>
      <span>Loading work orders…</span>
    </div>

    <!-- Empty State -->
    <div v-else-if="!events.length" class="jr-wov-sidebar__state jr-wov-sidebar__empty">
      <svg class="jr-wov-sidebar__empty-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 002.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 00-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 00.75-.75 2.25 2.25 0 00-.1-.664m-5.8 0A2.251 2.251 0 0113.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25zM6.75 12h.008v.008H6.75V12zm0 3h.008v.008H6.75V15zm0 3h.008v.008H6.75V18z" />
      </svg>
      <p class="jr-wov-sidebar__empty-title">No work orders found</p>
      <p class="jr-wov-sidebar__empty-desc">
        {{ searchQuery ? 'Try adjusting your search criteria.' : 'No orders scheduled for this view.' }}
      </p>
    </div>

    <!-- Event List -->
    <div v-else class="jr-wov-sidebar__list" role="listbox" aria-label="Work order list">
      <div
        v-for="event in events"
        :key="event.id"
        role="option"
        :aria-selected="selectedEventId === event.id ? 'true' : 'false'"
        tabindex="0"
        class="jr-wov-card"
        :class="{ 'jr-wov-card--selected': selectedEventId === event.id }"
        @click="onSelectEvent(event)"
        @keydown.enter="onSelectEvent(event)">
        <!-- Top row for general mode: Order Title / Work Account -->
        <div v-if="isGeneralMode && event.title" class="jr-wov-card__general-title">
          <span class="jr-wov-card__work-title" :title="event.title">
            {{ event.title }}
          </span>
          <span v-if="unreadCount(event.id) > 0" class="jr-wov-card__unread-chip">
            <svg class="jr-wov-card__icon-comment" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd" d="M3.5 2A1.5 1.5 0 002 3.5v9A1.5 1.5 0 003.5 14h1.75v3.25a.75.75 0 001.28.53L10.06 14h6.44A1.5 1.5 0 0018 12.5v-9A1.5 1.5 0 0016.5 2h-13zm1.5 4.75a.75.75 0 01.75-.75h8.5a.75.75 0 010 1.5h-8.5a.75.75 0 01-.75-.75zm0 3a.75.75 0 01.75-.75h5.5a.75.75 0 010 1.5h-5.5a.75.75 0 01-.75-.75z" clip-rule="evenodd" />
            </svg>
            {{ unreadCount(event.id) }}
          </span>
        </div>

        <!-- Structured Row: ID | Category | Status | Crew | Date -->
        <div class="jr-wov-card__row">
          <!-- Col 1: ID -->
          <div class="jr-wov-card__col-id">
            <span class="jr-wov-card__id">{{ event.id }}</span>
          </div>

          <!-- Col 2: Category Badge -->
          <div class="jr-wov-card__col-cat">
            <span
              class="jr-wov-card__cat-badge"
              :class="getCategoryClass(event.crew_category)">
              {{ formatCategory(event.crew_category) }}
            </span>
          </div>

          <!-- Col 3: Crew Name -->
          <div class="jr-wov-card__col-crew">
            <span class="jr-wov-card__crew" :title="event.crew_title">
              {{ event.crew_title || 'Unassigned' }}
            </span>
          </div>

          <!-- Col 4: Date + Unread if in WA mode -->
          <div class="jr-wov-card__col-date">
            <span class="jr-wov-card__date">
              {{ formatDate(event.date) }}
            </span>
            <span
              v-if="!isGeneralMode && unreadCount(event.id) > 0"
              class="jr-wov-card__unread-dot"
              :title="`${unreadCount(event.id)} unread messages`">
              {{ unreadCount(event.id) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Pagination Controls (General mode / Multiple pages) -->
    <div v-if="hasPagination" class="jr-wov-sidebar__pagination">
      <button
        type="button"
        class="jr-wov-sidebar__page-btn"
        :disabled="!hasPrevious || loading"
        @click="$emit('prev-page')">
        Previous
      </button>
      <span class="jr-wov-sidebar__page-info">
        Page {{ currentPage }}
      </span>
      <button
        type="button"
        class="jr-wov-sidebar__page-btn"
        :disabled="!hasNext || loading"
        @click="$emit('next-page')">
        Next
      </button>
    </div>
  </aside>
</template>

<script>
import { computed, ref } from "vue";
import dayjs from "dayjs";
import { useChatStore } from "@/stores/chatStore";

export default {
  name: "WorkOrderSidebar",
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
    unreadMap: {
      type: Object,
      default: () => ({}),
    },
  },
  emits: ["select-event", "search", "prev-page", "next-page"],
  setup(props, { emit }) {
    const chatStore = useChatStore();
    const searchQuery = ref("");

    const headerTitle = computed(() => {
      if (props.workAccount) {
        return `WO ${props.workAccount.id} – ${props.workAccount.title}`;
      }
      return "Work Orders";
    });

    const eventsCountLabel = computed(() => {
      if (props.isGeneralMode && props.totalCount > 0) {
        return `${props.totalCount} orders`;
      }
      if (props.events.length > 0) {
        return `${props.events.length} ${props.events.length === 1 ? "order" : "orders"}`;
      }
      return "";
    });

    const hasPagination = computed(() => props.hasPrevious || props.hasNext);

    const formatCategory = (cat) => {
      if (!cat) return "General";
      const cleaned = String(cat).replace(/^[\p{Emoji}\s\d]+/u, "").trim();
      if (!cleaned) return String(cat);
      return cleaned.charAt(0).toUpperCase() + cleaned.slice(1).toLowerCase();
    };

    const getCategoryClass = (cat) => {
      if (!cat) return "jr-wov-card__cat-badge--default";
      const lower = String(cat).toLowerCase();
      if (lower.includes("trim")) return "jr-wov-card__cat-badge--trim";
      if (lower.includes("rough") || lower.includes("routh")) {
        return "jr-wov-card__cat-badge--rough";
      }
      if (lower.includes("repair") || lower.includes("punch")) {
        return "jr-wov-card__cat-badge--repair";
      }
      return "jr-wov-card__cat-badge--default";
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

    const triggerSearch = () => {
      emit("search", searchQuery.value.trim());
    };

    const clearSearch = () => {
      searchQuery.value = "";
      emit("search", "");
    };

    const onSelectEvent = (event) => {
      emit("select-event", event);
    };

    return {
      searchQuery,
      headerTitle,
      eventsCountLabel,
      hasPagination,
      formatCategory,
      getCategoryClass,
      formatDate,
      unreadCount,
      triggerSearch,
      clearSearch,
      onSelectEvent,
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
  border-radius: var(--radius-jr-control, 0);
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
  background: color-mix(in srgb, var(--color-jr-primary, #2563eb) 10%, var(--color-jr-surface, #fff));
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
  transition: color 0.15s ease, background-color 0.15s ease;
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

.jr-wov-sidebar__empty-icon {
  width: 2rem;
  height: 2rem;
  color: var(--color-jr-muted, #4b5563);
  opacity: 0.6;
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
}

/* Card item */
.jr-wov-card {
  padding: 0.625rem 0.5rem;
  border-bottom: 1px solid var(--color-jr-border, #e5e7eb);
  cursor: pointer;
  transition: background-color 0.15s ease, border-color 0.15s ease;
  user-select: none;
  background: var(--color-jr-surface, #ffffff);
}

.jr-wov-card:hover {
  background: var(--color-jr-surface-muted, #f9fafb);
}

.jr-wov-card--selected {
  background: color-mix(in srgb, var(--color-jr-primary, #2563eb) 10%, var(--color-jr-surface, #ffffff));
}

.jr-wov-card:focus-visible {
  outline: 2px solid var(--color-jr-primary, #2563eb);
  outline-offset: -2px;
}

.jr-wov-card__general-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-bottom: 0.375rem;
}

.jr-wov-card__work-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--color-jr-text, #111827);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.jr-wov-card__unread-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.125rem 0.375rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-jr-warning, #d97706);
  background: color-mix(in srgb, var(--color-jr-warning, #d97706) 12%, var(--color-jr-surface, #fff));
  border: 1px solid color-mix(in srgb, var(--color-jr-warning, #d97706) 25%, transparent);
  border-radius: var(--radius-jr-control, 0);
  flex-shrink: 0;
}

.jr-wov-card__icon-comment {
  width: 0.75rem;
  height: 0.75rem;
}

/* Structured grid row */
.jr-wov-card__row {
  display: grid;
  grid-template-columns: 2.75rem 5rem 1fr auto;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
}

.jr-wov-card__col-id {
  font-weight: 700;
  color: var(--color-jr-text, #111827);
  font-variant-numeric: tabular-nums;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.jr-wov-card__id {
  display: inline-block;
  padding: 0.125rem 0.25rem;
  background: var(--color-jr-surface-muted, #f3f4f6);
  border-radius: var(--radius-jr-control, 0);
  font-size: 0.75rem;
}

.jr-wov-card__cat-badge {
  display: inline-block;
  padding: 0.125rem 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: var(--radius-jr-control, 0);
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.jr-wov-card__cat-badge--rough {
  background: color-mix(in srgb, var(--color-jr-warning, #d97706) 12%, var(--color-jr-surface, #fff));
  color: var(--color-jr-warning, #d97706);
  border: 1px solid color-mix(in srgb, var(--color-jr-warning, #d97706) 25%, transparent);
}

.jr-wov-card__cat-badge--trim {
  background: color-mix(in srgb, var(--color-jr-info, #0284c7) 12%, var(--color-jr-surface, #fff));
  color: var(--color-jr-info, #0284c7);
  border: 1px solid color-mix(in srgb, var(--color-jr-info, #0284c7) 25%, transparent);
}

.jr-wov-card__cat-badge--repair {
  background: color-mix(in srgb, var(--color-jr-muted, #4b5563) 12%, var(--color-jr-surface, #fff));
  color: var(--color-jr-muted, #4b5563);
  border: 1px solid color-mix(in srgb, var(--color-jr-muted, #4b5563) 25%, transparent);
}

.jr-wov-card__cat-badge--default {
  background: color-mix(in srgb, var(--color-jr-muted, #4b5563) 12%, var(--color-jr-surface, #fff));
  color: var(--color-jr-muted, #4b5563);
  border: 1px solid color-mix(in srgb, var(--color-jr-muted, #4b5563) 25%, transparent);
}

.jr-wov-card__col-crew {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.jr-wov-card__crew {
  color: var(--color-jr-muted, #4b5563);
  font-size: 0.75rem;
}

.jr-wov-card__col-date {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.25rem;
  text-align: right;
  white-space: nowrap;
}

.jr-wov-card__date {
  font-size: 0.75rem;
  color: var(--color-jr-muted, #4b5563);
  font-variant-numeric: tabular-nums;
}

.jr-wov-card__unread-dot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1rem;
  height: 1rem;
  padding: 0 0.25rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-jr-warning, #d97706);
  background: color-mix(in srgb, var(--color-jr-warning, #d97706) 20%, var(--color-jr-surface, #fff));
  border-radius: var(--radius-jr-control, 0);
}

/* Pagination bar */
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
  transition: background-color 0.15s ease, border-color 0.15s ease;
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
