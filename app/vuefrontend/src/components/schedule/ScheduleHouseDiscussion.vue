<template>
    <div class="work-account-discussion-container">
        <div class="mb-3">
            <h4 class="text-center mb-0" style="color: orange;">
                {{ event?.title || 'Unknown Title' }}
            </h4>
            <p v-if="event?.work_account_title" class="text-center text-muted small mb-0">
                Work Account: {{ event.work_account_title }}
            </p>
        </div>

        <div v-if="event && event.id" class="card">
            <BNav tabs class="card-header-tabs">
                <BNavItem :active="activeTab === 'notes'" @click="activeTab = 'notes'">
                    📝 Notes
                </BNavItem>
                <BNavItem :active="activeTab === 'folder'" @click="activeTab = 'folder'">
                    📁 Folder
                </BNavItem>
                <BNavItem :active="activeTab === 'contracts'" @click="activeTab = 'contracts'">
                    📜 Contracts
                </BNavItem>
                <BNavItem :active="activeTab === 'chat'" @click="activeTab = 'chat'">
                    💬 Chat for Job
                </BNavItem>
                <BNavItem :active="activeTab === 'transactions'" @click="activeTab = 'transactions'">
                    💰 Transactions
                </BNavItem>
            </BNav>

            <div class="card-body">
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

                <!-- Chat Tab -->
                <div v-show="activeTab === 'chat'" class="tab-content-item">
                    <ScheduleHouseChatComponent :eventId="event.id" />
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
import { BNav, BNavItem } from 'bootstrap-vue-next';
import ScheduleHouseNotesComponent from "./ScheduleHouseNotesComponent.vue";
import ScheduleHouseChatComponent from "./ScheduleHouseChatComponent.vue";
import ScheduleHouseContractsComponent from "./ScheduleHouseContractsComponent.vue";
import EventImageAdmin from "./EventImageAdmin.vue";
import ScheduleHouseTransactionsComponent from "./ScheduleHouseTransactionsComponent.vue";

export default {
    name: 'ScheduleHouseDiscussion',
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
            activeTab: 'notes', // Default tab
        };
    },
    watch: {
        event: {
            immediate: true,
            handler(newEvent) {
                console.log("Received event prop in ScheduleHouseDiscussion:", newEvent);
            }
        }
    }
};
</script>

<style scoped>
.work-account-discussion-container {
    padding: 1rem;
}

.card {
    border: 1px solid #dee2e6;
    border-radius: 0.375rem;
}

.card-body {
    min-height: 400px;
    padding: 1.5rem;
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

:deep(.nav-tabs) {
    border-bottom: 2px solid #dee2e6;
}

:deep(.nav-item .nav-link) {
    color: #495057;
    border: none;
    border-bottom: 3px solid transparent;
    padding: 0.75rem 1rem;
    transition: all 0.2s;
}

:deep(.nav-item .nav-link:hover) {
    border-bottom-color: #0d6efd;
    color: #0d6efd;
}

:deep(.nav-item .nav-link.active) {
    color: #0d6efd;
    background-color: transparent;
    border-bottom-color: #0d6efd;
    font-weight: 600;
}
</style>
