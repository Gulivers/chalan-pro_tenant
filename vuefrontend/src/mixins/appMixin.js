import axios from 'axios';
import Swal from 'sweetalert2';

export const appMixin = {
  methods: {
    // ───────────────────────────────────────────────────────────────
    // AUTHENTICATION & USER DATA
    // ───────────────────────────────────────────────────────────────
    getAuthenticatedUser() {
      const token = localStorage.getItem('authToken');
      if (token) {
        return axios
          .get('/api/user_detail/')
          .then(response => {
            return response.data;
          })
          .catch(error => {
            console.error('Error fetching user data:', error);
            return null;
          });
      } else {
        console.error('No auth token found');
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
    confirmDelete(title = 'Are you sure?', text = 'This action cannot be undone.', callback = null) {
      Swal.fire({
        title,
        text,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#3085d6',
        cancelButtonColor: '#d33',
        confirmButtonText: 'Yes, delete it!',
        cancelButtonText: 'Cancel',
      }).then(result => {
        if (result.isConfirmed && typeof callback === 'function') {
          callback();
        }
      });
    },

    // ───────────────────────────────────────────────────────────────
    // NOTIFICATIONS
    // ───────────────────────────────────────────────────────────────
    notifySuccess(message = 'Operation completed successfully.') {
      Swal.fire('Success!', message, 'success');
    },

    notifyError(message = 'Something went wrong.') {
      Swal.fire('Error', message, 'error');
    },

    notifyWarning(message = 'Warning') {
      Swal.fire({
        icon: 'warning',
        title: 'Warning',
        text: message,
        confirmButtonText: 'Got it!',
      });
    },

    notifyFieldErrors(errors = {}) {
      const messages = Object.entries(errors)
        .map(([field, msgs]) => `<strong>${field}</strong>: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`)
        .join('<br>');

      Swal.fire({
        icon: 'error',
        title: 'Validation Error',
        html: messages || 'There were errors in your form submission.',
        confirmButtonText: 'OK',
      });
    },

    notifyConfirm(title, text, confirmCallback, confirmButtonText = 'Yes, confirm', cancelButtonText = 'Cancel') {
      import('sweetalert2').then(Swal => {
        Swal.default
          .fire({
            title: title,
            text: text,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#6c757d',
            confirmButtonText: confirmButtonText,
            cancelButtonText: cancelButtonText,
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
    notifyToastSuccess(message = 'Operation completed successfully.') {
      Swal.fire({
        toast: true,
        position: 'bottom-end',
        icon: 'success',
        title: message,
        showConfirmButton: false,
        timer: 3500,
        timerProgressBar: true,
      });
    },

    notifyToastError(message = 'Something went wrong.') {
      Swal.fire({
        toast: true,
        position: 'bottom-end',
        icon: 'error',
        title: message,
        showConfirmButton: false,
        timer: 4000,
        timerProgressBar: true,
      });
    },
    
    notifyToasWarning(message = 'Warning') {
      Swal.fire({
        toast: true,
        icon: 'warning',
        title: 'Warning',
        text: message,
        confirmButtonText: 'Got it!',
      });
    },
  },
};
