<template>
  <JRPage>
    <JRPageHeader title="Supervisor Community Assignments">
      <template #actions>
        <JRButton
          type="button"
          variant="ghost"
          size="sm"
          :disabled="loading"
          @click="fetchCommunities">
          Refresh
        </JRButton>
      </template>
    </JRPageHeader>

    <p v-if="loading" class="jr-sc-status" role="status">
      Loading supervisor assignments…
    </p>

    <JREmptyState
      v-else-if="loadError"
      title="Could not load supervisor assignments."
      description="Check the connection and try again.">
      <JRButton
        type="button"
        variant="ghost"
        size="sm"
        @click="fetchCommunities">
        Refresh
      </JRButton>
    </JREmptyState>

    <JREmptyState
      v-else-if="supervisorGroups.length === 0"
      title="No supervisor assignments."
      description="Communities appear when a crew member is linked to a community." />

    <template v-else>
      <JRSection
        v-for="group in supervisorGroups"
        :key="group.name"
        :title="group.name">
        <template #actions>
          <JRBadge
            :value="communityCountLabel(group.communities.length)"
            severity="secondary" />
        </template>
        <ul class="jr-sc-list" :aria-label="`Communities for ${group.name}`">
          <li
            v-for="community in group.communities"
            :key="community"
            class="jr-sc-list__item">
            {{ community }}
          </li>
        </ul>
      </JRSection>
    </template>
  </JRPage>
</template>

<script>
  import axios from 'axios';
  import { computed, defineComponent, ref, onMounted } from 'vue';
  import { JRBadge, JRButton, JREmptyState, JRPage, JRPageHeader, JRSection } from '@/ui';

  export default defineComponent({
    name: 'SupervisorCommunitiesList',
    components: { JRBadge, JRButton, JREmptyState, JRPage, JRPageHeader, JRSection },
    setup() {
      const communities = ref({});
      const loading = ref(true);
      const loadError = ref(false);

      const supervisorGroups = computed(() =>
        Object.entries(communities.value || {}).map(([name, list]) => ({
          name,
          communities: Array.isArray(list) ? list : [],
        }))
      );

      const communityCountLabel = (count) =>
        count === 1 ? '1 community' : `${count} communities`;

      const fetchCommunities = async () => {
        loading.value = true;
        loadError.value = false;
        try {
          const res = await axios.get('/api/supervisor-communities/');
          const data = res.data;
          communities.value =
            data && typeof data === 'object' && !Array.isArray(data) ? data : {};
        } catch (err) {
          console.error('Failed to fetch supervisor communities:', err);
          communities.value = {};
          loadError.value = true;
        } finally {
          loading.value = false;
        }
      };

      onMounted(() => {
        fetchCommunities();
      });

      return {
        loading,
        loadError,
        supervisorGroups,
        communityCountLabel,
        fetchCommunities,
      };
    },
  });
</script>

<style scoped>
  .jr-sc-status {
    margin: 0;
    font-size: 0.8125rem;
    line-height: 1.4;
    color: var(--color-jr-muted);
  }

  .jr-sc-list {
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .jr-sc-list__item {
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--color-jr-border);
    font-size: 0.875rem;
    line-height: 1.4;
    color: var(--color-jr-text);
    overflow-wrap: anywhere;
  }

  .jr-sc-list__item:last-child {
    border-bottom: 0;
  }
</style>
