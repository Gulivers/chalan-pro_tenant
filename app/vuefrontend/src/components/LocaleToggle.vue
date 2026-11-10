<template>
  <div
    class="jr-locale-toggle"
    role="group"
    :aria-label="t('lang.toggleLabel')">
    <button
      type="button"
      class="jr-locale-toggle__btn"
      :class="{ 'jr-locale-toggle__btn--active': locale === 'en' }"
      :aria-pressed="locale === 'en'"
      @click="onSelect('en')">
      {{ t('lang.en') }}
    </button>
    <button
      type="button"
      class="jr-locale-toggle__btn"
      :class="{ 'jr-locale-toggle__btn--active': locale === 'es' }"
      :aria-pressed="locale === 'es'"
      @click="onSelect('es')">
      {{ t('lang.es') }}
    </button>
  </div>
</template>

<script>
import { useLocale } from '@/composables/useLocale'

export default {
  name: 'LocaleToggle',
  props: {
    /** When false, only updates local i18n (e.g. guest). Default persists. */
    persist: {
      type: Boolean,
      default: true,
    },
  },
  setup(props) {
    const { locale, t, setLocale } = useLocale()

    async function onSelect(lang) {
      if (locale.value === lang) return
      await setLocale(lang, { persist: props.persist })
    }

    return { locale, t, onSelect }
  },
}
</script>

<style scoped>
.jr-locale-toggle {
  display: inline-flex;
  border: 1px solid var(--color-jr-border);
  background: var(--color-jr-surface);
}

.jr-locale-toggle__btn {
  border: 0;
  background: transparent;
  color: var(--color-jr-primary);
  font-size: 0.8125rem;
  font-weight: 600;
  line-height: 1.3;
  padding: 0.35rem 0.6rem;
  cursor: pointer;
  transition: background-color 0.15s ease, color 0.15s ease;
}

.jr-locale-toggle__btn:hover {
  background: var(--color-jr-surface-muted);
}

.jr-locale-toggle__btn:focus-visible {
  outline: 2px solid var(--color-jr-primary);
  outline-offset: 2px;
  z-index: 1;
}

.jr-locale-toggle__btn--active {
  background: var(--color-jr-primary);
  color: #ffffff;
}

.jr-locale-toggle__btn--active:hover {
  background: var(--color-jr-primary-hover);
}
</style>
