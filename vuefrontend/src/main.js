import {createApp} from 'vue';
import App from './App.vue';

// Router & Stores

// Plugins válidos para Vue 3
import router from './router';
import { createPinia } from 'pinia';  // OAHP
import store from './store';

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



// Permite que las cookies se envíen con cada solicitud
axios.defaults.withCredentials = true;
// La URL base de la API
// axios.defaults.baseURL = process.env.VUE_APP_API_BASE_URL || 'http://localhost:8000/';
axios.defaults.baseURL = process.env.VUE_APP_API_BASE_URL || 'https://chalan-pro.onrender.com';
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
