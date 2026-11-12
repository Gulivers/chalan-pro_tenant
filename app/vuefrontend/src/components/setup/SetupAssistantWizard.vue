<template>
  <JRDialog
    :visible="panelOpen"
    :header="$t('setup.wizardHeader')"
    size="xl"
    :show-footer="false"
    @update:visible="onVisible">
    <div class="jr-setup-wizard jr-pilot">
      <header class="jr-setup-wizard__brand">
        <img
          v-if="tenantLogoUrl && !tenantLogoFailed"
          :src="tenantLogoUrl"
          :alt="tenantName || $t('setup.companyLogoAlt')"
          class="jr-setup-wizard__logo"
          @error="tenantLogoFailed = true" />
        <div class="jr-setup-wizard__brand-copy">
          <p class="jr-setup-wizard__brand-name">
            {{ tenantName || 'JobRhythm' }}
          </p>
          <p class="jr-setup-wizard__lead">
            {{ $t('setup.welcomeLead', { name: greetName }) }}
          </p>
        </div>
      </header>

      <p v-if="loading" class="jr-setup-wizard__status" role="status">
        {{ $t('setup.loading') }}
      </p>

      <Message
        v-else-if="error"
        severity="error"
        :closable="false"
        class="jr-setup-wizard__msg">
        {{ error }}
      </Message>

      <Message
        v-if="actionError"
        severity="error"
        :closable="false"
        class="jr-setup-wizard__msg">
        {{ actionError }}
      </Message>

      <Stepper
        v-else
        v-model:value="phase"
        class="jr-setup-wizard__stepper">
        <StepList>
          <Step value="1">{{ $t('setup.stepInventory') }}</Step>
          <Step value="2">{{ $t('setup.stepMasters') }}</Step>
          <Step value="3">{{ $t('setup.stepOperate') }}</Step>
        </StepList>

        <StepPanels>
          <StepPanel value="1">
            <div class="jr-setup-wizard__panel">
              <h3 class="jr-setup-wizard__step-title">
                {{ $t('setup.step1Title') }}
              </h3>
              <p class="jr-setup-wizard__step-message">
                {{ $t('setup.step1Message') }}
              </p>
              <p class="jr-setup-wizard__step-desc">
                {{ $t('setup.step1Desc') }}
              </p>

              <InventoryMasterDataSetupContent
                embedded
                compact
                @imported="onInventoryImported" />

              <div class="jr-setup-wizard__nav">
                <div class="jr-setup-wizard__nav-start">
                  <JRButton
                    v-if="inventoryPending"
                    type="button"
                    variant="ghost"
                    @click="onSkipInventory">
                    {{ $t('setup.configureLater') }}
                  </JRButton>
                </div>
                <JRButton
                  type="button"
                  variant="primary"
                  @click="onNextInventory">
                  {{ $t('common.next') }}
                </JRButton>
              </div>
              <p
                v-if="inventoryPending"
                class="jr-setup-wizard__hint">
                {{ $t('setup.inventoryOptionalHint') }}
              </p>
            </div>
          </StepPanel>

          <StepPanel value="2">
            <div class="jr-setup-wizard__panel">
              <h3 class="jr-setup-wizard__step-title">
                {{ $t('setup.step2Title') }}
              </h3>
              <p class="jr-setup-wizard__step-message">
                {{ $t('setup.step2Message') }}
              </p>
              <p class="jr-setup-wizard__step-desc">
                {{ $t('setup.step2Desc') }}
              </p>

              <Message
                v-if="pendingCritical.length"
                severity="warn"
                :closable="false"
                class="jr-setup-wizard__msg">
                {{ $t('setup.step2Warn') }}
              </Message>

              <ul class="jr-setup-wizard__list" role="list">
                <li
                  v-for="step in essentialSteps"
                  :key="step.key"
                  class="jr-setup-wizard__row">
                  <div class="jr-setup-wizard__row-main">
                    <div class="jr-setup-wizard__row-meta">
                      <JRBadge :severity="badgeSeverity(step)">
                        {{ badgeLabel(step) }}
                      </JRBadge>
                      <p class="jr-setup-wizard__row-title">{{ step.title }}</p>
                    </div>
                    <p class="jr-setup-wizard__row-desc">{{ step.description }}</p>
                  </div>
                  <div class="jr-setup-wizard__row-actions">
                    <JRButton
                      type="button"
                      :variant="step.status === 'pending' ? 'primary' : 'secondary'"
                      size="sm"
                      @click="goStep(step)">
                      {{ step.status === 'pending' ? step.cta : $t('common.review') }}
                    </JRButton>
                    <JRButton
                      v-if="step.canSkip"
                      type="button"
                      variant="ghost"
                      size="sm"
                      @click="onSkip(step.key)">
                      {{ $t('setup.configureLater') }}
                    </JRButton>
                  </div>
                </li>
              </ul>

              <div class="jr-setup-wizard__nav">
                <JRButton
                  type="button"
                  variant="secondary"
                  @click="goPhase('1')">
                  {{ $t('common.back') }}
                </JRButton>
                <JRButton
                  type="button"
                  variant="primary"
                  @click="goPhase('3')">
                  {{ $t('common.next') }}
                </JRButton>
              </div>
              <p v-if="!criticalReady" class="jr-setup-wizard__hint">
                {{ $t('setup.step2Hint') }}
              </p>
            </div>
          </StepPanel>

          <StepPanel value="3">
            <div class="jr-setup-wizard__panel">
              <h3 class="jr-setup-wizard__step-title">
                {{ $t('setup.step3Title') }}
              </h3>
              <p class="jr-setup-wizard__step-message">
                {{ $t('setup.step3Message') }}
              </p>
              <p class="jr-setup-wizard__step-desc">
                {{ $t('setup.step3Desc') }}
              </p>

              <ul class="jr-setup-wizard__list" role="list">
                <li
                  v-for="step in operateSteps"
                  :key="step.key"
                  class="jr-setup-wizard__row">
                  <div class="jr-setup-wizard__row-main">
                    <div class="jr-setup-wizard__row-meta">
                      <JRBadge :severity="badgeSeverity(step)">
                        {{ badgeLabel(step) }}
                      </JRBadge>
                      <p class="jr-setup-wizard__row-title">{{ step.title }}</p>
                    </div>
                    <p class="jr-setup-wizard__row-desc">{{ step.description }}</p>
                  </div>
                  <div class="jr-setup-wizard__row-actions">
                    <JRButton
                      type="button"
                      :variant="step.status === 'pending' ? 'primary' : 'secondary'"
                      size="sm"
                      @click="goStep(step)">
                      {{ step.status === 'pending' ? step.cta : $t('common.review') }}
                    </JRButton>
                    <JRButton
                      v-if="step.canSkip"
                      type="button"
                      variant="ghost"
                      size="sm"
                      @click="onSkip(step.key)">
                      {{ $t('setup.configureLater') }}
                    </JRButton>
                  </div>
                </li>
              </ul>

              <div class="jr-setup-wizard__nav">
                <JRButton
                  type="button"
                  variant="secondary"
                  @click="goPhase('2')">
                  {{ $t('common.back') }}
                </JRButton>
                <JRButton
                  type="button"
                  variant="primary"
                  :disabled="!criticalReady || finishing"
                  @click="onFinish">
                  {{ finishing ? $t('common.saving') : $t('setup.markComplete') }}
                </JRButton>
              </div>
              <p v-if="!criticalReady" class="jr-setup-wizard__hint">
                {{ $t('setup.step3Hint') }}
              </p>
            </div>
          </StepPanel>
        </StepPanels>
      </Stepper>
    </div>
  </JRDialog>
</template>

<script>
import { computed, onMounted, ref, watch } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import Message from 'primevue/message';
import Stepper from 'primevue/stepper';
import StepList from 'primevue/steplist';
import Step from 'primevue/step';
import StepPanels from 'primevue/steppanels';
import StepPanel from 'primevue/steppanel';
import { JRBadge, JRButton, JRDialog } from '@/ui';
import InventoryMasterDataSetupContent from '@/components/inventory/InventoryMasterDataSetupContent.vue';
import { useI18n } from 'vue-i18n';
import { useTenantSetup } from '@/composables/useTenantSetup';
import { useAuthStore } from '@/stores/auth';

const ESSENTIAL_KEYS = [
  'crew_categories',
  'crews',
  'party_types',
  'party_categories',
  'builder',
  'communities',
  'house_models',
];

const OPERATE_KEYS = [
  'first_event',
  'pick_ticket',
  'work_prices',
  'first_contract',
];

function displayFirstName(raw) {
  const value = String(raw || '').trim();
  if (!value) return '';
  const token = value.includes('@') ? value.split('@')[0] : value.split(/\s+/)[0];
  if (!token) return '';
  return token.charAt(0).toUpperCase() + token.slice(1);
}

export default {
  name: 'SetupAssistantWizard',
  components: {
    JRBadge,
    JRButton,
    JRDialog,
    Message,
    Stepper,
    StepList,
    Step,
    StepPanels,
    StepPanel,
    InventoryMasterDataSetupContent,
  },
  setup() {
    const router = useRouter();
    const { t } = useI18n({ useScope: 'global' });
    const setup = useTenantSetup();
    const auth = useAuthStore();
    const phase = ref('1');
    const finishing = ref(false);
    const actionError = ref('');
    const resolvedName = ref('');
    const tenantName = ref('');
    const tenantLogoUrl = ref('');
    const tenantLogoFailed = ref(false);

    const greetName = computed(() =>
      resolvedName.value ? `, ${resolvedName.value}` : ''
    );

    function goPhase(next) {
      phase.value = String(next);
    }

    const essentialSteps = computed(() =>
      setup.stepList.value.filter((s) => ESSENTIAL_KEYS.includes(s.key))
    );
    const operateSteps = computed(() =>
      setup.stepList.value.filter((s) => OPERATE_KEYS.includes(s.key))
    );

    function badgeSeverity(step) {
      if (step.status === 'done') return 'success';
      if (step.status === 'skipped') return 'secondary';
      if (step.critical) return 'warn';
      return 'info';
    }

    function badgeLabel(step) {
      if (step.status === 'done') return t('common.done');
      if (step.status === 'skipped') return t('common.later');
      if (step.critical) return t('common.required');
      return t('common.optional');
    }

    function syncPhase() {
      // Only suggest a starting phase when opening; never trap the user on step 1.
      if (setup.inventoryPending.value) {
        phase.value = '1';
        return;
      }
      if (!setup.criticalReady.value) {
        phase.value = '2';
        return;
      }
      const operatePending = operateSteps.value.some((s) => s.status === 'pending');
      phase.value = operatePending ? '3' : '2';
    }

    async function resolveTenantContext() {
      const fromStoreUser = auth.user?.value;
      if (fromStoreUser?.username) {
        resolvedName.value = displayFirstName(fromStoreUser.username);
      }
      if (fromStoreUser?.tenant_name) {
        tenantName.value = fromStoreUser.tenant_name;
      }
      if (fromStoreUser?.tenant_logo_url) {
        tenantLogoUrl.value = fromStoreUser.tenant_logo_url;
        tenantLogoFailed.value = false;
      }
      try {
        const { data } = await axios.get('/api/auth/me/');
        resolvedName.value =
          displayFirstName(data?.username || data?.email) || resolvedName.value;
        tenantName.value = data?.tenant_name || tenantName.value || '';
        tenantLogoUrl.value = data?.tenant_logo_url || tenantLogoUrl.value || '';
        tenantLogoFailed.value = false;
        if (data) auth.setUser?.(data);
      } catch (_) {
        /* keep store fallbacks */
      }
    }

    async function ensureLoaded() {
      try {
        await Promise.all([setup.load(), resolveTenantContext()]);
        syncPhase();
        if (setup.shouldAutoOpenWelcome.value) {
          setup.openPanel();
        }
      } catch (_) {
        /* silent */
      }
    }

    async function onInventoryImported() {
      actionError.value = '';
      await setup.load({ force: true });
      if (setup.steps.value.inventory !== 'done') {
        try {
          await setup.completeStep('inventory');
        } catch (_) {
          /* seed flag will auto-complete */
        }
      }
    }

    async function onSkipInventory() {
      actionError.value = '';
      try {
        await setup.skipStep('inventory');
      } catch (_) {
        /* still advance — inventory is optional in the wizard */
      }
      goPhase('2');
    }

    async function onNextInventory() {
      actionError.value = '';
      if (setup.inventoryPending.value) {
        try {
          await setup.skipStep('inventory');
        } catch (_) {
          /* still advance — inventory is optional in the wizard */
        }
      }
      goPhase('2');
    }

    async function onSkip(key) {
      actionError.value = '';
      try {
        await setup.skipStep(key);
      } catch (_) {
        /* ignore */
      }
    }

    function goStep(step) {
      if (step?.routeName) {
        setup.closePanelLocal();
        router.push({ name: step.routeName });
      }
    }

    async function onFinish() {
      finishing.value = true;
      actionError.value = '';
      try {
        await setup.finish();
      } catch (err) {
        actionError.value =
          err?.response?.data?.detail || t('setup.finishBlocked');
      } finally {
        finishing.value = false;
      }
    }

    async function onVisible(val) {
      if (val) {
        setup.openPanel();
        syncPhase();
        return;
      }
      try {
        await setup.dismissWelcome();
        await setup.dismissPanel();
      } catch (_) {
        setup.closePanelLocal();
        setup.closeWelcomeLocal();
      }
    }

    onMounted(ensureLoaded);

    watch(
      () => setup.panelOpen.value,
      (open) => {
        if (open) {
          setup.load({ force: true }).then(syncPhase).catch(() => {});
        }
      }
    );

    watch(
      () => router.currentRoute.value.fullPath,
      () => {
        if (setup.panelOpen.value) {
          setup.load({ force: true }).catch(() => {});
        }
      }
    );

    return {
      panelOpen: setup.panelOpen,
      loading: setup.loading,
      error: setup.error,
      inventoryPending: setup.inventoryPending,
      criticalReady: setup.criticalReady,
      pendingCritical: setup.pendingCritical,
      essentialSteps,
      operateSteps,
      phase,
      finishing,
      actionError,
      greetName,
      tenantName,
      tenantLogoUrl,
      tenantLogoFailed,
      badgeSeverity,
      badgeLabel,
      goPhase,
      onInventoryImported,
      onSkipInventory,
      onNextInventory,
      onSkip,
      goStep,
      onFinish,
      onVisible,
    };
  },
};
</script>

<style scoped>
.jr-setup-wizard {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.jr-setup-wizard__brand {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 0.75rem 1rem;
  width: 100%;
  padding-bottom: 1rem;
  margin-bottom: 0.15rem;
  border-bottom: 1px solid var(--color-jr-border);
}

.jr-setup-wizard__logo {
  width: 3.5rem;
  height: 3.5rem;
  object-fit: contain;
  flex: 0 0 auto;
  background: var(--color-jr-surface-muted);
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-control, 0);
}

.jr-setup-wizard__brand-copy {
  min-width: 0;
  flex: 1 1 18rem;
}

.jr-setup-wizard__brand-name {
  margin: 0 0 0.35rem;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-jr-text);
}

.jr-setup-wizard__lead {
  margin: 0;
  width: 100%;
  font-size: 0.875rem;
  line-height: 1.5;
  color: var(--color-jr-muted);
}

.jr-setup-wizard__status {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-jr-muted);
}

.jr-setup-wizard__msg {
  --p-message-border-radius: var(--radius-jr-control, 0);
}

.jr-setup-wizard__stepper {
  width: 100%;
}

/* One motion moment: active step marker pulses like document status Draft. */
.jr-setup-wizard__stepper :deep(.p-step[data-p-active='true'] .p-step-number) {
  background: var(--color-jr-primary);
  border-color: var(--color-jr-primary);
  color: var(--color-jr-surface, #ffffff);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-jr-primary) 18%, transparent);
  animation: jr-setup-step-pulse 1.35s ease-in-out infinite;
}

.jr-setup-wizard__stepper :deep(.p-step[data-p-active='true'] .p-step-title) {
  color: var(--color-jr-text);
  font-weight: 700;
}

@keyframes jr-setup-step-pulse {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--color-jr-primary) 22%, transparent);
  }
  50% {
    opacity: 0.4;
    transform: scale(0.92);
    box-shadow: 0 0 0 6px color-mix(in srgb, var(--color-jr-primary) 10%, transparent);
  }
}

@media (prefers-reduced-motion: reduce) {
  .jr-setup-wizard__stepper :deep(.p-step[data-p-active='true'] .p-step-number) {
    animation: none;
    opacity: 1;
    transform: none;
  }
}

.jr-setup-wizard__panel {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 1rem 1.25rem 0.15rem;
}

.jr-setup-wizard__step-title {
  margin: 0 0 0.1rem;
  font-size: 1.125rem;
  font-weight: 600;
  line-height: 1.25;
  color: var(--color-jr-text);
}

.jr-setup-wizard__step-message {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.4;
  color: var(--color-jr-text);
}

.jr-setup-wizard__step-desc {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.45;
  color: var(--color-jr-muted);
}

.jr-setup-wizard__list {
  list-style: none;
  margin: 0.15rem 0 0;
  padding: 0;
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel, 0.75rem);
  background: var(--color-jr-surface);
  overflow: hidden;
}

.jr-setup-wizard__row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem 1rem;
  padding: 0.85rem 1rem;
  border-bottom: 1px solid var(--color-jr-border);
}

.jr-setup-wizard__row:last-child {
  border-bottom: 0;
}

.jr-setup-wizard__row-main {
  min-width: 0;
  flex: 1 1 14rem;
}

.jr-setup-wizard__row-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.jr-setup-wizard__row-title {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  line-height: 1.35;
  color: var(--color-jr-text);
}

.jr-setup-wizard__row-desc {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.4;
  color: var(--color-jr-muted);
}

.jr-setup-wizard__row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}

.jr-setup-wizard__nav {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  margin-top: 0.35rem;
  padding-top: 0.85rem;
  border-top: 1px solid var(--color-jr-border);
}

.jr-setup-wizard__nav-start {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  min-height: 1px;
}

.jr-setup-wizard__hint {
  margin: 0;
  font-size: 0.75rem;
  line-height: 1.4;
  color: var(--color-jr-muted);
}

.jr-setup-wizard :deep(.p-steplist) {
  gap: 0.25rem;
}

.jr-setup-wizard :deep(.p-steppanel-content) {
  border-radius: var(--radius-jr-control, 0);
}

@media (max-width: 767.98px) {
  .jr-setup-wizard {
    gap: 1rem;
  }

  .jr-setup-wizard__panel {
    padding-left: 0.75rem;
    padding-right: 0.75rem;
  }

  .jr-setup-wizard__nav {
    flex-direction: column-reverse;
    align-items: stretch;
  }

  .jr-setup-wizard__nav-start {
    width: 100%;
  }

  .jr-setup-wizard__nav .jr-button {
    width: 100%;
  }
}
</style>
