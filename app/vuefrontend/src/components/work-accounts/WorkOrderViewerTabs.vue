<template>
  <div class="jr-wov-tabs">
    <Tabs
      v-model:value="activeTab"
      lazy
      scrollable
      class="jr-wov-tabs__prime"
      @update:value="onTabChange">
      <TabList>
        <Tab
          v-for="tab in visibleTabs"
          :key="tab.id"
          :value="tab.id"
          class="jr-wov-tab">
          <span class="jr-wov-tab__inner">
            <svg
              v-if="tab.id === 'chat'"
              class="jr-wov-tab__icon"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true">
              <path
                fill-rule="evenodd"
                d="M3.5 2A1.5 1.5 0 002 3.5v9A1.5 1.5 0 003.5 14h1.75v3.25a.75.75 0 001.28.53L10.06 14h6.44A1.5 1.5 0 0018 12.5v-9A1.5 1.5 0 0016.5 2h-13zm1.5 4.75a.75.75 0 01.75-.75h8.5a.75.75 0 010 1.5h-8.5a.75.75 0 01-.75-.75zm0 3a.75.75 0 01.75-.75h5.5a.75.75 0 010 1.5h-5.5a.75.75 0 01-.75-.75z"
                clip-rule="evenodd" />
            </svg>
            <svg
              v-else-if="tab.id === 'notes'"
              class="jr-wov-tab__icon"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true">
              <path
                d="M5.433 13.917l1.262-3.155A4 4 0 017.58 9.42l6.92-6.918a2.121 2.121 0 013 3l-6.92 6.918c-.383.383-.84.685-1.343.886l-3.154 1.262a.5.5 0 01-.65-.65z" />
              <path
                d="M3.5 5.75c0-.414.336-.75.75-.75H10a.75.75 0 010 1.5H4.25v10.5h10.5V13a.75.75 0 011.5 0v4.25a.75.75 0 01-.75.75H3.5a.75.75 0 01-.75-.75V5.75z" />
            </svg>
            <svg
              v-else-if="tab.id === 'folder'"
              class="jr-wov-tab__icon"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true">
              <path
                d="M2 4.75C2 3.784 2.784 3 3.75 3h3.586a1.75 1.75 0 011.237.513l1.414 1.414a.25.25 0 00.177.073h6.086c.966 0 1.75.784 1.75 1.75v8.5A1.75 1.75 0 0116.25 17H3.75A1.75 1.75 0 012 15.25V4.75z" />
            </svg>
            <svg
              v-else-if="tab.id === 'contracts'"
              class="jr-wov-tab__icon"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true">
              <path
                fill-rule="evenodd"
                d="M4.5 2A1.5 1.5 0 003 3.5v13A1.5 1.5 0 004.5 18h11a1.5 1.5 0 001.5-1.5V7.621a1.5 1.5 0 00-.44-1.06l-4.12-4.122A1.5 1.5 0 0011.378 2H4.5zm2.25 7a.75.75 0 000 1.5h6.5a.75.75 0 000-1.5h-6.5zm0 3a.75.75 0 000 1.5h6.5a.75.75 0 000-1.5h-6.5zm0 3a.75.75 0 000 1.5h4a.75.75 0 000-1.5h-4z"
                clip-rule="evenodd" />
            </svg>
            <svg
              v-else-if="tab.id === 'transactions'"
              class="jr-wov-tab__icon"
              viewBox="0 0 20 20"
              fill="currentColor"
              aria-hidden="true">
              <path
                fill-rule="evenodd"
                d="M1 4a1 1 0 011-1h16a1 1 0 011 1v2a1 1 0 01-1 1H2a1 1 0 01-1-1V4zm0 6a1 1 0 011-1h16a1 1 0 011 1v6a1 1 0 01-1 1H2a1 1 0 01-1-1v-6zm3 2a1 1 0 000 2h3a1 1 0 000-2H4z"
                clip-rule="evenodd" />
            </svg>
            <span class="jr-wov-tab__label">{{ tab.label }}</span>
          </span>
        </Tab>
      </TabList>
      <TabPanels>
        <TabPanel value="chat">
          <ScheduleHouseChatComponent
            v-if="eventId"
            :key="eventId"
            :event-id="eventId"
            :work-account-id="workAccountId" />
          <JREmptyState
            v-else
            title="Chat unavailable"
            description="This work account has no linked schedule event yet. Create a schedule event to start chatting." />
        </TabPanel>

        <TabPanel value="notes">
          <ScheduleHouseNotesComponent
            v-if="eventId"
            :key="eventId"
            :event-id="eventId"
            :work-account-id="workAccountId" />
          <JREmptyState
            v-else
            title="Notes unavailable"
            description="Notes are tied to a schedule event. Link this work account to a schedule event to add notes." />
        </TabPanel>

        <TabPanel value="folder">
          <EventImageAdmin
            v-if="eventId"
            :key="eventId"
            :event-id="eventId" />
          <JREmptyState
            v-else
            title="Folder unavailable"
            description="Project files are stored per schedule event. Link this work account to a schedule event to upload or view files." />
        </TabPanel>

        <TabPanel value="contracts">
          <ScheduleHouseContractsComponent
            :event-id="eventId"
            :work-account-id="workAccountId" />
        </TabPanel>

        <TabPanel value="transactions">
          <ScheduleHouseTransactionsComponent
            :event-id="eventId"
            :work-account-id="workAccountId" />
        </TabPanel>
      </TabPanels>
    </Tabs>
  </div>
</template>

<script>
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import Tab from "primevue/tab";
import TabList from "primevue/tablist";
import TabPanel from "primevue/tabpanel";
import TabPanels from "primevue/tabpanels";
import Tabs from "primevue/tabs";
import ScheduleHouseChatComponent from "@components/schedule/ScheduleHouseChatComponent.vue";
import ScheduleHouseNotesComponent from "@components/schedule/ScheduleHouseNotesComponent.vue";
import EventImageAdmin from "@components/schedule/EventImageAdmin.vue";
import ScheduleHouseContractsComponent from "@components/schedule/ScheduleHouseContractsComponent.vue";
import ScheduleHouseTransactionsComponent from "@components/schedule/ScheduleHouseTransactionsComponent.vue";
import { JREmptyState } from "@/ui";
import {
  WORK_ORDER_VIEWER_TABS,
  WORK_ORDER_VIEWER_TAB_IDS,
} from "@/utils/resolveScheduleEventForWorkAccount";

export default {
  name: "WorkOrderViewerTabs",
  components: {
    Tabs,
    TabList,
    Tab,
    TabPanels,
    TabPanel,
    ScheduleHouseChatComponent,
    ScheduleHouseNotesComponent,
    EventImageAdmin,
    ScheduleHouseContractsComponent,
    ScheduleHouseTransactionsComponent,
    JREmptyState,
  },
  props: {
    workAccountId: {
      type: Number,
      default: null,
    },
    eventId: {
      type: Number,
      default: null,
    },
    initialTab: {
      type: String,
      default: "chat",
    },
    /** When false (e.g. schedule modal), do not write ?tab= into the route. */
    syncRoute: {
      type: Boolean,
      default: true,
    },
  },
  setup(props) {
    const route = useRoute();
    const router = useRouter();

    const normalizeTab = (tab) =>
      WORK_ORDER_VIEWER_TAB_IDS.includes(tab) ? tab : "chat";

    const activeTab = ref(normalizeTab(props.initialTab || route.query.tab));

    const visibleTabs = computed(() => WORK_ORDER_VIEWER_TABS);

    const syncTabToRoute = (tab) => {
      if (!props.syncRoute) return;
      const nextTab = normalizeTab(tab);
      if (route.query.tab === nextTab) return;
      router.replace({
        name: route.name,
        params: route.params,
        query: { ...route.query, tab: nextTab },
      });
    };

    const onTabChange = (tab) => {
      syncTabToRoute(tab);
    };

    watch(
      () => route.query.tab,
      (tab) => {
        if (!props.syncRoute || !tab) return;
        const normalized = normalizeTab(tab);
        if (normalized !== activeTab.value) {
          activeTab.value = normalized;
        }
      }
    );

    watch(
      () => props.initialTab,
      (tab) => {
        if (!tab) return;
        const normalized = normalizeTab(tab);
        if (normalized !== activeTab.value) {
          activeTab.value = normalized;
        }
      }
    );

    return {
      activeTab,
      visibleTabs,
      onTabChange,
    };
  },
};
</script>

<style scoped>
.jr-wov-tabs {
  border: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface, #fff);
  border-radius: var(--radius-jr-control, 0);
  overflow: hidden;
}

.jr-wov-tabs__prime :deep(.p-tablist-tab-list) {
  background: var(--color-jr-surface-muted, #f9fafb);
  border-bottom: 1px solid var(--color-jr-border, #e5e7eb);
  gap: 0.25rem;
  padding: 0 0.5rem;
}

.jr-wov-tabs__prime :deep(.p-tab) {
  border: none;
  border-bottom: 2px solid transparent;
  background: transparent;
  color: var(--color-jr-muted, #4b5563);
  font-family: var(--font-jr-sans, sans-serif);
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.875rem 1rem;
  transition: color 0.15s ease, background-color 0.15s ease, border-color 0.15s ease;
  cursor: pointer;
}

.jr-wov-tabs__prime :deep(.p-tab:hover) {
  color: var(--color-jr-text, #111827);
  background-color: color-mix(
    in srgb,
    var(--color-jr-primary, #2563eb) 5%,
    transparent
  );
}

.jr-wov-tabs__prime :deep(.p-tab:focus-visible) {
  outline: 2px solid var(--color-jr-primary, #2563eb);
  outline-offset: -2px;
}

.jr-wov-tabs__prime :deep(.p-tab.p-tab-active) {
  color: var(--color-jr-primary, #2563eb);
  font-weight: 600;
  border-bottom-color: var(--color-jr-primary, #2563eb);
  background: transparent;
}

.jr-wov-tabs__prime :deep(.p-tablist-active-bar) {
  height: 2px;
  background-color: var(--color-jr-primary, #2563eb);
}

.jr-wov-tab__inner {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.jr-wov-tab__icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
  color: inherit;
}

.jr-wov-tab__label {
  white-space: nowrap;
}

.jr-wov-tabs__prime :deep(.p-tabpanels) {
  padding: 1.25rem;
  min-height: 28rem;
  background: var(--color-jr-surface, #fff);
}

.jr-wov-tabs__prime :deep(.p-tabpanel) {
  outline: none;
}

.jr-wov-tabs__prime :deep(.jr-toolbar) {
  margin-bottom: 0.75rem;
}

@media (max-width: 768px) {
  .jr-wov-tabs__prime :deep(.p-tab) {
    padding: 0.75rem 0.75rem;
    font-size: 0.8125rem;
  }

  .jr-wov-tabs__prime :deep(.p-tabpanels) {
    padding: 0.75rem;
    min-height: 22rem;
  }
}
</style>
