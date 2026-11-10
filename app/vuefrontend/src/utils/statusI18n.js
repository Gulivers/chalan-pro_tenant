import i18n from '@/i18n'

/**
 * Translate a status by code. Falls back to API name when no key exists.
 */
export function tStatus(code, fallbackName = '') {
  const key = String(code || '')
    .trim()
    .toLowerCase()
  if (!key) return fallbackName || ''
  const path = `status.${key}`
  const translated = i18n.global.t(path)
  if (translated && translated !== path) return translated
  return fallbackName || code
}

export function workAccountStateLabelI18n(state) {
  const key = String(state || '').toLowerCase()
  if (key === 'completed') return tStatus('completed')
  if (key === 'in_progress') return tStatus('in_progress')
  return tStatus('not_started')
}
