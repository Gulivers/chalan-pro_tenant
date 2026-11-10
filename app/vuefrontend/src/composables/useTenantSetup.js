import { computed, ref } from 'vue';
import { fetchTenantSetup, patchTenantSetup } from '@/services/tenantSetupApi';
import i18n from '@/i18n';

const state = ref(null);
const loading = ref(false);
const error = ref('');
const panelOpen = ref(false);
const welcomeModalOpen = ref(false);
let loadPromise = null;

const STEP_META = {
  inventory: {
    phase: 1,
    i18nKey: 'inventory',
    routeName: 'inventory-master-data-setup',
    critical: false,
  },
  crew_categories: {
    phase: 2,
    i18nKey: 'crew_categories',
    routeName: 'crew-category-form',
    critical: false,
  },
  crews: {
    phase: 2,
    i18nKey: 'crews',
    routeName: 'crew-form',
    critical: false,
  },
  party_types: {
    phase: 2,
    i18nKey: 'party_types',
    routeName: 'party-types-form',
    critical: false,
  },
  party_categories: {
    phase: 2,
    i18nKey: 'party_categories',
    routeName: 'party-categories-form',
    critical: false,
  },
  builder: {
    phase: 2,
    i18nKey: 'builder',
    routeName: 'builder-form',
    critical: true,
  },
  communities: {
    phase: 2,
    i18nKey: 'communities',
    routeName: 'job-form',
    critical: true,
  },
  house_models: {
    phase: 2,
    i18nKey: 'house_models',
    routeName: 'house-model-form',
    critical: false,
  },
  first_event: {
    phase: 3,
    i18nKey: 'first_event',
    routeName: 'schedule',
    critical: false,
  },
  pick_ticket: {
    phase: 3,
    i18nKey: 'pick_ticket',
    routeName: 'material-requests',
    critical: false,
  },
  work_prices: {
    phase: 3,
    i18nKey: 'work_prices',
    routeName: 'work-prices-form',
    critical: false,
  },
  first_contract: {
    phase: 3,
    i18nKey: 'first_contract',
    routeName: 'contract-form',
    critical: false,
  },
};

function stepCopy(i18nKey) {
  const t = i18n.global.t;
  const base = `setup.steps.${i18nKey}`;
  return {
    title: t(`${base}.title`),
    description: t(`${base}.description`),
    cta: t(`${base}.cta`),
  };
}

export function useTenantSetup() {
  const isOwner = computed(() => !!state.value?.is_tenant_owner);
  const setupCompleted = computed(() => !!state.value?.setup_completed);
  const criticalReady = computed(() => !!state.value?.critical_ready);
  const nextRecommended = computed(() => state.value?.next_recommended || null);
  const steps = computed(() => state.value?.steps || {});
  const counts = computed(() => state.value?.counts || {});
  const skippable = computed(
    () => new Set(state.value?.skippable_steps || [])
  );

  const showBanner = computed(() => {
    if (!state.value || !isOwner.value || setupCompleted.value) return false;
    if (state.value.banner_dismissed) return false;
    return true;
  });

  const showDashboardGuide = computed(() => {
    if (!state.value || !isOwner.value) return false;
    return !setupCompleted.value;
  });

  const shouldAutoOpenWelcome = computed(() => {
    if (!state.value || !isOwner.value || setupCompleted.value) return false;
    if (state.value.welcome_modal_dismissed) return false;
    return true;
  });

  const inventoryPending = computed(
    () => (steps.value.inventory || 'pending') === 'pending'
  );

  const stepList = computed(() => {
    // Depend on locale so labels re-resolve when language changes.
    void i18n.global.locale.value;
    const order = state.value?.step_order || Object.keys(STEP_META);
    return order.map((key) => {
      const meta = STEP_META[key];
      const status = steps.value[key] || 'pending';
      if (!meta) {
        return {
          key,
          status,
          phase: 2,
          title: key,
          description: '',
          routeName: 'home',
          cta: i18n.global.t('common.open'),
          critical: false,
          canSkip: skippable.value.has(key) && status === 'pending',
        };
      }
      const copy = stepCopy(meta.i18nKey);
      return {
        key,
        status,
        phase: meta.phase,
        routeName: meta.routeName,
        critical: meta.critical,
        ...copy,
        canSkip: skippable.value.has(key) && status === 'pending',
      };
    });
  });

  const phaseGroups = computed(() => {
    void i18n.global.locale.value;
    const t = i18n.global.t;
    const groups = [
      {
        phase: 1,
        title: t('setup.stepInventory'),
        blurb: t('setup.step1Message'),
        steps: [],
      },
      {
        phase: 2,
        title: t('setup.stepMasters'),
        blurb: t('setup.step2Message'),
        steps: [],
      },
      {
        phase: 3,
        title: t('setup.stepOperate'),
        blurb: t('setup.step3Message'),
        steps: [],
      },
    ];
    for (const step of stepList.value) {
      const group = groups.find((g) => g.phase === step.phase);
      if (group) group.steps.push(step);
    }
    return groups;
  });

  const pendingCritical = computed(() =>
    stepList.value.filter((s) => s.critical && s.status !== 'done')
  );

  async function load({ force = false } = {}) {
    if (loadPromise && !force) return loadPromise;
    loading.value = true;
    error.value = '';
    loadPromise = (async () => {
      try {
        state.value = await fetchTenantSetup();
        return state.value;
      } catch (err) {
        const status = err?.response?.status;
        if (status === 400 || status === 403 || status === 404) {
          state.value = null;
          return null;
        }
        error.value =
          err?.response?.data?.detail ||
          'Could not load company setup progress.';
        throw err;
      } finally {
        loading.value = false;
        loadPromise = null;
      }
    })();
    return loadPromise;
  }

  async function mutate(payload) {
    state.value = await patchTenantSetup(payload);
    return state.value;
  }

  async function skipStep(step) {
    return mutate({ action: 'skip', step });
  }

  async function completeStep(step) {
    return mutate({ action: 'complete', step });
  }

  async function dismissPanel() {
    panelOpen.value = false;
    return mutate({ action: 'dismiss_panel' });
  }

  async function dismissBanner() {
    return mutate({ action: 'dismiss_banner' });
  }

  async function dismissWelcome() {
    welcomeModalOpen.value = false;
    return mutate({ action: 'dismiss_welcome' });
  }

  async function reopen() {
    const data = await mutate({ action: 'reopen' });
    welcomeModalOpen.value = false;
    panelOpen.value = true;
    return data;
  }

  async function finish() {
    const data = await mutate({ action: 'finish' });
    panelOpen.value = false;
    welcomeModalOpen.value = false;
    return data;
  }

  function openPanel() {
    welcomeModalOpen.value = false;
    panelOpen.value = true;
  }

  function closePanelLocal() {
    panelOpen.value = false;
  }

  function openWelcome() {
    welcomeModalOpen.value = true;
  }

  function closeWelcomeLocal() {
    welcomeModalOpen.value = false;
  }

  return {
    state,
    loading,
    error,
    panelOpen,
    welcomeModalOpen,
    STEP_META,
    isOwner,
    setupCompleted,
    criticalReady,
    nextRecommended,
    steps,
    counts,
    showBanner,
    showDashboardGuide,
    shouldAutoOpenWelcome,
    inventoryPending,
    stepList,
    phaseGroups,
    pendingCritical,
    load,
    skipStep,
    completeStep,
    dismissPanel,
    dismissBanner,
    dismissWelcome,
    reopen,
    finish,
    openPanel,
    closePanelLocal,
    openWelcome,
    closeWelcomeLocal,
  };
}
