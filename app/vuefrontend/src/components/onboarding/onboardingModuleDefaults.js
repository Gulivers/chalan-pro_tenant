/**
 * Onboarding module slugs persisted on Tenant.preferences — aligned with app navbar (Jobrithm SPA).
 */
export const ONBOARDING_MODULE_IDS = [
  'operations',
  'inventory',
  'contracts_pricing',
  'entities',
  'crews_fleet',
  'communities',
]

export function defaultOnboardingPreferences() {
  return [...ONBOARDING_MODULE_IDS]
}

/**
 * If stored progress has legacy slug sets or incomplete lists, normalize to full current list.
 */
export function normalizeStoredPreferences(raw) {
  if (!Array.isArray(raw)) {
    return defaultOnboardingPreferences()
  }
  const valid = new Set(ONBOARDING_MODULE_IDS)
  const hasOnlyValidKeys = raw.length > 0 && raw.every((id) => valid.has(id))
  const complete = raw.length === ONBOARDING_MODULE_IDS.length && ONBOARDING_MODULE_IDS.every((id) => raw.includes(id))
  if (!hasOnlyValidKeys || !complete) {
    return defaultOnboardingPreferences()
  }
  return ONBOARDING_MODULE_IDS.filter((id) => raw.includes(id))
}
