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
    port: 3000,
    allowedHosts: ['.192.168.0.248:3000'],
    proxy: {
      '/api': {
        target: 'http://192.168.0.248:3000',
        changeOrigin: true,
        secure: false,
        // pathRewrite: { '^/api': '' },
      },
    },
  },
});
