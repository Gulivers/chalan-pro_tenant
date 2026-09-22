<template>
  <!--
    NotFoundView — pantallas 404 de la SPA JobRhythm.

    Se usa como catch-all del Vue Router (`/:pathMatch(.*)*`, name: not-found)
    cuando la URL no coincide con ninguna ruta definida (p. ej. /foo).

    Sin navbar/footer (meta.hideNavbar / hideFooter). Muestra:
      - "404"
      - "Route is not found."
      - CTA: "Back to log in form" si no hay sesión JWT, o "Back to home" si sí.

    No sustituye el redirect a /login de las rutas protegidas sin auth;
    esas van al guard del router. Este componente es solo para paths desconocidos.
  -->
  <div class="jr-not-found">
    <div class="jr-not-found__card" role="alert">
      <p class="jr-not-found__code">404</p>
      <p class="jr-not-found__message">Route is not found.</p>
      <router-link
        :to="ctaTo"
        class="jr-not-found__link">
        {{ ctaLabel }}
      </router-link>
    </div>
  </div>
</template>

<script setup>
/**
 * Vista pública de ruta no encontrada (catch-all del router).
 * El CTA depende de si hay access JWT en memoria o flag/sesión de refresh.
 */
import { computed } from 'vue';
import { hasAuthSession, getAccessToken } from '@/auth/tokenHelpers';

const isSignedIn = computed(() => Boolean(getAccessToken() || hasAuthSession()));

const ctaTo = computed(() => (isSignedIn.value ? '/' : '/login'));
const ctaLabel = computed(() =>
  isSignedIn.value ? 'Back to home' : 'Back to log in form'
);
</script>

<style scoped>
.jr-not-found {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: var(--color-jr-page, #f3f4f6);
}

.jr-not-found__card {
  width: 100%;
  max-width: 22rem;
  padding: 2.5rem 1.75rem;
  text-align: center;
  background: var(--color-jr-surface, #fff);
  border: 1px solid var(--color-jr-border, #e5e7eb);
  border-radius: var(--radius-jr-panel, 0.75rem);
  box-shadow: var(--shadow-jr-overlay, 0 10px 30px rgba(17, 24, 39, 0.08));
}

.jr-not-found__code {
  margin: 0 0 0.75rem;
  font-size: 2rem;
  font-weight: 700;
  line-height: 1.1;
  color: var(--color-jr-primary-950, #172554);
}

.jr-not-found__message {
  margin: 0 0 1.5rem;
  font-size: 0.9375rem;
  font-weight: 500;
  line-height: 1.4;
  color: var(--color-jr-text, #111827);
}

.jr-not-found__link {
  font-size: 0.9375rem;
  font-weight: 600;
  color: var(--color-jr-primary, #2563eb);
  text-decoration: none;
}

.jr-not-found__link:hover {
  color: var(--color-jr-primary-hover, #1d4ed8);
  text-decoration: underline;
  text-underline-offset: 0.15em;
}

.jr-not-found__link:focus-visible {
  outline: 2px solid var(--color-jr-primary, #2563eb);
  outline-offset: 3px;
}
</style>
