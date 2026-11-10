import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import axios from 'axios'
import { usePrimeVue } from 'primevue/config'
import { useAuthStore } from '@/stores/auth'
import { DEFAULT_LOCALE, normalizeLocale } from '@/i18n'
import { applyPrimeVueLocale } from '@/i18n/primeLocale'

/**
 * Apply and persist UI language (vue-i18n + optional PATCH /api/auth/me/).
 */
export function useLocale() {
  const { locale, t } = useI18n({ useScope: 'global' })
  const auth = useAuthStore()
  let primevue = null
  try {
    primevue = usePrimeVue()
  } catch (_) {
    primevue = null
  }

  const currentLocale = computed(() => normalizeLocale(locale.value))

  function applyLocal(lang) {
    const next = normalizeLocale(lang)
    const prev = normalizeLocale(locale.value)
    if (prev !== next) {
      locale.value = next
      try {
        document.documentElement.lang = next
      } catch (_) {
        /* ignore */
      }
    }
    if (primevue?.config) {
      applyPrimeVueLocale(primevue, next)
    }
    return next
  }

  function syncFromUser(userOrLang) {
    const raw =
      typeof userOrLang === 'string'
        ? userOrLang
        : userOrLang?.preferred_language
    applyLocal(raw || DEFAULT_LOCALE)
  }

  async function setLocale(lang, { persist = true, toast } = {}) {
    const next = applyLocal(lang)
    if (!persist) return next

    try {
      const { data } = await axios.patch('/api/auth/me/', {
        preferred_language: next,
      })
      // Locale already applied locally — avoid a second reactive locale write.
      if (data) {
        auth.setUser?.(data, { syncLocale: false })
      }
      toast?.success?.(t('lang.saved'))
    } catch (_) {
      toast?.error?.(t('lang.saveFailed'))
    }
    return next
  }

  return {
    locale: currentLocale,
    t,
    applyLocal,
    syncFromUser,
    setLocale,
  }
}
