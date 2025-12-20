/**
 * Configuración de ESLint para el proyecto Vue 3
 * 
 * Este archivo configura las reglas de linting para el código JavaScript/Vue
 * del frontend. ESLint ayuda a mantener la calidad del código detectando
 * errores y aplicando convenciones de estilo.
 * 
 * Configuraciones principales:
 * - Extiende las reglas esenciales de Vue 3
 * - Permite el uso de v-model con argumentos (v-model:prop)
 * - Configura reglas para desarrollo vs producción
 */
module.exports = {
  root: true,
  env: {
    node: true
  },
  extends: [
    'plugin:vue/vue3-essential',
    'eslint:recommended'
  ],
  parserOptions: {
    ecmaVersion: 2020
  },
  rules: {
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'vue/no-v-model-argument': 'off' // Deshabilitar esta regla para permitir v-model con argumentos
  }
}
