import axios from 'axios'

export async function fetchBillingStatus() {
  const { data } = await axios.get('/api/billing/status/')
  return data
}

export async function fetchBillingPlans() {
  const { data } = await axios.get('/api/billing/plans/')
  return data.plans || []
}

export async function createCheckoutSession(planSlug, billingInterval = 'monthly') {
  const { data } = await axios.post('/api/billing/create-checkout-session/', {
    plan_slug: planSlug,
    billing_interval: billingInterval,
  })
  return data
}

export async function createCustomerPortalSession() {
  const { data } = await axios.post('/api/billing/create-customer-portal-session/')
  return data
}
