import { fileURLToPath, URL } from 'node:url'
import path from 'node:path'

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

const rootDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), 'frontend')

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())

  const basePath = env.VITE_BASE_PATH || env.VITE_BASE_URL || '/'
  console.log(`[vite] base utilisé: ${basePath}`)

  return {
    root: rootDir,
    base: basePath,
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(rootDir, 'src'),
        '~': path.resolve(rootDir, 'src'),
      },
    },
    publicDir: path.resolve(rootDir, 'public'),
    build: {
      outDir: path.resolve(rootDir, '../dist'),
      emptyOutDir: true,
    },
    server: {
      host: true,
      port: 5173,
    },
  }
})