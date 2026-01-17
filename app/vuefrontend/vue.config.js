// script de alias de rutas
const path = require('path');
const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')

module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {
    plugins: [
      new webpack.DefinePlugin({
        __VUE_OPTIONS_API__: JSON.stringify(true),
        __VUE_PROD_DEVTOOLS__: JSON.stringify(false),
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: JSON.stringify(false),
      }),
    ],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src'),
        '@components': path.resolve(__dirname, 'src/components'),
        '@buttons': path.resolve(__dirname, 'src/components/buttons'),
        '@contracts': path.resolve(__dirname, 'src/components/contracts'),
        '@schedule': path.resolve(__dirname, 'src/components/schedule'),
        '@houses': path.resolve(__dirname, 'src/components/houses'),
        '@views': path.resolve(__dirname, 'src/views'),
        '@assets': path.resolve(__dirname, 'src/assets'),
        '@auth': path.resolve(__dirname, 'src/auth'),
        '@router': path.resolve(__dirname, 'src/router'),
        '@store': path.resolve(__dirname, 'src/store'),
        '@stores': path.resolve(__dirname, 'src/stores'),
        '@utils': path.resolve(__dirname, 'src/utils'),
        '@mixins': path.resolve(__dirname, 'src/mixins'),
        '@helpers': path.resolve(__dirname, 'src/helpers'),
        vue$: 'vue/dist/vue.esm-bundler.js', // mantenemos esto
      },
    },
  },
  devServer: {
    host: '0.0.0.0',
    port: 8080,
    // Permitir todos los hosts en desarrollo local (para multi-tenant)
    allowedHosts: 'all',
    // Deshabilitar validación estricta del Host header para desarrollo local
    client: {
      webSocketURL: 'auto://0.0.0.0:0/ws'
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        ws: true, // Habilitar WebSockets
        onProxyReq: (proxyReq, req, res) => {
          const host = req.headers.host;
          if (host) {
            const hostWithoutPort = host.split(':')[0];
            proxyReq.setHeader('Host', hostWithoutPort);
          }
        },
      },
      '/crews': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        onProxyReq: (proxyReq, req, res) => {
          const host = req.headers.host;
          if (host) {
            const hostWithoutPort = host.split(':')[0];
            proxyReq.setHeader('Host', hostWithoutPort);
          }
        },
      },
      '/admin': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        onProxyReq: (proxyReq, req, res) => {
          const host = req.headers.host;
          if (host) {
            const hostWithoutPort = host.split(':')[0];
            proxyReq.setHeader('Host', hostWithoutPort);
          }
        },
      },
      '/ws': {
        target: 'http://localhost:8000', // Usar http:// porque webpack-proxy maneja el upgrade a WebSocket automáticamente
        ws: true, // Habilitar WebSockets
        changeOrigin: true,
        secure: false,
        logLevel: 'debug', // Para debugging
        onProxyReq: (proxyReq, req, res) => {
          const host = req.headers.host;
          if (host) {
            const hostWithoutPort = host.split(':')[0];
            proxyReq.setHeader('Host', hostWithoutPort);
          }
        },
        onError: (err, req, res) => {
          console.error('Proxy WebSocket error:', err);
        },
      },
      '/static': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        onProxyReq: (proxyReq, req, res) => {
          const host = req.headers.host;
          if (host) {
            const hostWithoutPort = host.split(':')[0];
            proxyReq.setHeader('Host', hostWithoutPort);
          }
        },
      },
      '/media': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        onProxyReq: (proxyReq, req, res) => {
          const host = req.headers.host;
          if (host) {
            const hostWithoutPort = host.split(':')[0];
            proxyReq.setHeader('Host', hostWithoutPort);
          }
        },
      },
    },
  },
});
