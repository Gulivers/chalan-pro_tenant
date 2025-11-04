import axios from 'axios';
import router from '../router';
import { useAuthStore } from '../stores/auth';

const authService = {

  async handleLogout() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('userPermissions');
    const authStore = useAuthStore();
    authStore.logout();
    router.push('/login');
  }
};

export default authService;