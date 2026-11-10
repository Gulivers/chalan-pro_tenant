import axios from 'axios';
import Swal from 'sweetalert2';
import { hasAuthSession } from '@/auth/tokenHelpers';

const ensureTrailingSlash = (url = '') => (url.endsWith('/') ? url : `${url}/`); // Asegura slash final.
const stripTrailingSlash = (url = '') => url.replace(/\/+$/, ''); // Quita slashes duplicados al final.
const stripLeadingSlash = (path = '') => path.replace(/^\/+/, ''); // Quita slashes iniciales.

export const appMixin = {
  methods: {
    getApiBaseUrl() {
      const base = window.__API_BASE_URL || axios.defaults.baseURL || '';
      return ensureTrailingSlash(base);
    },

    getWsBaseUrl() {
      const base = window.__WS_BASE_URL || this.getApiBaseUrl();
      return ensureTrailingSlash(base);
    },

    buildWsUrl(path = '') {
      const base = this.getWsBaseUrl();
      return `${stripTrailingSlash(base)}/${stripLeadingSlash(path)}`;
    },

    // ───────────────────────────────────────────────────────────────
    // AUTHENTICATION & USER DATA
    // ───────────────────────────────────────────────────────────────
    getAuthenticatedUser() {
      if (hasAuthSession()) {
        return axios
          .get('/api/auth/me/')
          .then(response => {
            return response.data;
          })
          .catch(error => {
            console.error('Error fetching user data:', error);
            return null;
          });
      } else {
        console.error('No auth session found');
        return null;
      }
    },

    hasPermission(permission) {
      const userPermissions = JSON.parse(localStorage.getItem('userPermissions'));
      return userPermissions && userPermissions.permissions.includes(permission);
    },

    // ───────────────────────────────────────────────────────────────
    // CONFIRMATIONS
    // ───────────────────────────────────────────────────────────────
    confirmDelete(title, text, callback = null) {
      const t = this.$t?.bind(this);
      Swal.fire({
        title: title || t?.('common.confirmDeleteTitle') || 'Are you sure?',
        text: text || t?.('common.confirmDeleteText') || 'This action cannot be undone.',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: t?.('common.confirmDeleteButton') || 'Yes, delete it!',
        cancelButtonText: t?.('common.cancel') || 'Cancel',
      }).then(result => {
        if (result.isConfirmed && typeof callback === 'function') {
          callback();
        }
      });
    },

    // ───────────────────────────────────────────────────────────────
    // NOTIFICATIONS
    // ───────────────────────────────────────────────────────────────
    notifySuccess(message) {
      const t = this.$t?.bind(this);
      Swal.fire(
        t?.('common.success') || 'Success!',
        message || t?.('common.operationSuccess') || 'Operation completed successfully.',
        'success'
      );
    },

    notifyError(message) {
      const t = this.$t?.bind(this);
      Swal.fire(
        t?.('common.error') || 'Error',
        message || t?.('common.somethingWrong') || 'Something went wrong.',
        'error'
      );
    },

    notifyWarning(message) {
      const t = this.$t?.bind(this);
      Swal.fire({
        icon: 'warning',
        title: t?.('common.warning') || 'Warning',
        text: message || t?.('common.warning') || 'Warning',
        confirmButtonText: t?.('common.gotIt') || 'Got it!',
      });
    },

    notifyFieldErrors(errors = {}) {
      const t = this.$t?.bind(this);
      const messages = Object.entries(errors)
        .map(([field, msgs]) => `<strong>${field}</strong>: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`)
        .join('<br>');

      Swal.fire({
        icon: 'error',
        title: t?.('common.validationError') || 'Validation Error',
        html: messages || t?.('common.validationErrorText') || 'There were errors in your form submission.',
        confirmButtonText: t?.('common.ok') || 'OK',
      });
    },

    notifyConfirm(title, text, confirmCallback, confirmButtonText, cancelButtonText) {
      const t = this.$t?.bind(this);
      import('sweetalert2').then(Swal => {
        Swal.default
          .fire({
            title: title,
            text: text,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#6c757d',
            confirmButtonText:
              confirmButtonText || t?.('common.yesConfirm') || 'Yes, confirm',
            cancelButtonText:
              cancelButtonText || t?.('common.cancel') || 'Cancel',
          })
          .then(result => {
            if (result.isConfirmed && typeof confirmCallback === 'function') {
              confirmCallback();
            }
          });
      });
    },

    // ───────────────────────────────────────────────────────────────
    //  toast NOTIFICATIONS
    // ───────────────────────────────────────────────────────────────
    notifyToastSuccess(message) {
      const t = this.$t?.bind(this);
      Swal.fire({
        toast: true,
        position: 'bottom-end',
        icon: 'success',
        title: message || t?.('common.operationSuccess') || 'Operation completed successfully.',
        showConfirmButton: false,
        timer: 3500,
        timerProgressBar: true,
      });
    },

    notifyToastError(message) {
      const t = this.$t?.bind(this);
      Swal.fire({
        toast: true,
        position: 'bottom-end',
        icon: 'error',
        title: message || t?.('common.somethingWrong') || 'Something went wrong.',
        showConfirmButton: false,
        timer: 4000,
        timerProgressBar: true,
      });
    },
    
    notifyToasWarning(message) {
      const t = this.$t?.bind(this);
      Swal.fire({
        toast: true,
        icon: 'warning',
        title: t?.('common.warning') || 'Warning',
        text: message || t?.('common.warning') || 'Warning',
        confirmButtonText: t?.('common.gotIt') || 'Got it!',
      });
    },
  },
};
