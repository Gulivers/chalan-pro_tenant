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

    <template v-else-if="workAccount">
      <header class="jr-wov__header jr-page-header">
        <div class="jr-wov__header-text">
          <p class="jr-wov__eyebrow">Work Account</p>
          <h1 class="jr-page-header__title">{{ workAccount.title }}</h1>
          <p v-if="workAccountSubtitle" class="jr-page-header__desc">
            {{ workAccountSubtitle }}
          </p>
        </div>
        <div class="jr-page-header__actions jr-wov__header-actions">
          <JRButton type="button" variant="ghost" size="sm" @click="goToList">
            Back to list
          </JRButton>
          <JRButton
            v-if="canEdit"
            type="button"
            size="sm"
            @click="goToEdit">
            Edit
          </JRButton>
        </div>
      </header>

      <WorkOrderViewerTabs
        :work-account-id="workAccountId"
        :event-id="scheduleEventId"
        :initial-tab="initialTab" />
    </template>
  </JRPage>
</template>

<script>
import { computed, getCurrentInstance, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import axios from "axios";
import WorkOrderViewerTabs from "@components/work-accounts/WorkOrderViewerTabs.vue";
import {
  resolveScheduleEventForWorkAccount,
  WORK_ORDER_VIEWER_TAB_IDS,
} from "@/utils/resolveScheduleEventForWorkAccount";
import {
  JRPage,
  JRPageHeader,
  JRButton,
  JREmptyState,
} from "@/ui";

export default {
  name: "WorkOrderViewerView",
  components: {
    JRPage,
    JRPageHeader,
    JRButton,
    JREmptyState,
    WorkOrderViewerTabs,
  },
  setup() {
    const route = useRoute();
    const router = useRouter();
    const { proxy } = getCurrentInstance();

    const workAccount = ref(null);
    const scheduleEventId = ref(null);
    const isLoading = ref(true);
    const loadError = ref("");

    const workAccountId = computed(() => {
      const raw = route.params.id;
      const parsed = Number(raw);
      return Number.isFinite(parsed) ? parsed : null;
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

    const canEdit = computed(() =>
      proxy?.hasPermission?.("apptransactions.change_workaccount")
    );

    const loadWorkAccount = async () => {
      if (!workAccountId.value) {
        loadError.value = "Invalid work account id.";
        workAccount.value = null;
        isLoading.value = false;
        return;
      }

      isLoading.value = true;
      loadError.value = "";

      try {
        const { data } = await axios.get(
          `/api/work-accounts/${workAccountId.value}/`
        );
        workAccount.value = data;
        scheduleEventId.value = await resolveScheduleEventForWorkAccount(
          workAccountId.value,
          data?.title || ""
        );
      } catch (err) {
        console.error("Failed to load work account viewer", err);
        workAccount.value = null;
        scheduleEventId.value = null;
        if (err?.response?.status === 404) {
          loadError.value = "The requested work account does not exist or you do not have access.";
        } else if (err?.response?.status === 403) {
          loadError.value = "You do not have permission to view this work account.";
        } else {
          loadError.value = "Could not load this work account. Please try again.";
        }
      } finally {
        isLoading.value = false;
      }
    };

    const goToList = () => {
      router.push({ name: "work-accounts" });
    };

    const goToEdit = () => {
      router.push({
        name: "work-accounts-form",
        query: { id: workAccountId.value },
      });
    };

    onMounted(loadWorkAccount);

    watch(workAccountId, () => {
      loadWorkAccount();
    });

    return {
      workAccount,
      workAccountId,
      scheduleEventId,
      isLoading,
      loadError,
      initialTab,
      workAccountSubtitle,
      canEdit,
      goToList,
      goToEdit,
    };
  },
};
</script>

<style scoped>
.jr-wov__loading {
  padding: 2rem 0;
  color: var(--color-jr-text-muted, #6b7280);
}

.jr-wov__header {
  margin-bottom: 1rem;
  padding: 1rem 1.25rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-panel, 0.75rem);
  background: var(--color-jr-surface, #fff);
}

.jr-wov__eyebrow {
  margin: 0 0 0.25rem;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-jr-text-muted, #6b7280);
}

.jr-wov__header-actions {
  flex-shrink: 0;
}

@media (max-width: 768px) {
  .jr-wov__header {
    align-items: stretch;
  }
}
</style>
