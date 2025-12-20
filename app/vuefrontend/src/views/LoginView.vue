<template>
  <div class="container">
    <div class="row justify-content-center">

      <div class="col-xl-10 col-lg-12 col-md-9">

        <div class="card o-hidden border-0 shadow-lg my-5">
          <div class="card-body p-0">
            <!-- Nested Row within Card Body -->
            <div class="row">
              <div class="col-lg-6 d-none d-lg-block bg-login-image">
                <img src="@/assets/AI_ElectricalEstimator.png" alt="AI Electrical Estimator" class="img-fluid">
              </div>
              <div class="col-lg-6">
                <div class="p-5">
                  <div class="text-center">
                    <h1 class="h4 text-gray-900 mb-4">Welcome Back!</h1>
                  </div>
                  <form @submit.prevent="login" class="user">
                    <div class="form-group my-3">
                      <input v-model="username" type="text" class="form-control form-control-user"
                        placeholder="Enter Username">
                    </div>
                    <div class="form-group my-3">
                      <input v-model="password" type="password" class="form-control form-control-user"
                        placeholder="Password">
                    </div>
                    <button type="submit" class="btn btn-primary btn-user btn-block my-3" :disabled="isLoading">
                      <span v-if="isLoading" class="spinner-grow spinner-grow-sm" aria-hidden="true"></span>
                      <span v-if="isLoading"> Logging in...</span>
                      <span v-else>Login</span>
                    </button>
                  </form>
                  <div v-if="error" class="alert alert-danger mt-3">{{ error }}</div>
                  <hr>
                  <div class="text-center py-2">
                    <a class="small" @click.prevent="resetPassword">Forgot Password?</a>
                  </div>
                  <div class="alert alert-secondary text-center p-2" style="font-size: 11px; max-width: 320px; margin: 0 auto;">
                    <p class="mb-2 ">
                      This system and all of its functionalities, including but not limited to the Crew Scheduling interface, 
                      House Notes, and Real-Time Messaging, are protected under U.S. copyright law. Any unauthorized reproduction, 
                      distribution, or replication of any feature is strictly prohibited.
                    </p>
                    <p class="mb-0">
                      Developed by Oliver Hernandez. © 2025 All rights reserved.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>

    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
  setup() {
    const username = ref('')
    const password = ref('')
    const error = ref('')
    const isLoading = ref(false)
    const router = useRouter()

    const login = async () => {
      isLoading.value = true
      error.value = ''
      try {
        // Enviar credenciales al backend
        const response = await axios.post('/api/login/', {
          username: username.value,
          password: password.value
        })

        if (response.data && response.data.token) {
          // Almacenar el token de acceso en localStorage
          localStorage.setItem('authToken', response.data.token)
          //console.log('Access token stored:', localStorage.getItem('authToken'))

          // Configurar axios para usar el token en futuras solicitudes
          axios.defaults.headers.common['Authorization'] = `Token ${response.data.token}`

          // Obtener permisos del usuario
          const permissionsResponse = await axios.get('/api/user-permissions/')
          localStorage.setItem('userPermissions', JSON.stringify(permissionsResponse.data))

          // Redirigir al dashboard
          router.push('/');
        } else {
          throw new Error('Token not received in the response')
        }
      }  catch (err) {
        console.error('Login error:', err);
        if (err.response) {
          switch (err.response.status) {
            case 401:
              error.value = 'Incorrect credentials. Please try again.'; // Este mensaje es correcto
              break;
            case 403:
              error.value = 'Access denied. This may occur if your account does not have sufficient permissions.'; // Mensaje más claro
              break;
            case 500:
              error.value = 'Internal server error. Please try again later.'; // Mensaje para errores del servidor
              break;
            default:
              error.value = `Unknown error: ${err.response.status}. Please try again later.`; // Mensaje más informativo
          }
        } else if (err.request) {
          error.value = 'Could not connect to the server. Please check your internet connection.'; // Mensaje más específico
        } else {
          error.value = `An unexpected error occurred: ${err.message}. Please try again later.`; // Mensaje más informativo
        }
      } finally {
        isLoading.value = false
      }
    }

    const logout = () => {
      // Limpiar el token y los permisos de localStorage
      localStorage.removeItem('authToken')
      localStorage.removeItem('userPermissions')

      // Eliminar el token de las cabeceras de axios
      delete axios.defaults.headers.common['Authorization']

      // Redirigir al usuario a la página de inicio de sesión
      router.push('/login')
    }

    const resetPassword = () => {
      router.push('/reset_password'); 
    }
    
    return {
      username,
      password,
      error,
      isLoading,
      login,
      logout,
      resetPassword
    }
  }
}
</script>

<style scoped>
/* Puedes agregar estilos personalizados aquí */
</style>