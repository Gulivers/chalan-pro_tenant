// Este script define una tienda de autenticación utilizando la Composition API de Vue
import { ref, computed } from 'vue'

const token = ref(null)
const user = ref(null)

export function useAuthStore() {
  const isAuthenticated = computed(() => !!token.value)

  function setToken(newToken) {
    token.value = newToken
  }

  function setUser(newUser) {
    user.value = newUser
  }

  function logout() {
    token.value = null
    user.value = null
    // Aquí puedes agregar lógica adicional para el logout
  }

  return {
    token,
    user,
    isAuthenticated,
    setToken,
    setUser,
    logout
  }
}