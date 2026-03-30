<template>
  <div class="work-account-discussion-container pt-0">
    <div class="mb-1">
      <div class="border rounded shadow-sm py-1 px-2 bg-light mb-1">
        <h4 class="text-center mb-0 text-warning">
          📋 Work Account:
          <span class="text-primary">
            {{ event?.title || "Unknown Title" }}
          </span>
        </h4>
      </div>
    </div>

    <div v-if="event && event.id" class="card px-3 py-2.5">
      <BNav tabs class="card-header-tabs">
        <BNavItem :active="activeTab === 'chat'" @click="activeTab = 'chat'">
          💬 Chat for Job
        </BNavItem>
        <BNavItem :active="activeTab === 'notes'" @click="activeTab = 'notes'">
          📝 Notes
        </BNavItem>
        <BNavItem
          :active="activeTab === 'folder'"
          @click="activeTab = 'folder'">
          📁 Folder
        </BNavItem>
        <BNavItem
          :active="activeTab === 'contracts'"
          @click="activeTab = 'contracts'">
          📜 Contracts
        </BNavItem>

        <BNavItem
          :active="activeTab === 'transactions'"
          @click="activeTab = 'transactions'">
          💰 Transactions
        </BNavItem>
      </BNav>

      <div class="card-body px-1">
        <!-- Chat Tab (default) -->
        <div v-show="activeTab === 'chat'" class="tab-content-item">
          <ScheduleHouseChatComponent :eventId="event.id" />
        </div>

        <!-- Notes Tab -->
        <div v-show="activeTab === 'notes'" class="tab-content-item">
          <ScheduleHouseNotesComponent :eventId="event.id" />
        </div>

        <!-- Folder Tab -->
        <div v-show="activeTab === 'folder'" class="tab-content-item">
          <EventImageAdmin :eventId="event.id" />
        </div>

        <!-- Contracts Tab -->
        <div v-show="activeTab === 'contracts'" class="tab-content-item">
          <ScheduleHouseContractsComponent :eventId="event.id" />
        </div>

        <!-- Transactions Tab -->
        <div v-show="activeTab === 'transactions'" class="tab-content-item">
          <ScheduleHouseTransactionsComponent :eventId="event.id" />
        </div>
      </div>
    </div>

    <div v-else class="text-center text-danger p-4">
      <p>No event data available.</p>
    </div>
  </div>
</template>

<script>
import { BNav, BNavItem } from "bootstrap-vue-next";
import ScheduleHouseNotesComponent from "./ScheduleHouseNotesComponent.vue";
import ScheduleHouseChatComponent from "./ScheduleHouseChatComponent.vue";
import ScheduleHouseContractsComponent from "./ScheduleHouseContractsComponent.vue";
import EventImageAdmin from "./EventImageAdmin.vue";
import ScheduleHouseTransactionsComponent from "./ScheduleHouseTransactionsComponent.vue";

export default {
  name: "ScheduleHouseDiscussion",
  components: {
    BNav,
    BNavItem,
    ScheduleHouseNotesComponent,
    ScheduleHouseChatComponent,
    ScheduleHouseContractsComponent,
    EventImageAdmin,
    ScheduleHouseTransactionsComponent,
  },
  props: {
    event: Object, // Event object received from ScheduleEventModal
  },
  data() {
    return {
      activeTab: "chat", // Default tab
    };
  },
  watch: {
    event: {
      immediate: true,
      handler(newEvent) {
        console.log(
          "Received event prop in ScheduleHouseDiscussion:",
          newEvent
        );
      },
    },
  },
};
</script>

<style scoped>
.work-account-discussion-container {
  padding: 1rem;
}

.card {
  border: 0.5px solid #dee2e6;
  border-radius: 0.5rem;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.card-header-tabs {
  border-bottom: 2px solid #dee2e6;
  background-color: #f8f9fa;
  padding: 0;
}

.card-body {
  min-height: 500px;
  padding: 1rem;
  background-color: #fff;
}

.tab-content-item {
  animation: fadeIn 0.3s ease-in;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Estilos para BNav tabs de bootstrap-vue-next */
:deep(.nav-tabs) {
  border-bottom: 2px solid #dee2e6;
  margin-bottom: 0;
}

:deep(.nav-item) {
  margin-bottom: -2px;
}

:deep(.nav-item .nav-link) {
  color: #495057;
  border: none;
  border-bottom: 3px solid transparent;
  padding: 0.5rem 1rem;
  transition: all 0.2s ease;
  background-color: transparent;
  cursor: pointer;
}

:deep(.nav-item .nav-link:hover) {
  border-bottom-color: #0d6efd;
  color: #0d6efd;
  background-color: rgba(13, 110, 253, 0.05);
}

:deep(.nav-item .nav-link.active) {
  color: #0d6efd;
  background-color: transparent;
  border-bottom-color: #0d6efd;
  font-weight: 600;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .work-account-discussion-container {
    padding: 0.5rem;
  }

  .card-body {
    padding: 1rem;
    min-height: 400px;
  }

  :deep(.nav-item .nav-link) {
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
  }
}
</style>
