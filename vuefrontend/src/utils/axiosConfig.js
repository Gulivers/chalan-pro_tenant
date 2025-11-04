// Interceptor de solicitudes de Axios para manejar la autenticación
import axios from 'axios';
import Swal from 'sweetalert2';
import { useAuthStore } from '../stores/auth';
import router from '../router';

export function setupAxiosInterceptors() {
  // Interceptor de solicitud
  axios.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('authToken');

      if (token) {
        config.headers['Authorization'] = `Token ${token}`;
      }
      return config;
    },
    (error) => Promise.reject(error)
  );

  const api_endpoints = [
    { 'route': '/api/contract/', 'method': 'PUT' },
    { 'route': '/api/contract/', 'method': 'POST' },
    { 'route': '/api/contract/', 'method': 'DELETE' },
    // { 'route': '/api/contract/', 'method': 'GET' },
    { 'route': '/api/contractdetails/', 'method': 'PUT' },
    { 'route': '/api/workprice/', 'method': 'PUT' },
    { 'route': '/api/workprice/', 'method': 'POST' },
    { 'route': '/api/workprice/', 'method': 'DELETE' },
    // { 'route': '/api/workprice/', 'method': 'GET' }
  ];

  // Función para verificar si la ruta y el método están en la lista
  function shouldLogAction(url, method) {
    return api_endpoints.some(endpoint => url.includes(endpoint.route) && method.toUpperCase() === endpoint.method);
  }

  // Interceptor de respuesta
  axios.interceptors.response.use(
    response => {

      const config = response.config;
      // console.log("config->", config);
      // Verificamos si la URL y el método están en la lista api_endpoints
      if (shouldLogAction(config.url, config.method)) {
        logUserAction(config, response.data);
      }

      return response;
    },
    async error => {
      const originalRequest = error?.config;
      const status = error?.response?.status;
      const data = error?.response?.data || {};
      const method = (originalRequest?.method || '').toUpperCase();

      // 401 → limpiar y redirigir a login
      if (status === 401 && !originalRequest?._retry) {
        originalRequest._retry = true;
        localStorage.removeItem('authToken');
        localStorage.removeItem('userPermissions');
        router.push('/login');
        return Promise.reject(error);
      }

      // 👇 NUEVO: Manejo global del PROTECT (DELETE → 409 Conflict)
      // Backend debe devolver: { detail: "...", code: "in_use" }
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

      // 👇 NUEVO: Manejo silencioso de errores 404 para referencias rotas
      // No mostrar errores al usuario para referencias que no existen
      if (status === 404) {
        const url = originalRequest?.url || '';
        // Solo logear en consola, no mostrar al usuario
        console.warn(`Resource not found (404): ${url}`);
        // No mostrar SweetAlert para errores 404
        return Promise.reject(error);
      }

      return Promise.reject(error);
    }
  );
}

// Función para registrar la acción del usuario
function logUserAction(config, data) {
  const token = localStorage.getItem('authToken');
  if (token) {
    axios.post('/api/log-action/', {
      action: config.method.toUpperCase(),
      model_name: extractModelName(config.url), // Extraemos el nombre del modelo
      object_id: data.id || null, // ID del objeto, si está disponible
      details: `Action logged at ${config.url} with method ${config.method.toUpperCase()}`
    }, {
      headers: {
        Authorization: `Token ${token}`,
        'Content-Type': 'application/json'
      }
    })
      .then(response => {
        console.log("Action logged:", response.data);
      })
      .catch(error => {
        console.error("Error logging the action:", error);
      });
  } else {
    console.error("Token not found. The user is not authenticated.");
  }
}

// Función para extraer el nombre del modelo de la URL
function extractModelName(url) {
  if (url.includes('/api/contract/')) return 'Contract';
  if (url.includes('/api/contractdetails/')) return 'ContractDetails';
  if (url.includes('/api/workprice/')) return 'WorkPrice';
  if (url.includes('/api/events/')) return 'Event';
  return 'UnknownModel'; // Modelo desconocido si no se encuentra
}