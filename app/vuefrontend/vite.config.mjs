import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { VitePWA } from 'vite-plugin-pwa'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const rootDir = path.dirname(fileURLToPath(import.meta.url))

// Solo lo lee Node (vite.config). No usar prefijo VITE_: no debe ir al bundle.
const apiProxyTarget =
  process.env.VUE_APP_API_PROXY_TARGET || 'http://localhost:8000'

const srcAlias = (segment) => path.resolve(rootDir, 'src', segment)

function rewriteTenantHost(proxy) {
  const apply = (proxyReq, req) => {
    const host = req.headers?.host
    if (!host) return
    proxyReq.setHeader('Host', host.split(':')[0])
  }
  proxy.on('proxyReq', apply)
  proxy.on('proxyReqWs', apply)
}

function proxyToBackend({ ws = false } = {}) {
  return {
    target: apiProxyTarget,
    changeOrigin: true,
    secure: false,
    ws,
    configure: rewriteTenantHost,
  }
}

export default defineConfig({
  base: '/',
  plugins: [
    vue(),
    VitePWA({
      registerType: 'autoUpdate',
      strategies: 'generateSW',
      filename: 'service-worker.js',
      manifestFilename: 'manifest.json',
      injectRegister: 'auto',
      includeAssets: [
        'img/icons/favicon.ico',
        'img/icons/apple-touch-icon.png',
        'img/icons/favicon-96x96.png',
        'img/jobrhythm-logo.png',
      ],
      manifest: {
        name: 'JobRhythm',
        short_name: 'JobRhythm',
        theme_color: '#0d6efd',
        background_color: '#ffffff',
        display: 'standalone',
        start_url: '/',
        icons: [
          {
            src: './img/icons/apple-touch-icon.png',
            sizes: '180x180',
            type: 'image/png',
          },
          {
            src: './img/icons/favicon-96x96.png',
            sizes: '96x96',
            type: 'image/png',
          },
        ],
      },
      workbox: {
        skipWaiting: true,
        clientsClaim: true,
        navigateFallback: 'index.html',
        navigateFallbackDenylist: [
          /^\/api/,
          /^\/admin/,
          /^\/ws/,
          /^\/static/,
          /^\/media/,
        ],
      },
      devOptions: {
        enabled: false,
      },
    }),
  ],
  resolve: {
    alias: {
      '@': srcAlias(''),
      '@components': srcAlias('components'),
      '@buttons': srcAlias('components/buttons'),
      '@contracts': srcAlias('components/contracts'),
      '@schedule': srcAlias('components/schedule'),
      '@houses': srcAlias('components/houses'),
      '@crews': srcAlias('components/crews'),
      '@layout': srcAlias('components/layout'),
      '@transactions': srcAlias('components/transactions'),
      '@inventory': srcAlias('components/inventory'),
      '@types': srcAlias('types'),
      '@views': srcAlias('views'),
      '@assets': srcAlias('assets'),
      '@auth': srcAlias('auth'),
      '@router': srcAlias('router'),
      '@store': srcAlias('store'),
      '@stores': srcAlias('stores'),
      '@utils': srcAlias('utils'),
      '@mixins': srcAlias('mixins'),
      '@helpers': srcAlias('helpers'),
      '@ui': srcAlias('ui'),
    },
  },
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
  server: {
    host: '0.0.0.0',
    port: 8080,
    strictPort: true,
    allowedHosts: true,
    // El HMR no puede usar /ws: esa ruta es el proxy hacia Django.
    hmr: {
      path: '/vite-hmr',
    },
    proxy: {
      '/api': proxyToBackend({ ws: true }),
      // /crews no se proxea: son rutas del Vue Router.
      '/admin': proxyToBackend(),
      '/ws': proxyToBackend({ ws: true }),
      '/static': proxyToBackend(),
      '/media': proxyToBackend(),
    },
  },
})
