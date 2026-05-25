<template>
  <div class="container py-4 billing-page">
    <div class="row justify-content-center">
      <div class="col-lg-10">
        <h1 class="h3 fw-bold mb-2">Billing</h1>
        <p class="text-muted mb-4">
          Keep your operations connected after your trial ends.
        </p>

        <div v-if="loading" class="text-center py-5">
          <div class="spinner-border text-primary" role="status" />
        </div>

        <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

        <template v-else>
          <div
            v-if="status.trial_active"
            class="alert alert-success d-flex align-items-center justify-content-between flex-wrap gap-2"
          >
            <span>
              <strong>Free trial:</strong>
              {{ status.trial_days_left }} day(s) remaining.
              Upgrade before your trial expires to avoid interruption.
            </span>
          </div>

          <div
            v-else-if="status.needs_payment"
            class="alert alert-warning"
          >
            <strong>Action required.</strong>
            Your trial has ended or payment needs attention.
            Choose a plan below to continue.
          </div>

          <div
            v-if="status.in_grace_period"
            class="alert alert-warning"
          >
            Payment failed. You have a short grace period to update your payment method.
          </div>

          <div class="card shadow-sm mb-4">
            <div class="card-body">
              <h5 class="card-title">Current status</h5>
              <p class="mb-1">
                <span class="text-muted">Subscription:</span>
                <strong>{{ status.subscription_status || 'None' }}</strong>
              </p>
              <p v-if="status.current_plan_slug" class="mb-1">
                <span class="text-muted">Plan:</span>
                <strong>{{ formatPlanName(status.current_plan_slug) }}</strong>
              </p>
              <p v-if="status.landing_selected_plan" class="mb-0 small text-muted">
                Selected at signup: {{ status.landing_selected_plan }}
              </p>
            </div>
          </div>

          <div class="mb-3 d-flex align-items-center gap-2 flex-wrap">
            <span class="text-muted small">Billing period:</span>
            <div class="btn-group" role="group">
              <button
                type="button"
                class="btn btn-sm"
                :class="interval === 'monthly' ? 'btn-primary' : 'btn-outline-primary'"
                @click="interval = 'monthly'"
              >
                Monthly
              </button>
              <button
                type="button"
                class="btn btn-sm"
                :class="interval === 'yearly' ? 'btn-primary' : 'btn-outline-primary'"
                @click="interval = 'yearly'"
              >
                Annual (save 15%)
              </button>
            </div>
          </div>

          <div class="row g-3 mb-4">
            <div
              v-for="plan in plans"
              :key="plan.slug"
              class="col-md-4"
            >
              <div
                class="card h-100 shadow-sm"
                :class="{ 'border-primary': plan.is_recommended }"
              >
                <div class="card-body d-flex flex-column">
                  <div v-if="plan.is_recommended" class="mb-2">
                    <span class="badge bg-primary">Recommended</span>
                  </div>
                  <h5 class="card-title">{{ plan.name }}</h5>
                  <p class="fs-4 fw-bold mb-1">
                    {{ formatPrice(plan) }}
                    <span class="fs-6 text-muted fw-normal">
                      / {{ interval === 'yearly' ? 'year' : 'month' }}
                    </span>
                  </p>
                  <p v-if="plan.max_crews" class="small text-muted">
                    Up to {{ plan.max_crews }} active crews
                  </p>
                  <p v-else class="small text-muted">Unlimited crews</p>
                  <button
                    type="button"
                    class="btn mt-auto"
                    :class="plan.is_recommended ? 'btn-primary' : 'btn-outline-primary'"
                    :disabled="checkoutLoading === plan.slug"
                    @click="startCheckout(plan.slug)"
                  >
                    <span v-if="checkoutLoading === plan.slug">Redirecting…</span>
                    <span v-else-if="plan.slug === suggestedSlug && plan.is_recommended">
                      Upgrade to {{ plan.name }}
                    </span>
                    <span v-else-if="plan.slug === 'starter'">Continue with Starter</span>
                    <span v-else>Choose {{ plan.name }}</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="card shadow-sm">
            <div class="card-body d-flex flex-wrap align-items-center justify-content-between gap-2">
              <div>
                <h5 class="mb-1">Manage billing</h5>
                <p class="text-muted small mb-0">
                  Update payment method, view invoices, or cancel in the Stripe customer portal.
                </p>
              </div>
              <button
                type="button"
                class="btn btn-outline-secondary"
                :disabled="portalLoading"
                @click="openPortal"
              >
                {{ portalLoading ? 'Opening…' : 'Manage Billing' }}
              </button>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  fetchBillingStatus,
  fetchBillingPlans,
  createCheckoutSession,
  createCustomerPortalSession,
} from '@/api/billing'

const loading = ref(true)
const error = ref('')
const status = ref({})
const plans = ref([])
const interval = ref('monthly')
const checkoutLoading = ref(null)
const portalLoading = ref(false)

const suggestedSlug = computed(
  () => status.value.suggested_plan_slug || 'professional'
)

function formatPlanName(slug) {
  if (!slug) return ''
  return slug.charAt(0).toUpperCase() + slug.slice(1)
}

function formatPrice(plan) {
  const raw =
    interval.value === 'yearly' ? plan.yearly_price : plan.monthly_price
  const n = Number(raw)
  if (Number.isNaN(n)) return raw
  return `$${n.toLocaleString('en-US')}`
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [st, pl] = await Promise.all([
      fetchBillingStatus(),
      fetchBillingPlans(),
    ])
    status.value = st
    plans.value = pl
  } catch (e) {
    error.value =
      e.response?.data?.detail || 'Could not load billing. Please try again.'
  } finally {
    loading.value = false
  }
}

async function startCheckout(planSlug) {
  checkoutLoading.value = planSlug
  try {
    const { checkout_url } = await createCheckoutSession(planSlug, interval.value)
    if (checkout_url) window.location.href = checkout_url
  } catch (e) {
    error.value =
      e.response?.data?.detail || 'Checkout could not be started.'
  } finally {
    checkoutLoading.value = null
  }
}

async function openPortal() {
  portalLoading.value = true
  try {
    const { portal_url } = await createCustomerPortalSession()
    if (portal_url) window.location.href = portal_url
  } catch (e) {
    error.value =
      e.response?.data?.detail || 'Could not open billing portal.'
  } finally {
    portalLoading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.billing-page .card.border-primary {
  box-shadow: 0 0 0 1px var(--bs-primary);
}
</style>
