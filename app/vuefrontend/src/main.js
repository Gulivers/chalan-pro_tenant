import {createApp} from 'vue';
import App from './App.vue';

// Router & Stores

// Plugins válidos para Vue 3
import router from './router';
import { createPinia } from 'pinia';  // OAHP
import store from './store';

// jQuery y DataTables (deben estar antes de Bootstrap)
import $ from 'jquery';
import 'datatables.net'; // Solo JS, el CSS lo carga el CDN en index.html
// Hacer jQuery disponible globalmente
window.$ = window.jQuery = $;

// Bootstrap (no es plugin de Vue)
// Bootstrap CSS primero
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-vue-next/dist/bootstrap-vue-next.css'
import 'vue-select/dist/vue-select.css';
import 'leaflet/dist/leaflet.css';
import '@/assets/scss/custom-bootstrap.scss'; // custom scss npm install sass sass-loader --save-dev

// Bootstrap JS (bundle = incluye Popper). Importa SOLO uno
import 'bootstrap/dist/js/bootstrap.bundle.min.js'; // OAHP
// import 'bootstrap/dist/js/bootstrap.min.js';

// BootstrapVueNext (plugin de Vue)
import BootstrapVueNext from 'bootstrap-vue-next';

// Axios & helpers
import axios from 'axios';
import {setupAxiosInterceptors} from './utils/axiosConfig';

import { BTable, BPagination } from 'bootstrap-vue-next'
import { Modal } from 'bootstrap';

// Mixins globales
import {appMixin} from '@mixins/appMixin';
import {dataTableMixin} from '@mixins/dataTableMixin';

import authService from './auth/authService';

// Directivas
import TooltipDirective from '@/directives/tooltip'

// ───────────────────────────────────────────────────────────────
// Helpers para URLs según el entorno actual
// ───────────────────────────────────────────────────────────────
const ensureTrailingSlash = (url = '') => (url.endsWith('/') ? url : `${url}/`); // Añade slash final si falta.
const stripTrailingSlash = (url = '') => url.replace(/\/+$/, ''); // Quita slashes repetidos al final.
const stripLeadingSlash = (path = '') => path.replace(/^\/+/, ''); // Quita slashes iniciales.

const isLocalLikeHost = (hostname) => {
  if (!hostname) return false;
  const localHosts = ['localhost', '127.0.0.1'];
  if (localHosts.includes(hostname)) return true;
  return /^192\.168\./.test(hostname) || /^10\./.test(hostname) || /^172\.(1[6-9]|2\d|3[0-1])\./.test(hostname);
};

const resolveApiBaseUrl = () => {
  const envUrl = (process.env.VUE_APP_API_BASE_URL || '').trim();
  if (envUrl.length > 0) {
    return ensureTrailingSlash(envUrl);
  }

  const { protocol, hostname, port } = window.location;
  const devPorts = new Set(['3000', '3001', '8080', '8081', '5173', '5174']);
  const isDevPort = Boolean(port) && devPorts.has(port);
  if (isLocalLikeHost(hostname) || isDevPort) {
    const apiPort = '8000';
    return ensureTrailingSlash(`${protocol}//${hostname}:${apiPort}`);
  }

  // Render (producción): detectar patrón "-frontend.onrender.com" y mapear a "-backend".
  const renderMatch = hostname.match(/^(?<prefix>.+)-frontend(\.onrender\.com)$/);
  if (renderMatch?.groups?.prefix) {
    const backendHost = `${renderMatch.groups.prefix}-backend.onrender.com`;
    return ensureTrailingSlash(`${protocol}//${backendHost}`);
  }

  // Producción genérica: mismo host (backend reverso o env configurado).
  return ensureTrailingSlash(`${protocol}//${hostname}`);
};

const resolveWsBaseUrl = (apiUrl) => {
  const envWs = (process.env.VUE_APP_WS_BASE_URL || '').trim();
  
  // Si hay una URL de WebSocket configurada explícitamente, usarla
  if (envWs.length > 0) {
    return ensureTrailingSlash(envWs);
  }
  
  // En producción multi-tenant, usar el hostname actual para mantener el dominio del tenant
  const { protocol, hostname, port } = window.location;
  const devPorts = new Set(['3000', '3001', '8080', '8081', '5173', '5174']);
  const isDevPort = Boolean(port) && devPorts.has(port);
  
  // En desarrollo local, usar la URL de la API
  if (isLocalLikeHost(hostname) || isDevPort) {
    const base = apiUrl;
    if (base.startsWith('https://')) {
      return ensureTrailingSlash(`wss://${base.slice(8)}`);
    }
    if (base.startsWith('http://')) {
      return ensureTrailingSlash(`ws://${base.slice(7)}`);
    }
    return ensureTrailingSlash(base);
  }
  
  // En producción, usar el hostname actual (mantiene el dominio del tenant)
  const wsProtocol = protocol === 'https:' ? 'wss:' : 'ws:';
  if (port && !['80', '443'].includes(port)) {
    return ensureTrailingSlash(`${wsProtocol}//${hostname}:${port}`);
  }
  return ensureTrailingSlash(`${wsProtocol}//${hostname}`);
};

const joinUrl = (base, path = '') => {
  const cleanBase = stripTrailingSlash(base);
  const cleanPath = stripLeadingSlash(path);
  return `${cleanBase}/${cleanPath}`;
};

// Determinar URLs base y exponerlas globalmente
const API_BASE_URL = resolveApiBaseUrl();
const WS_BASE_URL = resolveWsBaseUrl(API_BASE_URL);
window.__API_BASE_URL = API_BASE_URL;
window.__WS_BASE_URL = WS_BASE_URL;
window.__BUILD_WS_URL = (path = '') => joinUrl(WS_BASE_URL, path); // Helper global simple.

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

app.component('BTable', BTable)
app.component('BPagination', BPagination)

// Usa los mixins globalmente en toda la app
app.mixin(appMixin);
app.mixin(dataTableMixin);

// Monta la aplicación con router y store
app.mount('#app')
