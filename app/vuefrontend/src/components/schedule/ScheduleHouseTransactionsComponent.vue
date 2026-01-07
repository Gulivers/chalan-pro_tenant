<template>
  <div class="house-transactions-container">
    <div class="text-center py-5">
      <h5 class="text-muted mb-3">💰 Transactions</h5>
      <p class="text-muted">Transactions view will be implemented here.</p>
      <p class="small text-muted">This section will display all transactions related to this work account.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ScheduleHouseTransactionsComponent',
  props: {
    eventId: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      // TODO: Add transactions data
    };
  },
  async mounted() {
    // TODO: Load transactions data
  },
  methods: {
    // TODO: Add transaction methods
  },
};
</script>

<style scoped>
.house-transactions-container {
  padding: 1rem;
  min-height: 300px;
}
</style>

