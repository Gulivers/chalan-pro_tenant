/**
 * Normalizes ?plan= from the marketing site into Tenant plan labels.
 * Accepts: starter, professional, enterprise, pro, common variants; exact Starter|Professional|Enterprise.
 */
export function normalizeLandingPlan(raw) {
  if (raw == null || raw === '') return null
  const s = String(raw).trim()
  if (!s) return null
  const lower = s.toLowerCase().replace(/\s+/g, '-')
  const map = {
    starter: 'Starter',
    'starter-plan': 'Starter',
    professional: 'Professional',
    'professional-plan': 'Professional',
    pro: 'Professional',
    enterprise: 'Enterprise',
    'enterprise-plan': 'Enterprise',
    empresa: 'Enterprise',
  }
  if (map[lower]) return map[lower]
  if (['Starter', 'Professional', 'Enterprise'].includes(s)) return s
  return null
}
