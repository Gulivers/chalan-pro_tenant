<template>
  <JRPage>
    <div class="mx-auto max-w-5xl">
      <JRPageHeader
        :title="$t('billing.title')"
        :description="$t('billing.description')" />

      <div v-if="loading" class="flex justify-center py-12" role="status">
        <ProgressSpinner
          style="width: 2.5rem; height: 2.5rem"
          strokeWidth="4"
          :aria-label="$t('billing.loading')" />
      </div>

      <Message v-else-if="error" severity="error" :closable="false">
        {{ error }}
      </Message>

      <template v-else>
        <Message
          v-if="status.trial_active"
          class="mb-4"
          severity="success"
          :closable="false">
          <strong>{{ $t("billing.trialLead") }}</strong>
          {{
            $t("billing.trialDays", { days: status.trial_days_left })
          }}
        </Message>

        <Message
          v-else-if="status.needs_payment"
          class="mb-4"
          severity="warn"
          :closable="false">
          <strong>{{ $t("billing.actionRequired") }}</strong>
          {{ $t("billing.actionRequiredText") }}
        </Message>

        <Message
          v-if="status.in_grace_period"
          class="mb-4"
          severity="warn"
          :closable="false">
          {{ $t("billing.gracePeriod") }}
        </Message>

        <JRSection :title="$t('billing.currentStatus')">
          <p class="mb-1">
            <span class="text-jr-muted">{{ $t("billing.subscription") }}</span>
            <strong>{{
              status.subscription_status || $t("billing.none")
            }}</strong>
          </p>
          <p v-if="status.current_plan_slug" class="mb-1">
            <span class="text-jr-muted">{{ $t("billing.plan") }}</span>
            <strong>{{ formatPlanName(status.current_plan_slug) }}</strong>
          </p>
          <p
            v-if="status.landing_selected_plan"
            class="mb-0 text-sm text-jr-muted">
            {{
              $t("billing.selectedAtSignup", {
                plan: status.landing_selected_plan,
              })
            }}
          </p>
        </JRSection>

        <div class="mb-4 flex flex-wrap items-center gap-2">
          <span class="text-sm text-jr-muted">{{
            $t("billing.billingPeriod")
          }}</span>
          <JRButton
            type="button"
            size="sm"
            :variant="interval === 'monthly' ? 'primary' : 'secondary'"
            @click="interval = 'monthly'">
            {{ $t("billing.monthly") }}
          </JRButton>
          <JRButton
            type="button"
            size="sm"
            :variant="interval === 'yearly' ? 'primary' : 'secondary'"
            @click="interval = 'yearly'">
            {{ $t("billing.annual") }}
          </JRButton>
        </div>

        <div class="mb-4 grid grid-cols-1 gap-3 md:grid-cols-3">
          <article
            v-for="plan in plans"
            :key="plan.slug"
            class="flex h-full flex-col rounded-jr-panel border bg-jr-surface p-4"
            :class="
              plan.is_recommended ? 'border-jr-primary' : 'border-jr-border'
            ">
            <div v-if="plan.is_recommended" class="mb-2">
              <JRBadge
                :value="$t('billing.recommended')"
                severity="info" />
            </div>
            <h2 class="mb-2 text-base font-semibold">{{ plan.name }}</h2>
            <p class="mb-1 text-2xl font-semibold">
              {{ formatPrice(plan) }}
              <span class="text-base font-normal text-jr-muted">
                /
                {{
                  interval === "yearly"
                    ? $t("billing.year")
                    : $t("billing.month")
                }}
              </span>
            </p>
            <p v-if="plan.max_crews" class="text-sm text-jr-muted">
              {{ $t("billing.upToCrews", { count: plan.max_crews }) }}
            </p>
            <p v-else class="text-sm text-jr-muted">
              {{ $t("billing.unlimitedCrews") }}
            </p>
            <JRButton
              type="button"
              class="mt-auto"
              :variant="plan.is_recommended ? 'primary' : 'secondary'"
              :disabled="checkoutLoading === plan.slug"
              @click="startCheckout(plan.slug)">
              <span v-if="checkoutLoading === plan.slug">{{
                $t("billing.redirecting")
              }}</span>
              <span
                v-else-if="
                  plan.slug === suggestedSlug && plan.is_recommended
                ">
                {{ $t("billing.upgradeTo", { name: plan.name }) }}
              </span>
              <span v-else-if="plan.slug === 'starter'">{{
                $t("billing.continueStarter")
              }}</span>
              <span v-else>{{
                $t("billing.choosePlan", { name: plan.name })
              }}</span>
            </JRButton>
          </article>
        </div>

        <JRSection :title="$t('billing.manageTitle')">
          <div class="flex flex-wrap items-center justify-between gap-3">
            <p class="mb-0 text-sm text-jr-muted">
              {{ $t("billing.manageText") }}
            </p>
            <JRButton
              type="button"
              variant="secondary"
              :disabled="portalLoading"
              @click="openPortal">
              {{
                portalLoading
                  ? $t("billing.opening")
                  : $t("billing.manageButton")
              }}
            </JRButton>
          </div>
        </JRSection>
      </template>
    </div>
  </JRPage>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import Message from "primevue/message";
import ProgressSpinner from "primevue/progressspinner";
import { JRPage, JRPageHeader, JRSection, JRButton, JRBadge } from "@/ui";
import {
  fetchBillingStatus,
  fetchBillingPlans,
  createCheckoutSession,
  createCustomerPortalSession,
} from "@/api/billing";

const { t } = useI18n();

const loading = ref(true);
const error = ref("");
const status = ref({});
const plans = ref([]);
const interval = ref("monthly");
const checkoutLoading = ref(null);
const portalLoading = ref(false);

const suggestedSlug = computed(
  () => status.value.suggested_plan_slug || "professional"
);

function formatPlanName(slug) {
  if (!slug) return "";
  return slug.charAt(0).toUpperCase() + slug.slice(1);
}

function formatPrice(plan) {
  const raw =
    interval.value === "yearly" ? plan.yearly_price : plan.monthly_price;
  const n = Number(raw);
  if (Number.isNaN(n)) return raw;
  return `$${n.toLocaleString("en-US")}`;
}

async function load() {
  loading.value = true;
  error.value = "";
  try {
    const [st, pl] = await Promise.all([
      fetchBillingStatus(),
      fetchBillingPlans(),
    ]);
    status.value = st;
    plans.value = pl;
  } catch (e) {
    error.value = e.response?.data?.detail || t("billing.loadError");
  } finally {
    loading.value = false;
  }
}

async function startCheckout(planSlug) {
  checkoutLoading.value = planSlug;
  try {
    const { checkout_url } = await createCheckoutSession(
      planSlug,
      interval.value
    );
    if (checkout_url) window.location.href = checkout_url;
  } catch (e) {
    error.value = e.response?.data?.detail || t("billing.checkoutError");
  } finally {
    checkoutLoading.value = null;
  }
}

async function openPortal() {
  portalLoading.value = true;
  try {
    const { portal_url } = await createCustomerPortalSession();
    if (portal_url) window.location.href = portal_url;
  } catch (e) {
    error.value = e.response?.data?.detail || t("billing.portalError");
  } finally {
    portalLoading.value = false;
  }
}

onMounted(load);
</script>
