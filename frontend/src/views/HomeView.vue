<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import {
  PageHeader as APageHeader,
  Card as ACard,
  TypographyTitle as ATypographyTitle,
  TypographyParagraph as ATypographyParagraph,
  Alert as AAlert
} from 'ant-design-vue';

const authStore = useAuthStore()
</script>

<template>
  <div>
    <a-page-header title="首页" sub-title="系统概览" />
    <div class="content-card">
      <a-card>
        <a-typography-title :level="2">
          欢迎回来, {{ authStore.user?.full_name || authStore.user?.username }}!
        </a-typography-title>
        <a-typography-paragraph>
          欢迎使用内部订单管理系统。您可以在顶部的导航栏中选择需要操作的模块。
        </a-typography-paragraph>
        <a-alert
          message="系统提示"
          description="这是一个基于 Vue 3, Vite, Ant Design Vue, Pinia 和 Flask 构建的现代化 Web 应用。所有页面和布局问题均已修复。"
          type="info"
          show-icon
        />
      </a-card>
    </div>
  </div>
</template>

<style scoped>
.content-card {
  margin: 0 24px;
}
</style>