import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// Docker: VITE_API_PROXY=http://fastapi-container:8000
// Host:   default http://127.0.0.1:8000
const apiTarget = process.env.VITE_API_PROXY || 'http://127.0.0.1:8000'
const wsTarget = apiTarget.replace(/^http/, 'ws')

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  server: {
    host: '0.0.0.0',
    port: 3000,
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        target: apiTarget,
        changeOrigin: true,
        // FastAPI routes are at /, nginx/Vite strip the /api prefix
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/ws': {
        target: wsTarget,
        ws: true,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ws/, ''),
      },
    },
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
