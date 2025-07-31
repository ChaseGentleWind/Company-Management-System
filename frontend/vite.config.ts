// frontend/vite.config.ts

import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },

  // =========== 新增服务器配置 ===========
  server: {
    // 监听所有网络地址，这对于在Docker中暴露服务至关重要
    host: true,
    // 我们将开发服务器的端口固定为 8080
    port: 8080,
    // 确保热模块替换 (HMR) 是开启的
    hmr: true,
    // 这是解决热更新问题的核心：使用轮询方式来检测文件变动
    watch: {
      usePolling: true,
    },
  },
  // =========== 新增配置结束 ===========
})
