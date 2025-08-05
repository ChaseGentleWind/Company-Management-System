<script setup lang="ts">
import { RouterLink, RouterView, useRoute } from 'vue-router';
import { useAuthStore } from './stores/auth';
import { computed, ref, watch } from 'vue';
import {
  Layout as ALayout,
  LayoutHeader as ALayoutHeader,
  LayoutContent as ALayoutContent,
  Menu as AMenu,
  MenuItem as AMenuItem,
  Button as AButton,
  Badge as ABadge,
} from 'ant-design-vue';
import { BellOutlined } from '@ant-design/icons-vue';
import { useNotificationStore } from './stores/notifications';
import NotificationCenter from './components/NotificationCenter.vue';

const authStore = useAuthStore();
const notificationStore = useNotificationStore();
const route = useRoute();

const allowedOrderRoles = ['SUPER_ADMIN', 'CUSTOMER_SERVICE', 'DEVELOPER', 'FINANCE'];

// 唯一的、修正后的 selectedKeys 计算属性
const selectedKeys = computed(() => {
  if (route.path.startsWith('/orders')) return ['/orders'];
  if (route.path.startsWith('/admin')) return ['/admin/user-management'];
  if (route.path.startsWith('/finance')) return ['/finance/reports'];
  return [route.path];
});

// 控制通知抽屉的 ref
const drawerVisible = ref(false);

const showDrawer = () => {
  // 每次打开时都重新获取最新的通知
  notificationStore.fetchNotifications();
  drawerVisible.value = true;
};

// 监听登录状态，用户登录后主动获取一次通知
watch(
  () => authStore.isAuthenticated,
  (isAuth) => {
    if (isAuth) {
      notificationStore.fetchNotifications();
    }
  },
  { immediate: true } // immediate: true 确保组件加载时如果已登录也执行一次
);
</script>

<template>
  <a-layout v-if="authStore.isAuthenticated" class="layout">
    <a-layout-header class="header">
      <div class="logo">
        <img alt="Vue logo" src="@/assets/logo.svg" />
        <span>管理系统</span>
      </div>
      <a-menu theme="dark" mode="horizontal" :selected-keys="selectedKeys" class="menu">
        <a-menu-item key="/">
          <router-link to="/">首页</router-link>
        </a-menu-item>

        <a-menu-item key="/orders" v-if="allowedOrderRoles.includes(authStore.userRole)">
          <router-link to="/orders">订单管理</router-link>
        </a-menu-item>

        <a-menu-item key="/finance/reports" v-if="['FINANCE', 'SUPER_ADMIN'].includes(authStore.userRole)">
          <router-link to="/finance/reports">财务报表</router-link>
        </a-menu-item>

        <a-menu-item
          key="/admin/user-management"
          v-if="authStore.userRole === 'SUPER_ADMIN'"
        >
          <router-link to="/admin/user-management">用户管理</router-link>
        </a-menu-item>
      </a-menu>

      <div class="user-actions">
        <a-badge :count="notificationStore.unreadCount" class="notification-badge">
          <bell-outlined @click="showDrawer" style="font-size: 18px; cursor: pointer" />
        </a-badge>

        <span>你好, {{ authStore.user?.full_name || authStore.user?.username }}</span>
        <a-button type="link" @click="authStore.logout()">登出</a-button>
      </div>
    </a-layout-header>

    <a-layout-content class="content">
      <div style="background: #fff; padding: 24px; min-height: calc(100vh - 64px - 48px);">
          <RouterView />
      </div>
    </a-layout-content>
  </a-layout>

  <RouterView v-else />

  <notification-center :visible="drawerVisible" @close="drawerVisible = false" />
</template>

<style scoped>
.layout {
  min-height: 100vh;
}
.header {
  display: flex;
  align-items: center;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 10;
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
.notification-badge {
  margin-right: 24px;
}
.content {
  padding: 24px;
  background-color: #f0f2f5;
}
</style>
