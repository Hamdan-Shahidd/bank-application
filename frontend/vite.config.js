import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const API = 'http://localhost:8000'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    allowedHosts: ['.ngrok-free.dev', '.ngrok-free.app'],
    hmr: { protocol: 'wss', clientPort: 443 },
    proxy: {
      '^/(auth|me|history|signup|login|deposit|withdraw|transfer|assistant|market|weather|email|image|debug)(/|$)': {
        target: API,
        changeOrigin: true,
        bypass(req) {
          const isPageLoad =
            req.method === 'GET' &&
            (req.headers.accept || '').includes('text/html') &&
            !req.url.startsWith('/auth/')
          if (isPageLoad) return '/index.html'
        },
      },
    },
  },
})