<template>
  <div
    v-if="showBanner"
    class="jr-setup-banner"
    role="status">
    <div class="jr-setup-banner__copy">
      <p class="jr-setup-banner__title">Setup still open</p>
      <p class="jr-setup-banner__text">
        Finish your company infrastructure or schedule your first job when you are ready.
      </p>
    </div>
    <div class="jr-setup-banner__actions">
      <JRButton type="button" variant="primary" size="sm" @click="onContinue">
        Continue setup
      </JRButton>
      <JRButton type="button" variant="ghost" size="sm" @click="onDismiss">
        Dismiss
      </JRButton>
    </div>
  </div>
</template>

<script>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { JRButton } from '@/ui';
import { useTenantSetup } from '@/composables/useTenantSetup';

export default {
  name: 'SetupReminderBanner',
  components: { JRButton },
  setup() {
    const router = useRouter();
    const setup = useTenantSetup();

    onMounted(() => {
      setup.load().catch(() => {});
    });

    async function onContinue() {
      try {
        await setup.reopen();
      } catch (_) {
        setup.openPanel();
      }
      if (router.currentRoute.value.name !== 'home') {
        router.push({ name: 'home' });
      }
    }

    async function onDismiss() {
      try {
        await setup.dismissBanner();
      } catch (_) {
        /* keep banner if PATCH fails */
      }
    }

    return {
      showBanner: setup.showBanner,
      onContinue,
      onDismiss,
    };
  },
};
</script>

<style scoped>
.jr-setup-banner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem 1rem;
  margin: 0 0 1rem;
  padding: 0.75rem 1rem;
  background: color-mix(in srgb, var(--color-jr-primary) 8%, var(--color-jr-surface));
  border: 1px solid var(--color-jr-border);
  border-radius: var(--radius-jr-panel, 0.75rem);
}

.jr-setup-banner__copy {
  min-width: 0;
  flex: 1 1 16rem;
}

.jr-setup-banner__title {
  margin: 0 0 0.2rem;
  font-size: 0.875rem;
  font-weight: 600;
  line-height: 1.3;
  color: var(--color-jr-text);
}

.jr-setup-banner__text {
  margin: 0;
  font-size: 0.8125rem;
  line-height: 1.4;
  color: var(--color-jr-muted);
  max-width: 62ch;
}

.jr-setup-banner__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
}
</style>
