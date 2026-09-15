<template>
  <JRPage>
    <div v-if="isLoading" class="jr-wov__loading" role="status" aria-live="polite">
      <p>Loading work account…</p>
    </div>

    <template v-else-if="loadError">
      <JRPageHeader title="Work Order Viewer" />
      <JREmptyState
        title="Work account not found"
        :description="loadError">
        <JRButton type="button" variant="ghost" size="sm" @click="goToList">
          Back to Work Accounts
        </JRButton>
      </JREmptyState>
    </template>

    <template v-else>
      <!-- Page Header (reactive to selected Work Order) -->
      <header class="jr-wov__header jr-page-header">
        <div class="jr-wov__header-text">
          <p class="jr-wov__eyebrow">
            {{ isGeneralMode && !workAccount ? 'Operations' : 'Work Account' }}
          </p>
          <h1 class="jr-page-header__title">{{ displayHeaderTitle }}</h1>
          <dl v-if="headerMetaItems.length" class="jr-wov__meta">
            <div
              v-for="item in headerMetaItems"
              :key="item.label"
              class="jr-wov__meta-item">
              <dt class="jr-wov__meta-label">{{ item.label }}</dt>
              <dd class="jr-wov__meta-value" :title="item.value">{{ item.value }}</dd>
            </div>
          </dl>
          <p v-else-if="displayHeaderSubtitle" class="jr-page-header__desc">
            {{ displayHeaderSubtitle }}
          </p>
        </div>
        <div class="jr-page-header__actions jr-wov__header-actions">
          <JRButton
            type="button"
            :variant="sidebarOpen ? 'primary' : 'secondary'"
            size="sm"
            :aria-expanded="sidebarOpen ? 'true' : 'false'"
            :aria-controls="isMobile ? 'jr-wov-orders-drawer' : 'jr-wov-orders-sidebar'"
            @click="toggleSidebar">
            Work Orders
            <JRBadge
              v-if="ordersBadgeCount"
              class="jr-wov__orders-badge"
              :value="ordersBadgeCount"
              :severity="sidebarOpen ? 'contrast' : 'info'" />
          </JRButton>
          <JRButton type="button" variant="ghost" size="sm" @click="goToList">
            Back to list
          </JRButton>
          <JRButton
            v-if="canEdit && effectiveWorkAccountId"
            type="button"
            size="sm"
            @click="goToEdit">
            Edit
          </JRButton>
        </div>
      </header>

      <!-- 2-Column Responsive Layout (desktop: tabs left, sidebar right; mobile: tabs full width) -->
      <div
        class="jr-wov__layout"
        :class="{ 'jr-wov__layout--sidebar-collapsed': !sidebarOpen || isMobile }">
        <div class="jr-wov__main-col">
          <WorkOrderViewerTabs
            :work-account-id="effectiveWorkAccountId"
            :event-id="scheduleEventId"
            :initial-tab="initialTab" />
        </div>

        <!-- Desktop Right Sidebar (in-flow on desktop when sidebarOpen is true) -->
        <aside
          v-if="!isMobile && sidebarOpen"
          id="jr-wov-orders-sidebar"
          class="jr-wov__sidebar-col"
          aria-label="Work Orders">
          <WorkOrderSidebar
            :work-account="workAccount"
            :events="events"
            :selected-event-id="scheduleEventId"
            :total-count="totalEventsCount"
            :loading="isEventsLoading"
            :has-previous="hasPrevious"
            :has-next="hasNext"
            :current-page="currentPage"
            :is-general-mode="isGeneralMode"
            :unread-map="unreadMap"
            @select-event="handleSelectEvent"
            @search="handleSearch"
            @prev-page="handlePrevPage"
            @next-page="handleNextPage" />
        </aside>
      </div>

      <!-- Mobile Offcanvas Drawer (overlay, right, backdrop) -->
      <JRDrawer
        v-if="isMobile"
        id="jr-wov-orders-drawer"
        class="jr-wov__drawer"
        :visible="sidebarOpen"
        position="right"
        :modal="true"
        :dismissable="true"
        :block-scroll="true"
        header=" "
        @update:visible="onSidebarVisible">
        <WorkOrderSidebar
          :work-account="workAccount"
          :events="events"
          :selected-event-id="scheduleEventId"
          :total-count="totalEventsCount"
          :loading="isEventsLoading"
          :has-previous="hasPrevious"
          :has-next="hasNext"
          :current-page="currentPage"
          :is-general-mode="isGeneralMode"
          :unread-map="unreadMap"
          @select-event="handleSelectEvent"
          @search="handleSearch"
          @prev-page="handlePrevPage"
          @next-page="handleNextPage" />
      </JRDrawer>
    </template>
  </JRPage>
</template>

<script>
import { computed, getCurrentInstance, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import WorkOrderSidebar from "@components/work-accounts/WorkOrderSidebar.vue";
import WorkOrderViewerTabs from "@components/work-accounts/WorkOrderViewerTabs.vue";
import { useChatStore } from "@/stores/chatStore";
import {
  resolveScheduleEventForWorkAccount,
  WORK_ORDER_VIEWER_TAB_IDS,
} from "@/utils/resolveScheduleEventForWorkAccount";
import {
  JRPage,
  JRPageHeader,
  JRButton,
  JRBadge,
  JRDrawer,
  JREmptyState,
} from "@/ui";

const ensureTrailingSlash = (url) => (url.endsWith("/") ? url : `${url}/`);
const stripTrailingSlash = (url) => (url.endsWith("/") ? url.slice(0, -1) : url);
const stripLeadingSlash = (path) => (path.startsWith("/") ? path.slice(1) : path);

const getWsBaseUrl = () => {
  const envUrl = process.env.VUE_APP_WS_URL || process.env.VUE_APP_API_URL;
  if (envUrl) {
    const withoutProtocol = envUrl.replace(/^https?:\/\//i, "").replace(/^wss?:\/\//i, "");
    const base = stripTrailingSlash(withoutProtocol);
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${base}`;
  }
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const port = process.env.NODE_ENV === "development" ? ":8000" : "";
  return `${protocol}//${window.location.hostname}${port}`;
};

const buildWsUrl = (path) => {
  const base = ensureTrailingSlash(getWsBaseUrl());
  const cleanPath = stripLeadingSlash(path);
  return `${base}${cleanPath}`;
};

const isNarrowViewport = () =>
  typeof window !== "undefined" && window.matchMedia("(max-width: 1024px)").matches;

export default {
  name: "WorkOrderViewerView",
  components: {
    JRPage,
    JRPageHeader,
    JRButton,
    JRBadge,
    JRDrawer,
    JREmptyState,
    WorkOrderSidebar,
    WorkOrderViewerTabs,
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const chatStore = useChatStore();
    const { proxy } = getCurrentInstance();

    const workAccount = ref(null);
    const events = ref([]);
    const selectedEvent = ref(null);
    const scheduleEventId = ref(null);
    const isLoading = ref(true);
    const isEventsLoading = ref(false);
    const loadError = ref("");
    const searchQuery = ref("");
    const currentPage = ref(1);
    const totalEventsCount = ref(0);
    const hasPrevious = ref(false);
    const hasNext = ref(false);
    const unreadMap = ref({});
    const ws = ref(null);
    const isMobile = ref(isNarrowViewport());
    const sidebarOpen = ref(!isNarrowViewport());

    const handleResize = () => {
      const narrow = isNarrowViewport();
      if (isMobile.value !== narrow) {
        isMobile.value = narrow;
        sidebarOpen.value = !narrow;
      }
    };

    const isGeneralMode = computed(() => !route.params.id);

    const workAccountId = computed(() => {
      const raw = route.params.id;
      const parsed = Number(raw);
      return Number.isFinite(parsed) ? parsed : null;
    });

    const effectiveWorkAccountId = computed(() => {
      if (workAccountId.value) return workAccountId.value;
      if (workAccount.value?.id) return workAccount.value.id;
      if (selectedEvent.value?.work_account) return selectedEvent.value.work_account;
      return null;
    });

    const initialTab = computed(() => {
      const tab = route.query.tab;
      return WORK_ORDER_VIEWER_TAB_IDS.includes(tab) ? tab : "chat";
    });

    const workAccountSubtitle = computed(() => {
      if (!workAccount.value) return "";
      const parts = [
        workAccount.value.builder_name,
        workAccount.value.job_name,
        workAccount.value.lot ? `Lot ${workAccount.value.lot}` : null,
        workAccount.value.address,
      ].filter(Boolean);
      return parts.join(" · ");
    });

    const displayHeaderTitle = computed(() => {
      if (workAccount.value?.title) {
        return workAccount.value.title;
      }
      if (selectedEvent.value?.title) {
        return selectedEvent.value.title;
      }
      return "Work Order Viewer";
    });

    const displayHeaderSubtitle = computed(() => {
      if (workAccountSubtitle.value) {
        return workAccountSubtitle.value;
      }
      if (selectedEvent.value) {
        const parts = [
          selectedEvent.value.crew_title,
          selectedEvent.value.crew_category,
          selectedEvent.value.date,
        ].filter(Boolean);
        return parts.join(" · ");
      }
      return "Browse and collaborate on work orders";
    });

    /** Supervisor: miembros (Crew Members) de las cuadrillas con la comunidad asignada (Assigned Jobs). */
    const supervisorLabel = computed(() => {
      return (
        workAccount.value?.supervisor ||
        selectedEvent.value?.supervisor ||
        workAccount.value?.area_manager ||
        ""
      );
    });

    const headerMetaItems = computed(() => {
      const wa = workAccount.value;
      const ev = selectedEvent.value;
      const items = [
        { label: "Supervisor", value: supervisorLabel.value },
        { label: "Builder", value: wa?.builder_name || ev?.builder_name },
        { label: "House Model", value: wa?.house_model_name || ev?.house_model_name },
        { label: "Community", value: wa?.job_name || ev?.job_name },
        { label: "Address", value: wa?.address || ev?.address },
        {
          label: "Default Price Type",
          value: wa?.default_price_type_name || ev?.default_price_type_name || null,
        },
      ];
      return items.filter((item) => item.value);
    });

    const ordersBadgeCount = computed(() => {
      if (isGeneralMode.value && totalEventsCount.value > 0) {
        return totalEventsCount.value;
      }
      return events.value.length || 0;
    });

    const canEdit = computed(() =>
      proxy?.hasPermission?.("apptransactions.change_workaccount")
    );

    const toggleSidebar = () => {
      sidebarOpen.value = !sidebarOpen.value;
    };

    const onSidebarVisible = (visible) => {
      sidebarOpen.value = visible;
    };

    const closeSidebarIfNarrow = () => {
      if (isNarrowViewport()) {
        sidebarOpen.value = false;
      }
    };

    const loadUnreadCounts = async () => {
      try {
        const res = await axios.get("/api/unread-chat-counts/");
        if (res.data && typeof res.data === "object") {
          unreadMap.value = { ...res.data };
        }
      } catch (err) {
        console.warn("Could not load unread chat counts:", err);
      }
    };

    const loadWorkAccountData = async () => {
      if (!workAccountId.value) {
        workAccount.value = null;
        return;
      }
      try {
        const { data } = await axios.get(
          `/api/work-accounts/${workAccountId.value}/`
        );
        workAccount.value = data;
      } catch (err) {
        console.error("Failed to load work account", err);
        workAccount.value = null;
        if (err?.response?.status === 404) {
          loadError.value = "The requested work account does not exist or you do not have access.";
        } else if (err?.response?.status === 403) {
          loadError.value = "You do not have permission to view this work account.";
        } else {
          loadError.value = "Could not load this work account. Please try again.";
        }
      }
    };

    const loadEvents = async (page = 1) => {
      isEventsLoading.value = true;
      try {
        let url = `/api/my-events/?page=${page}`;
        if (workAccountId.value) {
          url += `&work_account=${workAccountId.value}`;
        }
        if (searchQuery.value.trim()) {
          url += `&search=${encodeURIComponent(searchQuery.value.trim())}`;
        }

        const res = await axios.get(url);
        const data = res.data;
        const list = Array.isArray(data?.results) ? data.results : Array.isArray(data) ? data : [];
        events.value = list;
        totalEventsCount.value = data?.count || list.length;
        hasPrevious.value = Boolean(data?.previous);
        hasNext.value = Boolean(data?.next);
        currentPage.value = page;

        // Auto-select event
        const targetEventId = Number(route.query.event);
        if (targetEventId) {
          const match = list.find((e) => e.id === targetEventId);
          if (match) {
            selectedEvent.value = match;
            scheduleEventId.value = match.id;
          } else if (list.length > 0) {
            selectedEvent.value = list[0];
            scheduleEventId.value = list[0].id;
          }
        } else if (list.length > 0) {
          selectedEvent.value = list[0];
          scheduleEventId.value = list[0].id;
        } else if (workAccountId.value) {
          // Fallback to resolver
          scheduleEventId.value = await resolveScheduleEventForWorkAccount(
            workAccountId.value,
            workAccount.value?.title || ""
          );
        }

        // If in general mode and we selected an event with work_account, load WA details
        if (isGeneralMode.value && selectedEvent.value?.work_account) {
          loadAccountForEvent(selectedEvent.value.work_account);
        }
      } catch (err) {
        console.error("Failed to load events list", err);
        events.value = [];
      } finally {
        isEventsLoading.value = false;
      }
    };

    const loadAccountForEvent = async (waId) => {
      if (!waId) return;
      if (workAccount.value && workAccount.value.id === waId) return;
      try {
        const { data } = await axios.get(`/api/work-accounts/${waId}/`);
        workAccount.value = data;
      } catch (e) {
        console.warn("Could not load associated work account:", e);
      }
    };

    const handleSelectEvent = (event) => {
      if (!event) return;
      selectedEvent.value = event;
      scheduleEventId.value = event.id;

      // Mark as read
      axios.post(`/api/mark-chat-read/${event.id}/`).catch(() => {});
      unreadMap.value[event.id] = 0;
      chatStore.markEventAsRead(event.id);

      // Keep tab query parameter intact, update event parameter
      router.replace({
        query: {
          ...route.query,
          event: event.id,
        },
      });

      if (isGeneralMode.value && event.work_account) {
        loadAccountForEvent(event.work_account);
      }

      // Offcanvas: close on mobile after selection; keep open on desktop
      if (isMobile.value) {
        sidebarOpen.value = false;
      }
    };

    const handleSearch = (term) => {
      searchQuery.value = term;
      loadEvents(1);
    };

    const handlePrevPage = () => {
      if (hasPrevious.value && currentPage.value > 1) {
        loadEvents(currentPage.value - 1);
      }
    };

    const handleNextPage = () => {
      if (hasNext.value) {
        loadEvents(currentPage.value + 1);
      }
    };

    const connectWebSocket = async () => {
      const token = localStorage.getItem("authToken");
      if (!token) return;

      try {
        const res = await axios.get("/api/user_detail/");
        const userId = res.data?.id;
        if (!userId) return;

        ws.value = new WebSocket(buildWsUrl(`ws/schedule/unread/user/${userId}/`));

        ws.value.onmessage = (msgEvent) => {
          try {
            const data = JSON.parse(msgEvent.data);
            if (data.type === "unread.updated") {
              const { event_id, count } = data;
              if (scheduleEventId.value === event_id) {
                axios.post(`/api/mark-chat-read/${event_id}/`).catch(() => {});
                unreadMap.value[event_id] = 0;
              } else {
                unreadMap.value[event_id] = count;
              }
            }
          } catch (e) {
            console.warn("[WS] Error parsing message:", e);
          }
        };
      } catch (e) {
        console.warn("[WS] Could not initialize unread counter:", e);
      }
    };

    const initView = async () => {
      isLoading.value = true;
      loadError.value = "";

      if (workAccountId.value) {
        await loadWorkAccountData();
      }

      await Promise.all([loadEvents(1), loadUnreadCounts()]);
      isLoading.value = false;
      connectWebSocket();
    };

    const goToList = () => {
      router.push({ name: "work-accounts" });
    };

    const goToEdit = () => {
      if (effectiveWorkAccountId.value) {
        router.push({
          name: "work-accounts-form",
          query: { id: effectiveWorkAccountId.value },
        });
      }
    };

    onMounted(() => {
      initView();
      if (typeof window !== "undefined") {
        window.addEventListener("resize", handleResize);
      }
    });

    onBeforeUnmount(() => {
      if (ws.value) {
        ws.value.close();
      }
      if (typeof window !== "undefined") {
        window.removeEventListener("resize", handleResize);
      }
    });

    watch(workAccountId, () => {
      initView();
    });

    return {
      workAccount,
      events,
      selectedEvent,
      scheduleEventId,
      isLoading,
      isEventsLoading,
      loadError,
      initialTab,
      isGeneralMode,
      effectiveWorkAccountId,
      workAccountId,
      workAccountSubtitle,
      displayHeaderTitle,
      displayHeaderSubtitle,
      headerMetaItems,
      ordersBadgeCount,
      sidebarOpen,
      isMobile,
      canEdit,
      totalEventsCount,
      hasPrevious,
      hasNext,
      currentPage,
      unreadMap,
      goToList,
      goToEdit,
      toggleSidebar,
      onSidebarVisible,
      handleSelectEvent,
      handleSearch,
      handlePrevPage,
      handleNextPage,
    };
  },
};
</script>

<style scoped>
.jr-wov__loading {
  padding: 2rem 0;
  color: var(--color-jr-muted, #4b5563);
}

.jr-wov__header {
  margin-bottom: 1rem;
  padding: 1rem 1.25rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-panel, 0.75rem);
  background: var(--color-jr-surface, #ffffff);
}

.jr-wov__eyebrow {
  margin: 0 0 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-jr-muted, #4b5563);
}

.jr-wov__header-actions {
  flex-shrink: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.jr-wov__orders-badge {
  margin-left: 0.35rem;
}

.jr-wov__meta {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(9.5rem, 1fr));
  gap: 0.625rem 1rem;
  margin: 0.75rem 0 0;
}

.jr-wov__meta-item {
  min-width: 0;
}

.jr-wov__meta-label {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  color: var(--color-jr-muted, #4b5563);
}

.jr-wov__meta-value {
  margin: 0.125rem 0 0;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-jr-text, #111827);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.jr-wov__layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 22.5rem;
  gap: 1rem;
  align-items: start;
}

.jr-wov__layout--sidebar-collapsed {
  grid-template-columns: minmax(0, 1fr);
}

.jr-wov__main-col {
  min-width: 0;
}

.jr-wov__sidebar-col {
  min-width: 0;
  position: sticky;
  top: 1rem;
}

@media (max-width: 1024px) {
  .jr-wov__layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .jr-wov__header {
    align-items: stretch;
  }

  .jr-wov__meta {
    grid-template-columns: repeat(auto-fill, minmax(8rem, 1fr));
  }
}
</style>

<style>
/* Drawer portals to body — match catalog drawer width pattern */
.p-drawer.jr-wov__drawer {
  width: min(24rem, 100vw);
}

.p-drawer.jr-wov__drawer .p-drawer-content {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 0 0.75rem 0.75rem;
}

.p-drawer.jr-wov__drawer .jr-wov-sidebar {
  flex: 1;
  min-height: 0;
  border: none;
  border-radius: 0;
}

.p-drawer.jr-wov__drawer .jr-wov-sidebar__list {
  max-height: none;
}

.p-drawer.jr-wov__drawer .p-drawer-header {
  padding-bottom: 0;
  min-height: 2.5rem;
}
</style>
