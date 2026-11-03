import { computed, ref } from 'vue';
import { fetchTenantSetup, patchTenantSetup } from '@/services/tenantSetupApi';

const state = ref(null);
const loading = ref(false);
const error = ref('');
const panelOpen = ref(false);
const welcomeModalOpen = ref(false);
let loadPromise = null;

const STEP_META = {
  inventory: {
    phase: 1,
    title: 'Import Florida inventory masters',
    description:
      'Load products, brands, categories, units, warehouses, prices, absence reasons, and optional house-model favorites in one step.',
    routeName: 'inventory-master-data-setup',
    cta: 'Import Florida inventory masters',
    critical: false,
  },
  crew_categories: {
    phase: 2,
    title: 'Crew categories',
    description: 'Define categories such as Rough, Trim, Undergrounds, or Slabs for field crews.',
    routeName: 'crew-category-form',
    cta: 'Add crew category',
    critical: false,
  },
  crews: {
    phase: 2,
    title: 'Crews',
    description: 'Create the crews that will run work in the field.',
    routeName: 'crew-form',
    cta: 'Add crew',
    critical: false,
  },
  party_types: {
    phase: 2,
    title: 'Party types',
    description: 'Set profile types for builders, suppliers, and other companies you work with.',
    routeName: 'party-types-form',
    cta: 'Add party type',
    critical: false,
  },
  party_categories: {
    phase: 2,
    title: 'Party categories',
    description: 'Group parties into corporate categories used on documents and purchases.',
    routeName: 'party-categories-form',
    cta: 'Add party category',
    critical: false,
  },
  builder: {
    phase: 2,
    title: 'Builders',
    description: 'Register at least one builder before you can schedule residential work.',
    routeName: 'builder-form',
    cta: 'Add builder',
    critical: true,
  },
  communities: {
    phase: 2,
    title: 'Communities',
    description: 'Add at least one community (subdivision / job site) where crews will work.',
    routeName: 'job-form',
    cta: 'Add community',
    critical: true,
  },
  house_models: {
    phase: 2,
    title: 'House models',
    description: 'Register standard house models or electrical plan sets used on contracts.',
    routeName: 'house-model-form',
    cta: 'Add house model',
    critical: false,
  },
  first_event: {
    phase: 3,
    title: 'Schedule your first event',
    description: 'Put the first job on the calendar — learn by scheduling real work.',
    routeName: 'schedule',
    cta: 'Open schedule',
    critical: false,
  },
  pick_ticket: {
    phase: 3,
    title: 'Assign materials',
    description: 'After an event exists, create a Material Request (pick ticket) for the crew.',
    routeName: 'material-requests',
    cta: 'Open material requests',
    critical: false,
  },
  work_prices: {
    phase: 3,
    title: 'Piece-work prices',
    description: 'Set destajo / piece rates so contracts and crew pay line up.',
    routeName: 'work-prices-form',
    cta: 'Add work prices',
    critical: false,
  },
  first_contract: {
    phase: 3,
    title: 'Generate your first contract',
    description: 'Create a contract from scheduled work when pricing is ready.',
    routeName: 'contract-form',
    cta: 'Create contract',
    critical: false,
  },
};

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
    const order = state.value?.step_order || Object.keys(STEP_META);
    return order.map((key) => {
      const meta = STEP_META[key] || {
        phase: 2,
        title: key,
        description: '',
        routeName: 'home',
        cta: 'Open',
        critical: false,
      };
      const status = steps.value[key] || 'pending';
      return {
        key,
        status,
        ...meta,
        canSkip: skippable.value.has(key) && status === 'pending',
      };
    });
  });

  const phaseGroups = computed(() => {
    const groups = [
      {
        phase: 1,
        title: 'Inventory starters',
        blurb: 'Get materials ready with the Florida master template.',
        steps: [],
      },
      {
        phase: 2,
        title: 'Essential masters',
        blurb: 'Builders and communities are required before Schedule can run.',
        steps: [],
      },
      {
        phase: 3,
        title: 'Operate in the field',
        blurb: 'Schedule work, assign materials, set piece rates, then contract.',
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
