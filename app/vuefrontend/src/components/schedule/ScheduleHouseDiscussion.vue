<template>
    <div class="p-lg-3">
        <h4 class="text-center"> {{ event?.title || 'Unknown Title' }}
        </h4>
        <div v-if="event && event.id" class="row">
            <!-- House Notes Section -->
            <div class="col-lg-6 border-end px-2 px-lg-3">
                <ScheduleHouseNotesComponent :eventId="event.id" />
            </div>

            <!-- House Chat Section -->
            <div class="col-lg-6 px-2 px-lg-3">
                <ScheduleHouseChatComponent :eventId="event.id" />
            </div>
        </div>
        <div v-else class="text-center text-danger">
            <p>No event data available.</p>
        </div>
    </div>
</template>

<script>
import ScheduleHouseNotesComponent from "./ScheduleHouseNotesComponent.vue";
import ScheduleHouseChatComponent from "./ScheduleHouseChatComponent.vue";

export default {
    props: {
        event: Object, // Event object received from ScheduleEventModal
    },
    components: {
        ScheduleHouseNotesComponent,
        ScheduleHouseChatComponent,
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
.discussion-container {
    padding: 20px;
}

h4 {
    color: orange;
}
</style>
