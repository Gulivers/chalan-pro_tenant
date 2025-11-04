<template>
  <div class="container py-4">
    <h3 class="mb-4 text-primary">Supervisor Community Assignments</h3>
    <div v-if="Object.keys(communities).length === 0" class="alert alert-info">No data available.</div>
    <div v-else>
      <div v-for="(communityList, supervisor) in communities" :key="supervisor" class="card mb-3 shadow-sm border-0">
        <div class="card-header bg-dark text-white">
          <strong>{{ supervisor }}</strong>
        </div>
        <div class="card-body">
          <ul class="list-group list-group-flush">
            <li v-for="(community, idx) in communityList" :key="idx" class="list-group-item">
              {{ community }}
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import axios from 'axios';
  import { defineComponent, ref, onMounted } from 'vue';

  export default defineComponent({
    name: 'SupervisorCommunitiesList',
    setup() {
      const communities = ref({});

      const fetchCommunities = async () => {
        try {
          const res = await axios.get('/api/supervisor-communities/');
          communities.value = res.data;
        } catch (err) {
          console.error('Failed to fetch supervisor communities:', err);
        }
      };

      onMounted(() => {
        fetchCommunities();
      });

      return {
        communities,
      };
    },
  });
</script>

<style scoped>
  .card-header {
    font-size: 1.2rem;
  }
  .list-group-item {
    font-size: 0.95rem;
    padding: 0.5rem 1rem;
  }
</style>
