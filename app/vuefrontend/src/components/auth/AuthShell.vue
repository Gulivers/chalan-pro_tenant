<template>
  <div class="jr-pilot jr-auth">
    <div class="jr-auth__layout">
      <main class="jr-auth__panel">
        <header class="jr-auth__chrome">
          <router-link
            to="/login"
            class="jr-auth__brand"
            aria-label="JobRhythm">
            <img
              :src="brandLogoUrl"
              alt="JobRhythm"
              class="jr-auth__brand-logo"
              width="220"
              height="56" />
          </router-link>
          <div
            v-if="tenantName"
            class="jr-auth__tenant"
            :title="tenantName">
            <img
              v-if="tenantLogoUrl"
              :src="tenantLogoUrl"
              alt=""
              class="jr-auth__tenant-logo"
              width="28"
              height="28"
              @error="onTenantLogoError" />
            <span class="jr-auth__tenant-name">{{ tenantName }}</span>
          </div>
        </header>

        <header class="jr-auth__intro">
          <h1 class="jr-auth__title">{{ title }}</h1>
          <p v-if="lead" class="jr-auth__lead">{{ lead }}</p>
        </header>

        <div class="jr-auth__body">
          <slot />
        </div>

        <p class="jr-auth__legal">
          © 2026 JobRhythm. Protected under U.S. copyright. Developed by Oliver
          Hernandez.
        </p>
      </main>

      <aside class="jr-auth__visual" aria-hidden="true">
        <img
          :src="heroImageUrl"
          alt=""
          class="jr-auth__visual-img"
          width="960"
          height="1280" />
        <div class="jr-auth__visual-scrim">
          <p class="jr-auth__visual-quote">
            From crew schedules to collections—one system that connects
            operations and profit on every job.
          </p>
        </div>
      </aside>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import brandLogoUrl from '@/assets/img/jobrhythm-logo-onboarding.png';
import heroImageUrl from '@/assets/img/auth-hero.jpg';

defineProps({
  title: {
    type: String,
    required: true,
  },
  lead: {
    type: String,
    default: '',
  },
});

const tenantName = ref('');
const tenantLogoUrl = ref(null);

function onTenantLogoError() {
  tenantLogoUrl.value = null;
}

onMounted(async () => {
  try {
    const { data } = await axios.get('/api/auth/tenant-context/');
    tenantName.value = data?.tenant_name || '';
    tenantLogoUrl.value = data?.tenant_logo_url || null;
  } catch {
    tenantName.value = '';
    tenantLogoUrl.value = null;
  }
});
</script>

<style scoped>
.jr-auth {
  min-height: 100vh;
  min-height: 100dvh;
  background: var(--color-jr-surface, #fff);
  color: var(--color-jr-text, #111827);
  font-family: var(--font-jr-sans, Inter, system-ui, sans-serif);
  caret-color: var(--color-jr-primary, #2563eb);
}

.jr-auth ::selection {
  background: color-mix(
    in srgb,
    var(--color-jr-primary, #2563eb) 28%,
    transparent
  );
  color: var(--color-jr-text, #111827);
}

.jr-auth__layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  min-height: 100vh;
  min-height: 100dvh;
}

.jr-auth__panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 1.5rem 1.25rem 2rem;
  max-width: 28rem;
  width: 100%;
  margin: 0 auto;
  animation: jr-auth-enter 0.35s cubic-bezier(0.22, 1, 0.36, 1) both;
}

.jr-auth__chrome {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem 1rem;
  margin-bottom: 2rem;
}

.jr-auth__brand {
  display: inline-flex;
  line-height: 0;
  text-decoration: none;
}

.jr-auth__brand-logo {
  display: block;
  height: 3.25rem;
  width: auto;
  max-width: 14rem;
  object-fit: contain;
}

.jr-auth__tenant {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
  max-width: 100%;
  padding: 0.35rem 0.65rem;
  border: 1px solid var(--color-jr-border, #e5e7eb);
  background: var(--color-jr-surface-muted, #f9fafb);
}

.jr-auth__tenant-logo {
  width: 1.5rem;
  height: 1.5rem;
  object-fit: contain;
  flex-shrink: 0;
}

.jr-auth__tenant-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-jr-text, #111827);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.jr-auth__intro {
  margin-bottom: 1.5rem;
}

.jr-auth__title {
  margin: 0 0 0.5rem;
  font-size: 2rem;
  font-weight: 700;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: var(--color-jr-text, #111827);
}

.jr-auth__lead {
  margin: 0;
  font-size: 0.9375rem;
  line-height: 1.5;
  color: var(--color-jr-muted, #4b5563);
}

.jr-auth__body {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.jr-auth__legal {
  margin: 2rem 0 0;
  font-size: 0.75rem;
  line-height: 1.45;
  color: var(--color-jr-muted, #4b5563);
}

.jr-auth__visual {
  display: none;
}

@keyframes jr-auth-enter {
  from {
    opacity: 0;
    transform: translateY(0.35rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (min-width: 960px) {
  .jr-auth__layout {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  }

  .jr-auth__panel {
    max-width: 28.5rem;
    margin: 0;
    padding: 2.5rem 3rem;
    justify-self: center;
    width: 100%;
  }

  .jr-auth__brand-logo {
    height: 3.5rem;
    max-width: 15.5rem;
  }

  .jr-auth__visual {
    display: block;
    position: relative;
    min-height: 100vh;
    min-height: 100dvh;
    overflow: hidden;
    background: var(--color-jr-primary-950, #172554);
  }

  .jr-auth__visual-img {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center top;
  }

  .jr-auth__visual-scrim {
    position: absolute;
    inset: auto 0 0;
    padding: 2rem 2rem 2.25rem;
    background: linear-gradient(
      to top,
      color-mix(in srgb, #0f172a 78%, transparent) 0%,
      transparent 100%
    );
  }

  .jr-auth__visual-quote {
    margin: 0;
    max-width: 22rem;
    font-size: 0.95rem;
    font-weight: 600;
    line-height: 1.4;
    color: #fff;
    text-shadow: 0 1px 2px rgba(15, 23, 42, 0.35);
  }
}
</style>

<!-- Shared form chrome used by Login / PasswordReset / Confirm -->
<style>
.jr-auth .jr-auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.jr-auth .jr-auth-form__list {
  margin: 0;
  padding-left: 1.1rem;
}

.jr-auth .jr-auth-pw {
  position: relative;
}

.jr-auth .jr-auth-pw .jr-control,
.jr-auth .jr-auth-pw input {
  padding-right: 2.75rem;
}

.jr-auth .jr-auth-pw__toggle {
  position: absolute;
  top: 50%;
  right: 0.5rem;
  transform: translateY(-50%);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--color-jr-muted, #4b5563);
  cursor: pointer;
}

.jr-auth .jr-auth-pw__toggle:hover {
  color: var(--color-jr-primary, #2563eb);
}

.jr-auth .jr-auth-pw__toggle:focus-visible {
  outline: 2px solid var(--color-jr-primary, #2563eb);
  outline-offset: 2px;
}

.jr-auth .jr-auth-pw__icon {
  width: 1rem;
  height: 1rem;
}

.jr-auth .jr-auth-form__footer {
  margin: 0;
  text-align: center;
}

.jr-auth .jr-auth-form__link {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-jr-primary, #2563eb);
  text-decoration: none;
  cursor: pointer;
}

.jr-auth .jr-auth-form__link:hover {
  color: var(--color-jr-primary-hover, #1d4ed8);
  text-decoration: underline;
  text-underline-offset: 0.15em;
}

.jr-auth .jr-auth-form__link:focus-visible {
  outline: 2px solid var(--color-jr-primary, #2563eb);
  outline-offset: 2px;
}
</style>
