import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  base: './',  // Use relative paths for PyQt6 compatibility
  build: {
    minify: false,  // Easier debugging in production
    sourcemap: true,
    outDir: 'dist'
  },
  server: {
    port: 5173,
    strictPort: false
  }
})
