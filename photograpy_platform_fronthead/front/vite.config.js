import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue' // 添加 Vue 插件
import path from 'path'

export default defineConfig({
  plugins: [vue()], // 启用 Vue 插件
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})