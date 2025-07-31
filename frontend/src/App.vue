<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from 'vue-router'
import { useAuthStore } from './stores/auth'
import { computed } from 'vue'
import {
  Layout as ALayout,
  LayoutHeader as ALayoutHeader,
  LayoutContent as ALayoutContent,
  Menu as AMenu,
  MenuItem as AMenuItem,
  Button as AButton,
} from 'ant-design-vue'

const authStore = useAuthStore()
const route = useRoute()

const allowedOrderRoles = ['SUPER_ADMIN', 'CUSTOMER_SERVICE', 'DEVELOPER', 'FINANCE']

// 计算当前激活的菜单项，用于高亮显示
const selectedKeys = computed(() => {
  if (route.path.startsWith('/orders')) return ['/orders']
  if (route.path.startsWith('/admin')) return ['/admin/user-management']
  return [route.path]
})
</script>

<template>
  <a-layout v-if="authStore.isAuthenticated" class="layout">
    <a-layout-header class="header">
      <div class="logo">
        <img alt="Vue logo" src="@/assets/logo.svg" />
        <span>管理系统</span>
      </div>
      <a-menu
        theme="dark"
        mode="horizontal"
        :selected-keys="selectedKeys"
        class="menu"
      >
        <a-menu-item key="/">
          <router-link to="/">首页</router-link>
        </a-menu-item>

        <a-menu-item
          key="/orders"
          v-if="allowedOrderRoles.includes(authStore.userRole)"
        >
          <router-link to="/orders">订单管理</router-link>
        </a-menu-item>

        <a-menu-item
          key="/admin/user-management"
          v-if="authStore.userRole === 'SUPER_ADMIN'"
        >
          <router-link to="/admin/user-management">用户管理</router-link>
        </a-menu-item>
      </a-menu>

      <div class="user-actions">
        <span>你好, {{ authStore.user?.full_name || authStore.user?.username }}</span>
        <a-button type="link" @click="authStore.logout()">登出</a-button>
      </div>
    </a-layout-header>

    <a-layout-content class="content">
      <RouterView />
    </a-layout-content>
  </a-layout>

  <RouterView v-else />
</template>

<style scoped>
.layout {
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  padding: 0 24px;
}

.logo {
  display: flex;
  align-items: center;
  color: white;
  margin-right: 40px;
}
.logo img {
  width: 32px;
  height: 32px;
  margin-right: 12px;
}
.logo span {
  font-size: 18px;
  font-weight: bold;
}

.menu {
  flex: 1;
  line-height: 64px; /* antd header 默认高度 */
}

.user-actions {
  display: flex;
  align-items: center;
  color: rgba(255, 255, 255, 0.85);
}
.user-actions span {
  margin-right: 16px;
}

.content {
  padding: 24px;
  background-color: #f0f2f5;
}
</style>
