import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  build: {
    minify: 'terser', // Usar Terser para minificación
    terserOptions: {
      compress: {
        drop_console: true, // Elimina todos los console.*
        drop_debugger: true // Elimina todos los debugger
      }
    }
  }
});
