<template>
  <JRPage>
    <div
      v-if="isLoading"
      class="jr-wov__loading"
      role="status"
      aria-live="polite">
      <div class="jr-wov__loading-spinner" aria-hidden="true"></div>
      <p class="jr-wov__loading-text">{{ $t("workOrderViewer.loading") }}</p>
    </div>

    <template v-else-if="loadError">
      <JRPageHeader :title="$t('workOrderViewer.title')" />
      <JREmptyState
        :title="$t('workOrderViewer.notFound')"
        :description="loadError">
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
          {{ $t("workOrderViewer.backToWorkAccounts") }}
        </JRButton>
      </JREmptyState>
    </template>

    <template v-else>
      <nav
        v-if="breadcrumbItems.length"
        class="jr-wov__crumb"
        :aria-label="$t('workOrderViewer.crumbWorkAccounts')">
        <template
          v-for="(item, index) in breadcrumbItems"
          :key="`${item.label}-${index}`">
          <RouterLink
            v-if="item.to"
            class="jr-wov__crumb-link"
            :to="item.to">
            {{ item.label }}
          </RouterLink>
          <span v-else class="jr-wov__crumb-current">{{ item.label }}</span>
          <span
            v-if="index < breadcrumbItems.length - 1"
            class="jr-wov__crumb-sep"
            aria-hidden="true">
            /
          </span>
        </template>
      </nav>

      <!--
        Desktop: sidebar aligns with header top (taller orders list).
        Left column = WA head + tabs; right = Work Orders rail.
      -->
      <div
        class="jr-wov__layout"
        :class="{
          'jr-wov__layout--sidebar-collapsed': !sidebarOpen || isMobile,
        }">
        <div class="jr-wov__main-col">
          <header class="jr-wov__header">
            <div class="jr-wov__header-main">
              <div class="jr-wov__header-text">
                <span class="jr-wov__label">
                  {{
                    isGeneralMode && !workAccount
                      ? $t("workOrderViewer.operations")
                      : $t("workOrderViewer.workAccount")
                  }}
                </span>
                <h1 class="jr-wov__title">{{ displayHeaderTitle }}</h1>

                <div
                  v-if="activeOrderChip"
                  class="jr-wov__active-order"
                  role="status"
                  :aria-label="$t('workOrderViewer.activeOrder')">
                  <span class="jr-wov__active-order-label">
                    {{ $t("workOrderViewer.activeOrder") }}
                  </span>
                  <span class="jr-wov__active-order-id">
                    {{
                      $t("workOrderViewer.orderChip", {
                        id: activeOrderChip.id,
                      })
                    }}
                  </span>
                  <template v-if="activeOrderChip.phase">
                    <span class="jr-wov__active-order-sep" aria-hidden="true"
                      >·</span
                    >
                    <JRBadge :value="activeOrderChip.phase" severity="info" />
                  </template>
                  <template v-if="activeOrderChip.crew">
                    <span class="jr-wov__active-order-sep" aria-hidden="true"
                      >·</span
                    >
                    <strong>{{ activeOrderChip.crew }}</strong>
                  </template>
                  <template v-if="activeOrderChip.date">
                    <span class="jr-wov__active-order-sep" aria-hidden="true"
                      >·</span
                    >
                    <span>{{ activeOrderChip.date }}</span>
                  </template>
                  <template v-if="activeOrderChip.status">
                    <span class="jr-wov__active-order-sep" aria-hidden="true"
                      >·</span
                    >
                    <JRBadge
                      :value="activeOrderChip.status"
                      :severity="activeOrderChip.statusSeverity" />
                  </template>
                </div>

                <p
                  v-else-if="!headerMetaItems.length && displayHeaderSubtitle"
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
                  {{ $t("common.backToList") }}
                </JRButton>
                <JRButton
                  v-if="canEdit && effectiveWorkAccountId"
                  type="button"
                  variant="secondary"
                  size="sm"
                  @click="goToEdit">
                  {{ $t("common.edit") }}
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
                  class="jr-wov__orders-toggle"
                  :variant="sidebarOpen ? 'secondary' : 'primary'"
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
                  {{ $t("workOrderViewer.workOrders") }}
                  <JRBadge
                    v-if="ordersBadgeCount"
                    class="jr-wov__orders-badge"
                    :value="ordersBadgeCount"
                    :severity="sidebarOpen ? 'info' : 'secondary'" />
                </JRButton>
              </div>
            </div>

            <WorkAccountProgressSummary
              v-if="effectiveWorkAccountId"
              class="jr-wov__header-progress"
              :work-account-id="effectiveWorkAccountId"
              :refresh-key="rollupRefreshKey" />
          </header>

          <JREmptyState
            v-if="!scheduleEventId"
            :title="$t('workOrderViewer.selectOrderGuideTitle')"
            :description="$t('workOrderViewer.selectOrderGuideDesc')">
            <JRButton
              type="button"
              variant="secondary"
              size="sm"
              @click="sidebarOpen = true">
              {{ $t("workOrderViewer.workOrders") }}
            </JRButton>
          </JREmptyState>
          <WorkOrderViewerTabs
            v-else
            :work-account-id="effectiveWorkAccountId"
            :event-id="scheduleEventId"
            :initial-tab="initialTab"
            @status-changed="onWorkOrderStatusChanged" />
        </div>

        <aside
          v-if="!isMobile && sidebarOpen"
          id="jr-wov-orders-sidebar"
          class="jr-wov__sidebar-col"
          :aria-label="$t('workOrderViewer.workOrders')">
          <WorkOrderSidebar
            v-bind="sidebarBindings"
            @select-event="handleSelectEvent"
            @search="handleSearch"
            @prev-page="handlePrevPage"
            @next-page="handleNextPage"
            @clear-work-account-filter="clearWorkAccountFilter"
            @update:ops-scope="onOpsScope" />
        </aside>
      </div>

      <JRDrawer
        v-if="isMobile"
        id="jr-wov-orders-drawer"
        class="jr-wov__drawer"
        :visible="sidebarOpen"
        position="right"
        :modal="true"
        :dismissable="true"
        :block-scroll="true"
        :header="$t('workOrderViewer.workOrders')"
        @update:visible="onSidebarVisible">
        <WorkOrderSidebar
          v-bind="sidebarBindings"
          @select-event="handleSelectEvent"
          @search="handleSearch"
          @prev-page="handlePrevPage"
          @next-page="handleNextPage"
          @clear-work-account-filter="clearWorkAccountFilter"
          @update:ops-scope="onOpsScope" />
      </JRDrawer>

      <div
        v-if="isMobile"
        class="jr-wov__mobile-sticky"
        :aria-label="$t('workOrderViewer.workOrders')">
        <JRButton
          type="button"
          class="jr-wov__orders-toggle jr-wov__orders-toggle--sticky"
          :variant="sidebarOpen ? 'secondary' : 'primary'"
          size="sm"
          :aria-expanded="sidebarOpen ? 'true' : 'false'"
          aria-controls="jr-wov-orders-drawer"
          @click="toggleSidebar">
          {{ $t("workOrderViewer.workOrders") }}
          <JRBadge
            v-if="ordersBadgeCount"
            class="jr-wov__orders-badge"
            :value="ordersBadgeCount"
            :severity="sidebarOpen ? 'info' : 'secondary'" />
        </JRButton>
      </div>
    </template>
  </JRPage>
</template>

<script>
import { getAccessToken } from '@/auth/tokenHelpers';
import { withWsTicket } from '@/auth/wsTicket';
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
import dayjs from "dayjs";
import WorkOrderSidebar from "@components/work-accounts/WorkOrderSidebar.vue";
import WorkAccountProgressSummary from "@components/work-accounts/WorkAccountProgressSummary.vue";
import WorkOrderViewerTabs from "@components/work-accounts/WorkOrderViewerTabs.vue";
import { useChatStore } from "@/stores/chatStore";
import {
  resolveScheduleEventForWorkAccount,
  WORK_ORDER_VIEWER_TAB_IDS,
} from "@/utils/resolveScheduleEventForWorkAccount";
import {
  pickPreferredWorkOrder,
  resolveOrderQueryId,
} from "@/utils/pickPreferredWorkOrder";
import { trackWov } from "@/utils/wovTelemetry";
import { tStatus } from "@/utils/statusI18n";
import { workOrderStatusSeverity } from "@/utils/workOrderStatus";
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
  const envUrl = import.meta.env.VITE_WS_URL || import.meta.env.VITE_API_URL;
  if (envUrl) {
    const withoutProtocol = envUrl
      .replace(/^https?:\/\//i, "")
      .replace(/^wss?:\/\//i, "");
    const base = stripTrailingSlash(withoutProtocol);
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${protocol}//${base}`;
  }
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  const port = import.meta.env.DEV ? ":8000" : "";
  return `${protocol}//${window.location.hostname}${port}`;
};

const buildWsUrl = (path) => {
  const base = ensureTrailingSlash(getWsBaseUrl());
  const cleanPath = stripLeadingSlash(path);
  return `${base}${cleanPath}`;
};

const isNarrowViewport = () =>
  typeof window !== "undefined" &&
  window.matchMedia("(max-width: 1100px)").matches;

const formatPhaseLabel = (cat, fallbackGeneral) => {
  if (!cat) return String(fallbackGeneral || "").toUpperCase();
  const cleaned = String(cat)
    .replace(/^[\p{Emoji}\s\d]+/u, "")
    .trim();
  if (!cleaned) return String(cat).toUpperCase();
  return cleaned.toUpperCase();
};

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
    WorkAccountProgressSummary,
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
    const searchQuery = ref(
      typeof route.query.q === "string" ? route.query.q : ""
    );
    const currentPage = ref(1);
    const totalEventsCount = ref(0);
    const hasPrevious = ref(false);
    const hasNext = ref(false);
    const unreadMap = ref({});
    const rollupRefreshKey = ref(0);
    const ws = ref(null);
    const isMobile = ref(isNarrowViewport());
    const sidebarOpen = ref(!isNarrowViewport());
    /** When true on a WA route, list all work orders (like /viewer). */
    const listAllWorkOrders = ref(false);
    /** Operations inbox scope: active | leaves | all */
    const opsScope = ref("active");
    const sessionStartedAt = ref(Date.now());
    const firstActionTracked = ref(false);

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

    const t = (key, values) => proxy?.$t?.(key, values) ?? key;

    const workAccountSubtitle = computed(() => {
      if (!workAccount.value) return "";
      const parts = [
        workAccount.value.builder_name,
        workAccount.value.job_name,
        workAccount.value.lot
          ? t("workOrderViewer.lotValue", { lot: workAccount.value.lot })
          : null,
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
      return t("workOrderViewer.title");
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
      return t("workOrderViewer.browseSubtitle");
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
        {
          label: t("workOrderViewer.areaSupervisor"),
          value: supervisorLabel.value,
        },
        {
          label: t("workOrderViewer.builder"),
          value: wa?.builder_name || ev?.builder_name,
        },
        {
          label: t("workOrderViewer.community"),
          value: wa?.job_name || ev?.job_name,
        },
        {
          label: t("workOrderViewer.lot"),
          value: wa?.lot
            ? t("workOrderViewer.lotValue", { lot: wa.lot })
            : null,
        },
        {
          label: t("workOrderViewer.houseModel"),
          value: wa?.house_model_name || ev?.house_model_name,
        },
        {
          label: t("workOrderViewer.address"),
          value: isAddrRedundant ? null : addr,
        },
        {
          label: t("workOrderViewer.defaultPriceType"),
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

    const activeOrderChip = computed(() => {
      const event = selectedEvent.value;
      if (!event?.id) return null;
      const phase = formatPhaseLabel(
        event.phase || event.crew_category,
        t("workOrderViewer.generalCategory")
      );
      const statusCode = event.status_code || event.work_order_status_code;
      const statusName = event.work_order_status_name;
      const status = statusCode || statusName
        ? tStatus(statusCode, statusName)
        : "";
      const dateStr = event.date;
      const d = dateStr ? dayjs(dateStr) : null;
      return {
        id: event.id,
        phase,
        crew: event.crew_title || "",
        date: d?.isValid() ? d.format("MM/DD") : dateStr || "",
        status,
        statusSeverity: workOrderStatusSeverity({
          status_code: statusCode,
          is_terminal: !!event.work_order_status_is_terminal,
        }),
      };
    });

    const breadcrumbItems = computed(() => {
      const items = [
        {
          label: t("workOrderViewer.crumbWorkAccounts"),
          to: { name: "work-accounts" },
        },
      ];
      if (workAccount.value?.title) {
        items.push({
          label: workAccount.value.title,
          to: workAccountId.value
            ? {
                name: "work-order-viewer",
                params: { id: workAccountId.value },
              }
            : null,
        });
      } else if (isGeneralMode.value) {
        items.push({ label: t("workOrderViewer.operations"), to: null });
      }
      if (activeOrderChip.value) {
        items.push({
          label: t("workOrderViewer.crumbOrder", {
            id: activeOrderChip.value.id,
            phase: activeOrderChip.value.phase,
          }),
          to: null,
        });
      }
      return items;
    });

    const sidebarBindings = computed(() => ({
      workAccount: workAccount.value,
      events: events.value,
      selectedEventId: scheduleEventId.value,
      totalCount: totalEventsCount.value,
      loading: isEventsLoading.value,
      hasPrevious: hasPrevious.value,
      hasNext: hasNext.value,
      currentPage: currentPage.value,
      isGeneralMode: browseAllWorkOrders.value,
      workAccountFilterActive: workAccountFilterActive.value,
      opsScope: opsScope.value,
      unreadMap: unreadMap.value,
      // Persist lupa filter across sidebar remount / order switches
      searchQuery: searchQuery.value,
    }));

    const markFirstAction = (action) => {
      if (firstActionTracked.value) return;
      firstActionTracked.value = true;
      trackWov("first_action", {
        action,
        ms: Date.now() - sessionStartedAt.value,
        mode: browseAllWorkOrders.value ? "operations" : "work_account",
      });
    };

    const onWorkOrderStatusChanged = (tracking) => {
      rollupRefreshKey.value += 1;
      if (!tracking) return;
      const patch = {
        work_order_status_code: tracking.status_code ?? null,
        work_order_status_name: tracking.status_name ?? null,
        work_order_status_is_terminal: !!tracking.is_terminal,
      };
      const eventId = tracking.event ?? scheduleEventId.value;
      events.value = events.value.map((event) =>
        event.id === eventId ? { ...event, ...patch } : event
      );
      if (selectedEvent.value?.id === eventId) {
        selectedEvent.value = { ...selectedEvent.value, ...patch };
      }
    };

    const toggleSidebar = () => {
      sidebarOpen.value = !sidebarOpen.value;
      trackWov("toggle_orders", {
        open: sidebarOpen.value,
        mobile: isMobile.value,
      });
    };

    const onSidebarVisible = (visible) => {
      sidebarOpen.value = visible;
    };

    const onOpsScope = (scope) => {
      opsScope.value = scope || "active";
      trackWov("ops_scope", { scope: opsScope.value });
      loadEvents(1);
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
          loadError.value = t("workOrderViewer.loadErrorNotFound");
        } else if (err?.response?.status === 403) {
          loadError.value = t("workOrderViewer.loadErrorForbidden");
        } else {
          loadError.value = t("workOrderViewer.loadErrorGeneric");
        }
      }
    };

    const syncViewerQuery = ({
      orderId = scheduleEventId.value,
      search = searchQuery.value,
    } = {}) => {
      const nextQuery = { ...route.query };
      if (orderId) {
        nextQuery.order = String(orderId);
        delete nextQuery.event;
      } else {
        delete nextQuery.order;
        delete nextQuery.event;
      }
      const term = typeof search === "string" ? search.trim() : "";
      if (term) {
        nextQuery.q = term;
      } else {
        delete nextQuery.q;
      }
      const sameOrder =
        String(route.query.order || route.query.event || "") ===
        String(nextQuery.order || "");
      const sameQ = String(route.query.q || "") === String(nextQuery.q || "");
      if (sameOrder && sameQ) return;
      router.replace({ query: nextQuery }).catch(() => {});
    };

    const applySelectedEvent = (event, { syncQuery = true } = {}) => {
      selectedEvent.value = event || null;
      scheduleEventId.value = event?.id ?? null;
      if (syncQuery) {
        syncViewerQuery({ orderId: event?.id ?? null });
      }
    };

    const loadEvents = async (page = 1) => {
      isEventsLoading.value = true;
      try {
        let url = `/api/my-events/?page=${page}`;
        if (workAccountFilterActive.value) {
          url += `&work_account=${workAccountId.value}`;
        } else if (browseAllWorkOrders.value && opsScope.value !== "all") {
          url += `&scope=${encodeURIComponent(opsScope.value)}`;
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

        const preferredId = resolveOrderQueryId(route.query);
        const preferred = pickPreferredWorkOrder(list, preferredId);

        if (preferred) {
          applySelectedEvent(preferred, {
            syncQuery: preferredId !== preferred.id,
          });
        } else if (workAccountId.value && workAccountFilterActive.value) {
          const resolvedId = await resolveScheduleEventForWorkAccount(
            workAccountId.value,
            workAccount.value?.title || ""
          );
          if (resolvedId) {
            applySelectedEvent({ id: resolvedId }, { syncQuery: true });
          } else {
            applySelectedEvent(null, { syncQuery: false });
          }
        } else {
          applySelectedEvent(null, { syncQuery: false });
        }

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
      const switched =
        selectedEvent.value?.id && selectedEvent.value.id !== event.id;
      applySelectedEvent(event, { syncQuery: true });

      axios.post(`/api/mark-chat-read/${event.id}/`).catch(() => {});
      unreadMap.value[event.id] = 0;
      chatStore.markEventAsRead(event.id);

      if (switched) {
        trackWov("order_change", {
          event_id: event.id,
          work_account_id: event.work_account || effectiveWorkAccountId.value,
        });
      }
      markFirstAction("select_order");

      if (browseAllWorkOrders.value && event.work_account) {
        loadAccountForEvent(event.work_account);
      }

      if (isMobile.value) {
        sidebarOpen.value = false;
      }
    };

    const handleSearch = (term) => {
      searchQuery.value = term;
      // Persist in URL so remounts / order switches keep the lupa filter
      syncViewerQuery({ search: term });
      loadEvents(1);
    };

    const clearWorkAccountFilter = () => {
      if (!workAccountId.value) return;
      listAllWorkOrders.value = true;
      opsScope.value = "active";
      trackWov("show_all", { work_account_id: workAccountId.value });
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
          await withWsTicket(buildWsUrl(`ws/schedule/unread/user/${userId}/`))
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
      sessionStartedAt.value = Date.now();
      firstActionTracked.value = false;
      // Restore lupa filter after remount (router-view keys on fullPath)
      if (typeof route.query.q === "string") {
        searchQuery.value = route.query.q;
      }

      if (workAccountId.value) {
        await loadWorkAccountData();
      }

      await Promise.all([loadEvents(1), loadUnreadCounts()]);
      isLoading.value = false;
      trackWov("view_open", {
        mode: browseAllWorkOrders.value ? "operations" : "work_account",
        work_account_id: workAccountId.value,
        order: resolveOrderQueryId(route.query),
        q: searchQuery.value || null,
      });
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
      activeOrderChip,
      breadcrumbItems,
      sidebarBindings,
      ordersBadgeCount,
      sidebarOpen,
      isMobile,
      canEdit,
      totalEventsCount,
      hasPrevious,
      hasNext,
      currentPage,
      unreadMap,
      rollupRefreshKey,
      onWorkOrderStatusChanged,
      goToList,
      goToEdit,
      toggleSidebar,
      onSidebarVisible,
      onOpsScope,
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

.jr-wov__crumb {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem;
  margin: 0 0 0.65rem;
  font-size: 0.8125rem;
  color: var(--color-jr-muted, #4b5563);
}

.jr-wov__crumb-link {
  color: var(--color-jr-primary, #2563eb);
  text-decoration: none;
  font-weight: 500;
}

.jr-wov__crumb-link:hover {
  text-decoration: underline;
}

.jr-wov__crumb-current {
  color: var(--color-jr-text, #111827);
  font-weight: 500;
}

.jr-wov__crumb-sep {
  color: var(--color-jr-muted, #4b5563);
}

.jr-wov__header {
  margin-bottom: 0;
  padding: 1.125rem 1.25rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-panel, 0.75rem);
  background: var(--color-jr-surface, #ffffff);
}

.jr-wov__active-order {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem 0.45rem;
  margin-top: 0.55rem;
  padding: 0.45rem 0.65rem;
  max-width: 100%;
  background: color-mix(
    in srgb,
    var(--color-jr-primary, #2563eb) 8%,
    var(--color-jr-surface, #ffffff)
  );
  border: 1px solid color-mix(
    in srgb,
    var(--color-jr-primary, #2563eb) 22%,
    var(--color-jr-border, #e5e7eb)
  );
  font-size: 0.8125rem;
  color: var(--color-jr-text, #111827);
}

.jr-wov__active-order-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-jr-primary, #2563eb);
}

.jr-wov__active-order-id {
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.jr-wov__active-order-sep {
  color: var(--color-jr-muted, #4b5563);
}

.jr-wov__header-progress {
  margin-top: 0.85rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
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

.jr-wov__orders-toggle--sticky {
  width: 100%;
  justify-content: center;
}

.jr-wov__mobile-sticky {
  display: flex;
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 30;
  gap: 0.5rem;
  padding: 0.65rem 0.85rem calc(0.65rem + env(safe-area-inset-bottom, 0px));
  background: var(--color-jr-surface, #ffffff);
  border-top: 1px solid var(--color-jr-border, #e5e7eb);
  box-shadow: 0 -8px 24px rgba(15, 23, 42, 0.08);
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
  grid-template-columns: minmax(0, 1fr) minmax(18rem, 22.5rem);
  gap: 1rem;
  align-items: start;
}

.jr-wov__layout--sidebar-collapsed {
  grid-template-columns: minmax(0, 1fr);
}

.jr-wov__main-col {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.jr-wov__sidebar-col {
  min-width: 0;
  position: sticky;
  top: calc(var(--jr-shell-topbar, 3rem) + 1rem);
  /* Full viewport under topbar — rail starts next to WA header */
  height: calc(100vh - var(--jr-shell-topbar, 3rem) - 2rem);
  max-height: calc(100vh - var(--jr-shell-topbar, 3rem) - 2rem);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.jr-wov__sidebar-col :deep(.jr-wov-sidebar) {
  flex: 1 1 auto;
  min-height: 0;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.jr-wov__sidebar-col :deep(.jr-wov-sidebar__list) {
  max-height: none;
  flex: 1 1 auto;
  min-height: 0;
}

@media (max-width: 1100px) {
  .jr-wov__layout {
    grid-template-columns: minmax(0, 1fr);
  }

  .jr-wov__meta {
    gap: 0.625rem 1.25rem;
  }
}

@media (max-width: 800px) {
  .jr-wov__header {
    padding: 0.85rem 0.9rem;
  }

  .jr-wov__meta-row {
    flex-direction: column;
    align-items: stretch;
  }

  .jr-wov__meta-actions {
    margin-left: 0;
    width: 100%;
  }

  .jr-wov__meta-actions :deep(.jr-wov__orders-toggle),
  .jr-wov__meta-actions :deep(.p-button) {
    width: 100%;
    justify-content: center;
  }

  .jr-wov__active-order {
    width: 100%;
  }

  /* Room for sticky mobile orders bar */
  .jr-wov__layout {
    padding-bottom: 4.5rem;
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
