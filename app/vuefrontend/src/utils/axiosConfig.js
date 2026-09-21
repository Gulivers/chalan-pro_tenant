// Interceptor de solicitudes de Axios para manejar la autenticación JWT
import axios from 'axios';
import Swal from 'sweetalert2';
import { useAuthStore } from '../stores/auth';
import authService from '../auth/authService';
import router from '../router';

let refreshPromise = null;

function isPublicPath() {
  if (typeof window === 'undefined') return false;
  const currentPath = window.location.pathname || '';
  const publicPaths = ['/onboarding', '/login', '/reset_password', '/reset-password-confirm'];
  if (publicPaths.some((path) => currentPath.startsWith(path))) return true;
  try {
    const currentRoute = router.currentRoute?.value;
    const publicRoutes = ['onboarding', 'login', 'reset_password', 'reset_password_confirm'];
    if (currentRoute && publicRoutes.includes(currentRoute.name)) return true;
  } catch (_) {
    /* ignore */
  }
  const urlLower = currentPath.toLowerCase();
  return urlLower.includes('onboarding') || urlLower.includes('login') || urlLower.includes('reset');
}

export function setupAxiosInterceptors() {
  axios.defaults.withCredentials = true;

  axios.interceptors.request.use(
    (config) => {
      const authStore = useAuthStore();
      const token = authStore.accessToken?.value;
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  const api_endpoints = [
    { route: '/api/contract/', method: 'PUT' },
    { route: '/api/contract/', method: 'POST' },
    { route: '/api/contract/', method: 'DELETE' },
    { route: '/api/contractdetails/', method: 'PUT' },
    { route: '/api/workprice/', method: 'PUT' },
    { route: '/api/workprice/', method: 'POST' },
    { route: '/api/workprice/', method: 'DELETE' },
  ];

  function shouldLogAction(url, method) {
    return api_endpoints.some(
      (endpoint) => url.includes(endpoint.route) && method.toUpperCase() === endpoint.method
    );
  }

  axios.interceptors.response.use(
    (response) => {
      const config = response.config;
      if (shouldLogAction(config.url, config.method)) {
        logUserAction(config, response.data);
      }
      return response;
    },
    async (error) => {
      const originalRequest = error?.config;
      const status = error?.response?.status;
      const data = error?.response?.data || {};
      const method = (originalRequest?.method || '').toUpperCase();
      const requestUrl = originalRequest?.url || '';

      const skipRefresh =
        requestUrl.includes('/api/auth/login/') ||
        requestUrl.includes('/api/auth/refresh/') ||
        requestUrl.includes('/api/auth/logout/') ||
        requestUrl.includes('/api/auth/password/');

      // 401 → try one silent refresh, then redirect
      if (status === 401 && originalRequest && !originalRequest._retry && !skipRefresh) {
        originalRequest._retry = true;

        const optionalEndpoints = [
          '/api/unread-chat-counts/',
          '/api/auth/me/',
          '/api/auth/tenant-context/',
          '/api/auth/validate/',
        ];
        const isOptionalEndpoint = optionalEndpoints.some((endpoint) =>
          requestUrl.includes(endpoint)
        );
        const isPublicRoute = isPublicPath();

        try {
          if (!refreshPromise) {
            refreshPromise = authService.refreshAccess().finally(() => {
              refreshPromise = null;
            });
          }
          const newAccess = await refreshPromise;
          originalRequest.headers.Authorization = `Bearer ${newAccess}`;
          return axios(originalRequest);
        } catch (_) {
          if (!isOptionalEndpoint && !isPublicRoute) {
            useAuthStore().clearSession();
            router.push('/login');
          }
          return Promise.reject(error);
        }
      }

      if (status === 403 && data.code === 'tenant_inactive') {
        if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/account-suspended')) {
          router.push(data.redirect || '/account-suspended');
        }
        return Promise.reject(error);
      }

      if (status === 402 && data.code === 'subscription_required') {
        const billingPath = data.redirect || '/billing';
        if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/billing')) {
          router.push(billingPath);
        }
        return Promise.reject(error);
      }

      if (
        method === 'DELETE' &&
        status === 409 &&
        (data.code === 'in_use' || /in use/i.test(data.detail || ''))
      ) {
        await Swal.fire(
          'Oops!',
          data.detail || 'This record is in use and cannot be deleted. Inactivate it instead.',
          'error'
        );
      }

      if (status === 404) {
        console.warn(`Resource not found (404): ${requestUrl}`);
        return Promise.reject(error);
      }

      return Promise.reject(error);
    }
  );
}

function logUserAction(config, data) {
  const authStore = useAuthStore();
  const token = authStore.accessToken?.value;
  if (!token) return;
  axios
    .post(
      '/api/log-action/',
      {
        action: config.method.toUpperCase(),
        model_name: extractModelName(config.url),
        object_id: data.id || null,
        details: `Action logged at ${config.url} with method ${config.method.toUpperCase()}`,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    )
    .catch(() => {});
}

function extractModelName(url) {
  if (url.includes('/api/contract/')) return 'Contract';
  if (url.includes('/api/contractdetails/')) return 'ContractDetails';
  if (url.includes('/api/workprice/')) return 'WorkPrice';
  if (url.includes('/api/events/')) return 'Event';
  return 'UnknownModel';
}
