import { createApp } from "vue";
import App from "./App.vue";

// Router & Stores

// Plugins válidos para Vue 3
import router from "./router";
import { createPinia } from "pinia"; // OAHP
import store from "./store";

import "leaflet/dist/leaflet.css";

// JobRhythm Design System (Pilot). Tailwind utilities viven bajo .jr-pilot.
import "@/assets/css/jr-design-system.css";
import "@/assets/css/jr-shell-nav.css";
import "@/assets/css/jr-tooltip.css";
import PrimeVue from "primevue/config";
import { JobRhythmPreset } from "@/ui/jr-primevue-preset";

// Axios & helpers
import axios from "axios";
import { setupAxiosInterceptors } from "./utils/axiosConfig";

// Mixins globales
import { appMixin } from "@mixins/appMixin";

import authService from "./auth/authService";

// Directivas
import TooltipDirective from "@/directives/tooltip";

// ───────────────────────────────────────────────────────────────
// Helpers para URLs según el entorno actual
// ───────────────────────────────────────────────────────────────
const ensureTrailingSlash = (url = "") => (url.endsWith("/") ? url : `${url}/`); // Añade slash final si falta.
const stripTrailingSlash = (url = "") => url.replace(/\/+$/, ""); // Quita slashes repetidos al final.
const stripLeadingSlash = (path = "") => path.replace(/^\/+/, ""); // Quita slashes iniciales.

const isLocalLikeHost = (hostname) => {
  if (!hostname) return false;
  const localHosts = ["localhost", "127.0.0.1"];
  if (localHosts.includes(hostname)) return true;
  return (
    /^192\.168\./.test(hostname) ||
    /^10\./.test(hostname) ||
    /^172\.(1[6-9]|2\d|3[0-1])\./.test(hostname)
  );
};

const resolveApiBaseUrl = () => {
  const envUrl = (import.meta.env.VITE_API_BASE_URL || "").trim();
  if (envUrl.length > 0) {
    return ensureTrailingSlash(envUrl);
  }

  const { protocol, hostname, port } = window.location;
  const devPorts = new Set(["3000", "3001", "8080", "8081", "5173", "5174"]);
  const isDevPort = Boolean(port) && devPorts.has(port);

  // En desarrollo local con npm run serve, usar ruta relativa para que el proxy funcione
  if (isLocalLikeHost(hostname) || isDevPort) {
    return "/";
  }

  // Render (producción): detectar patrón "-frontend.onrender.com" y mapear a "-backend".
  const renderMatch = hostname.match(
    /^(?<prefix>.+)-frontend(\.onrender\.com)$/
  );
  if (renderMatch?.groups?.prefix) {
    const backendHost = `${renderMatch.groups.prefix}-backend.onrender.com`;
    return ensureTrailingSlash(`${protocol}//${backendHost}`);
  }

  // Producción genérica: mismo host (backend reverso o env configurado).
  return ensureTrailingSlash(`${protocol}//${hostname}`);
};

const resolveWsBaseUrl = (apiUrl) => {
  const envWs = (import.meta.env.VITE_WS_BASE_URL || "").trim();

  // Si hay una URL de WebSocket configurada explícitamente, usarla
  if (envWs.length > 0) {
    return ensureTrailingSlash(envWs);
  }

  // En producción multi-tenant, usar el hostname actual para mantener el dominio del tenant
  const { protocol, hostname, port } = window.location;
  const devPorts = new Set(["3000", "3001", "8080", "8081", "5173", "5174"]);
  const isDevPort = Boolean(port) && devPorts.has(port);

  // En desarrollo local con npm run serve, conectar directamente al backend
  // para WebSockets (el proxy de webpack tiene problemas con WebSockets)
  if (isLocalLikeHost(hostname) || isDevPort) {
    // Conectar directamente al backend en el puerto 8000
    // Usar el hostname actual para mantener el dominio del tenant
    // Esto permite que django-tenants identifique correctamente el tenant
    return ensureTrailingSlash(`ws://${hostname}:8000`);
  }

  // En producción, usar el hostname actual (mantiene el dominio del tenant)
  const wsProtocol = protocol === "https:" ? "wss:" : "ws:";
  if (port && !["80", "443"].includes(port)) {
    return ensureTrailingSlash(`${wsProtocol}//${hostname}:${port}`);
  }
  return ensureTrailingSlash(`${wsProtocol}//${hostname}`);
};

const joinUrl = (base, path = "") => {
  const cleanBase = stripTrailingSlash(base);
  const cleanPath = stripLeadingSlash(path);
  return `${cleanBase}/${cleanPath}`;
};

// Determinar URLs base y exponerlas globalmente
const API_BASE_URL = resolveApiBaseUrl();
const WS_BASE_URL = resolveWsBaseUrl(API_BASE_URL);
window.__API_BASE_URL = API_BASE_URL;
window.__WS_BASE_URL = WS_BASE_URL;
window.__BUILD_WS_URL = (path = "") => joinUrl(WS_BASE_URL, path); // Helper global simple.

// Permite que las cookies se envíen con cada solicitud
axios.defaults.withCredentials = true;
axios.defaults.baseURL = API_BASE_URL;
setupAxiosInterceptors();

// Crea la aplicación de Vue
const app = createApp(App);

// plugins válidos aquí:
app.use(router);
const pinia = createPinia();
app.use(pinia);
app.use(store);
app.use(TooltipDirective);
const primeUiLicense = (import.meta.env.VITE_PRIMEUI_LICENSE || "").trim();

app.use(PrimeVue, {
  ...(primeUiLicense ? { license: primeUiLicense } : {}),
  theme: {
    preset: JobRhythmPreset,
    options: {
      darkModeSelector: "none",
      cssLayer: { name: "primevue", order: "theme, base, primevue, components, utilities" },
    },
  },
});

// Usa los mixins globalmente en toda la app
app.mixin(appMixin);

// Monta la aplicación con router y store
app.mount("#app");
