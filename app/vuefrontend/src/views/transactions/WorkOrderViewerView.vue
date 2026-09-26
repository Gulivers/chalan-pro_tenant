<template>
  <JRPage>
    <div
      v-if="isLoading"
      class="jr-wov__loading"
      role="status"
      aria-live="polite">
      <div class="jr-wov__loading-spinner" aria-hidden="true"></div>
      <p class="jr-wov__loading-text">Loading work account…</p>
    </div>

    <template v-else-if="loadError">
      <JRPageHeader title="Work Order Viewer" />
      <JREmptyState title="Work account not found" :description="loadError">
        <JRButton type="button" variant="ghost" size="sm" @click="goToList">
          <svg
            class="jr-wov__btn-icon"
            width="14"
            height="14"
            viewBox="0 0 16 16"
            fill="none"
            stroke="currentColor"
            stroke-width="1.75"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true">
            <path d="M10 12L6 8l4-4" />
          </svg>
          Back to Work Accounts
        </JRButton>
      </JREmptyState>
    </template>

    <template v-else>
      <!-- Page Header (reactive to selected Work Order) -->
      <header class="jr-wov__header">
        <div class="jr-wov__header-main">
          <div class="jr-wov__header-text">
            <span class="jr-wov__label">
              {{
                isGeneralMode && !workAccount ? "Operations" : "Work Account"
              }}
            </span>
            <h1 class="jr-wov__title">{{ displayHeaderTitle }}</h1>
            <p
              v-if="!headerMetaItems.length && displayHeaderSubtitle"
              class="jr-wov__desc">
              {{ displayHeaderSubtitle }}
            </p>
          </div>

          <div class="jr-wov__header-actions">
            <JRButton
              type="button"
              variant="ghost"
              size="sm"
              class="jr-wov__back-btn"
              @click="goToList">
              <svg
                class="jr-wov__btn-icon"
                width="20"
                height="20"
                viewBox="0 0 16 16"
                fill="none"
                stroke="currentColor"
                stroke-width="1.75"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true">
                <path d="M10 12L6 8l4-4" />
              </svg>
              Back to list
            </JRButton>
            <JRButton
              v-if="canEdit && effectiveWorkAccountId"
              type="button"
              variant="secondary"
              size="sm"
              @click="goToEdit">
              Edit
            </JRButton>
          </div>
        </div>

        <div class="jr-wov__meta-row">
          <dl v-if="headerMetaItems.length" class="jr-wov__meta">
            <div
              v-for="item in headerMetaItems"
              :key="item.label"
              class="jr-wov__meta-item">
              <dt class="jr-wov__meta-label">{{ item.label }}</dt>
              <dd class="jr-wov__meta-value" :title="item.value">
                {{ item.value }}
              </dd>
            </div>
          </dl>
          <div class="jr-wov__meta-actions">
            <JRButton
              type="button"
              :variant="sidebarOpen ? 'primary' : 'secondary'"
              size="sm"
              :aria-expanded="sidebarOpen ? 'true' : 'false'"
              :aria-controls="
                isMobile ? 'jr-wov-orders-drawer' : 'jr-wov-orders-sidebar'
              "
              @click="toggleSidebar">
              <svg
                class="jr-wov__btn-icon jr-wov__btn-icon--sidebar"
                width="20"
                height="20"
                viewBox="0 0 16 16"
                fill="none"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true">
                <rect x="1.75" y="2" width="12.5" height="12" rx="0" />
                <line x1="10.5" y1="2" x2="10.5" y2="14" />
                <path
                  d="M10.5 2H14.25V14H10.5Z"
                  :fill="sidebarOpen ? 'currentColor' : 'transparent'"
                  :opacity="sidebarOpen ? '0.35' : '0'"
                  stroke="none" />
              </svg>
              Work Orders
              <JRBadge
                v-if="ordersBadgeCount"
                class="jr-wov__orders-badge"
                :value="ordersBadgeCount"
                :severity="sidebarOpen ? 'secondary' : 'info'" />
            </JRButton>
          </div>
        </div>
      </header>

      <!-- 2-Column Responsive Layout (desktop: tabs left, sidebar right; mobile: tabs full width) -->
      <div
        class="jr-wov__layout"
        :class="{
          'jr-wov__layout--sidebar-collapsed': !sidebarOpen || isMobile,
        }">
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
            :is-general-mode="browseAllWorkOrders"
            :work-account-filter-active="workAccountFilterActive"
            :unread-map="unreadMap"
            @select-event="handleSelectEvent"
            @search="handleSearch"
            @prev-page="handlePrevPage"
            @next-page="handleNextPage"
            @clear-work-account-filter="clearWorkAccountFilter" />
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
        header="Work Orders"
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
          :is-general-mode="browseAllWorkOrders"
          :work-account-filter-active="workAccountFilterActive"
          :unread-map="unreadMap"
          @select-event="handleSelectEvent"
          @search="handleSearch"
          @prev-page="handlePrevPage"
          @next-page="handleNextPage"
          @clear-work-account-filter="clearWorkAccountFilter" />
      </JRDrawer>
    </template>
  </JRPage>
</template>

<script>
import { getAccessToken } from '@/auth/tokenHelpers';
import {
  computed,
  getCurrentInstance,
  onBeforeUnmount,
  onMounted,
  ref,
  watch,
} from "vue";
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
const stripTrailingSlash = (url) =>
  url.endsWith("/") ? url.slice(0, -1) : url;
const stripLeadingSlash = (path) =>
  path.startsWith("/") ? path.slice(1) : path;

const getWsBaseUrl = () => {
  const envUrl = process.env.VUE_APP_WS_URL || process.env.VUE_APP_API_URL;
  if (envUrl) {
    const withoutProtocol = envUrl
      .replace(/^https?:\/\//i, "")
      .replace(/^wss?:\/\//i, "");
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
  typeof window !== "undefined" &&
  window.matchMedia("(max-width: 1024px)").matches;

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
    /** When true on a WA route, list all work orders (like /viewer). */
    const listAllWorkOrders = ref(false);

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

    const workAccountFilterActive = computed(
      () => Boolean(workAccountId.value) && !listAllWorkOrders.value
    );

    const browseAllWorkOrders = computed(
      () => isGeneralMode.value || listAllWorkOrders.value
    );

    const effectiveWorkAccountId = computed(() => {
      // En el listado general, el evento elegido trae su work account al instante.
      // No esperar a loadAccountForEvent: si no, Missing Material pide con la cuenta anterior.
      if (browseAllWorkOrders.value && selectedEvent.value?.work_account) {
        return Number(selectedEvent.value.work_account);
      }
      if (workAccountId.value) return workAccountId.value;
      if (workAccount.value?.id) return workAccount.value.id;
      if (selectedEvent.value?.work_account)
        return Number(selectedEvent.value.work_account);
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
      const addr = (wa?.address || ev?.address || "").trim();
      const title = displayHeaderTitle.value?.trim() || "";
      const isAddrRedundant =
        addr && title && addr.toLowerCase() === title.toLowerCase();

      const items = [
        { label: "Area Supervisor", value: supervisorLabel.value },
        { label: "Builder", value: wa?.builder_name || ev?.builder_name },
        { label: "Community", value: wa?.job_name || ev?.job_name },
        { label: "Lot", value: wa?.lot ? `Lot ${wa.lot}` : null },
        {
          label: "House Model",
          value: wa?.house_model_name || ev?.house_model_name,
        },
        { label: "Address", value: isAddrRedundant ? null : addr },
        {
          label: "Default Price Type",
          value:
            wa?.default_price_type_name || ev?.default_price_type_name || null,
        },
      ];
      return items.filter((item) => item.value);
    });

    const ordersBadgeCount = computed(() => {
      if (browseAllWorkOrders.value && totalEventsCount.value > 0) {
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
          loadError.value =
            "The requested work account does not exist or you do not have access.";
        } else if (err?.response?.status === 403) {
          loadError.value =
            "You do not have permission to view this work account.";
        } else {
          loadError.value =
            "Could not load this work account. Please try again.";
        }
      }
    };

    const loadEvents = async (page = 1) => {
      isEventsLoading.value = true;
      try {
        let url = `/api/my-events/?page=${page}`;
        if (workAccountFilterActive.value) {
          url += `&work_account=${workAccountId.value}`;
        }
        if (searchQuery.value.trim()) {
          url += `&search=${encodeURIComponent(searchQuery.value.trim())}`;
        }

        const res = await axios.get(url);
        const data = res.data;
        const list = Array.isArray(data?.results)
          ? data.results
          : Array.isArray(data)
          ? data
          : [];
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
        } else if (workAccountId.value && workAccountFilterActive.value) {
          // Fallback to resolver
          scheduleEventId.value = await resolveScheduleEventForWorkAccount(
            workAccountId.value,
            workAccount.value?.title || ""
          );
        }

        // When browsing all orders, load WA details for the selected event
        if (browseAllWorkOrders.value && selectedEvent.value?.work_account) {
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

      if (browseAllWorkOrders.value && event.work_account) {
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

    const clearWorkAccountFilter = () => {
      if (!workAccountId.value) return;
      listAllWorkOrders.value = true;
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
      const token = getAccessToken();
      if (!token) return;

      try {
        const res = await axios.get("/api/auth/me/");
        const userId = res.data?.id;
        if (!userId) return;

        ws.value = new WebSocket(
          buildWsUrl(`ws/schedule/unread/user/${userId}/`)
        );

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
      listAllWorkOrders.value = false;
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
      browseAllWorkOrders,
      workAccountFilterActive,
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
      clearWorkAccountFilter,
    };
  },
};
</script>

<style scoped>
.jr-wov__loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 4rem 1rem;
  text-align: center;
}

.jr-wov__loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2.5px solid var(--color-jr-border, #e5e7eb);
  border-top-color: var(--color-jr-primary, #2563eb);
  border-radius: 50%;
  animation: jr-wov-spin 0.7s linear infinite;
}

.jr-wov__loading-text {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-jr-muted, #4b5563);
}

@keyframes jr-wov-spin {
  to {
    transform: rotate(360deg);
  }
}

.jr-wov__header {
  margin-bottom: 1rem;
  padding: 1.125rem 1.25rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-control, 0);
  background: var(--color-jr-surface, #ffffff);
}

.jr-wov__header-main {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

@media (min-width: 768px) {
  .jr-wov__header-main {
    flex-direction: row;
    align-items: flex-start;
    justify-content: space-between;
    gap: 1.25rem;
  }
}

.jr-wov__header-text {
  min-width: 0;
  flex: 1;
}

.jr-wov__label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-jr-label, #4b5563);
  margin-bottom: 0.25rem;
}

.jr-wov__title {
  margin: 0;
  font-size: 1.3125rem;
  font-weight: 600;
  line-height: 1.25;
  color: var(--color-jr-text, #111827);
  letter-spacing: -0.01em;
  word-break: break-word;
}

.jr-wov__desc {
  margin: 0.35rem 0 0;
  font-size: 0.875rem;
  font-weight: 400;
  color: var(--color-jr-muted, #4b5563);
}

.jr-wov__header-actions {
  flex-shrink: 0;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
}

.jr-wov__btn-icon {
  display: inline-block;
  vertical-align: middle;
  margin-right: 0.35rem;
  flex-shrink: 0;
}

.jr-wov__orders-badge {
  margin-left: 0.375rem;
}

.jr-wov__meta-actions :deep(.p-button-primary) .jr-wov__orders-badge {
  background: rgba(255, 255, 255, 0.22);
  color: #ffffff;
}

.jr-wov__meta-row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  justify-content: space-between;
  gap: 0.75rem 1rem;
  margin-top: 0.875rem;
  padding-top: 0.875rem;
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
}

.jr-wov__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 0.75rem 1.75rem;
  margin: 0;
  flex: 1 1 12rem;
  min-width: 0;
}

.jr-wov__meta-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex: 0 0 auto;
  margin-left: auto;
}

.jr-wov__meta-item {
  display: flex;
  flex-direction: column;
  min-width: 7.5rem;
}

.jr-wov__meta-label {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-jr-muted, #4b5563);
}

.jr-wov__meta-value {
  margin: 0.15rem 0 0;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-jr-text, #111827);
  line-height: 1.35;
  word-break: break-word;
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
  top: calc(var(--jr-shell-topbar, 3rem) + 1rem);
  max-height: calc(100vh - var(--jr-shell-topbar, 3rem) - 2rem);
  display: flex;
  flex-direction: column;
}

.jr-wov__sidebar-col :deep(.jr-wov-sidebar) {
  height: 100%;
}

@media (max-width: 1024px) {
  .jr-wov__layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .jr-wov__meta {
    gap: 0.625rem 1.25rem;
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
  padding: 0.75rem 1rem 0.25rem;
  min-height: 2.75rem;
}

.p-drawer.jr-wov__drawer .p-drawer-title {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-text, #111827);
}
</style>
